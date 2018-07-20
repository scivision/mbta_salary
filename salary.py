#!/usr/bin/env python
"""
Example of using 2014 MBTA salary data extracted from PDF with pandas for quick analysis

First you must download http://www.mbta.com/uploadedfiles/Smart_Forms/News,_Events_and_Press_Releases/Wages2014.pdf
to this directory and run
pdftotext -layout Wages2014.pdf

there are more efficient ways to index, but this is a rather small dataset.

examples: see README

Michael Hirsch
"""
from pathlib import Path
import numpy as np
from argparse import ArgumentParser
import pandas as pd
from typing import Tuple
from matplotlib.pyplot import subplots, figure
import seaborn as sns
sns.set_context('talk', font_scale=1.4)


def main():

    p = ArgumentParser(description="MBTA salary data plotter/parser")
    p.add_argument('fn', help='type filename to analyze e.g. wages2014.txt')
    p.add_argument('year', help='type year of data [2013 2014] so we can pick the right parser',
                   type=int, nargs='?', default=2014)
    p.add_argument('-l', '--lowerthreshold',
                   help='[dollars] lower salary threshold', type=float, default=0)
    p = p.parse_args()

    stats, data, sel = parsefilt(p.fn, p.year, p.lowerthreshold)

    with pd.option_context('precision', 0):
        print(stats)


def parsefilt(fn: Path, year: int, lowerthres: float) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:

    fn = Path(fn).expanduser()

    assert fn.suffix in ('.csv', '.txt', '.xls',
                         '.xlsx'), 'you must use a spreadsheet file or the PDF converted to text as per README.rst'

    # janky column spacing, require at least two spaces.
    # http://www.cheatography.com/davechild/cheat-sheets/regular-expressions/
    if year == 2015:  # NOTE this is a preliminary result using in-progess CY2015 data
        data = procxl(fn)
    elif year == 2014:
        data = pd.read_csv(fn, sep='\s{2,}', skiprows=2, engine='python', header=None, usecols=(2, 3, 4, 5, 6),
                           names=['DeptID', 'Descr', 'Title', 'ProjSal', 'Salary'])
    elif year == 2013:
        data = pd.read_csv(fn, sep='\s{2,}', skiprows=2, engine='python', header=None, usecols=(1, 2, 3, 4),
                           names=['DeptID', 'Descr', 'Title', 'Salary'])
    else:
        raise ValueError('year must be 2013 or 2014')
# %% remove zero salaries (thresholding is SEPARATE step)
    data = data.loc[data['Salary'] > 0, :]

    st = pd.DataFrame(columns=['max', 'median', '90th',
                               'subtot', 'num'], dtype=float)
    fg, ax = subplots(2, 5, figsize=(25, 12), sharex=True)
# %% easy case--police salary
    police = data['DeptID'] == 741  # by quick inspection of text file
    st.loc['police', :] = doplot(data, police, 'police', lowerthres, ax[0, 0])
# %% trickier example-- bus operator salary
    busops = data['Descr'].str.contains(
        'Bus ') & data['Title'].str.contains('Operator')
    busops_ft = busops & ~data['Title'].str.contains('P-T')
    busops_pt = busops & data['Title'].str.contains('P-T')
    st.loc['bus-ft', :] = doplot(data, busops_ft,
                                 'full-time bus operators', lowerthres, ax[0, 1])
    st.loc['bus-pt', :] = doplot(data, busops_pt,
                                 'part-time bus operators', 100, ax[1, 1])
# %% maintenance staff
    # we arbitrarily include Maintenance of Way, machinists, etc. in the same bucket
    maint = (data['Descr'].str.contains('MOW ') |
             data['Descr'].str.contains('Maint') |
             data['Descr'].str.contains('Repair') |
             data['Title'].str.contains('Technician'))
    st.loc['maint', :] = doplot(
        data, maint, 'maintenance/repair', lowerthres, ax[0, 2])
# %% Signaling staff
    signals = data['Descr'].str.contains('Signals')
    st.loc['signal', :] = doplot(
        data, signals, 'signals', lowerthres, ax[1, 0])
# %% subway operators, a.k.a. light rail
    subway = data['Descr'].str.contains('LRail')
    st.loc['subway', :] = doplot(
        data, subway, 'subway operators', lowerthres, ax[1, 2])
# %% commuter rail, a.k.a. heavy rail
    comm = data['Descr'].str.contains('HRail')
    st.loc['heavy', :] = doplot(
        data, comm, 'commuter rail', lowerthres, ax[0, 3])
# %% operations/training
    opstrn = data['Descr'].str.contains('OCC')
    st.loc['ops', :] = doplot(data, opstrn, 'operations', lowerthres, ax[1, 3])
# %% sort by median salary
    st.sort_values('median', ascending=False, inplace=True)
# %% everyone else e.g. general manager
    rest = ~(police | busops | maint | signals | subway | comm | opstrn)
    st.loc['rest', :] = doplot(data, rest, 'the rest', lowerthres, ax[1, 4])
# %% overall
    evry1 = np.ones(data.shape[0], dtype=bool)
    st.loc['all', :] = doplot(data, evry1, 'all', lowerthres, ax[0, 4])
# %% finish up
    [a.set_ylabel('Number of occurrences') for a in ax[:, 0]]
    [a.set_xlabel('{} Salary [$1000 USD]'.format(year)) for a in ax[1, :]]
    fg.suptitle('{} MBTA salary histograms'.format(year), fontsize='xx-large')
    fg.tight_layout()
    fg.subplots_adjust(top=0.93)

    maxearner = data.loc[data['Salary'].idxmax(), :]
    maxsalary = maxearner['Salary']
    try:
        maxearnerOT = maxsalary - maxearner['ProjSal']
        print(f'\nhighest earning MBTA staff ${maxsalary:.0f} in {year} was a {maxearner["Title"]},'
              f' including estimated ${maxearnerOT:.0f} overtime.\n')
    except KeyError:
        print(
            f'\nhighest earning MBTA staff ${maxsalary:.0f} in {year} was a {maxearner["Title"]}')
# %%
    fg = figure()
    ax = fg.gca()
    (st.ix[:-1, 'subtot']/1e8).sort_values().plot(kind='bar')
    ax.set_ylabel('expenditure [$10M]')
    ax.set_title('MBTA {} salary expenditure by category'.format(year))
    fg.subplots_adjust(bottom=0.15)

    return st, data, {'maint': maint, 'police': police, 'signals': signals}


def procxl(fn: Path) -> pd.DataFrame:
    """
    This function is for interim 2015 MBTA salary data--format may change in whole-year 2015 data.

    Note: at this time I don't include Backpay as by my current understanding,
    it is an increase in base salary that was backdated. It's for the previous year,
    but paid in the current year.

    Michael Hirsch
    """

    xldat = pd.read_excel(fn, sheetname=0, header=0, skip_footer=1,
                          parse_cols='B:E,G:H,J')
    data = pd.DataFrame(columns=['DeptID', 'Descr', 'Title', 'ProjSal', 'Salary'])

    data[['DeptID', 'Descr', 'Title', 'ProjSal']] = xldat[[
        'DeptID', 'Descr', 'Job Title', 'Annual Rate']]

    data['Salary'] = data['ProjSal'] + xldat['Overtime']

    return data


def doplot(data: pd.DataFrame, ind: np.ndarray,
           saltype: str, thres: float, ax) -> Tuple[float, float, float, float, float]:
    # %% for analysis, remove new trainees arbitrarily chosen making less than threshold
    sal = data['Salary'][ind]
    sal = sal[sal > thres]
# %% plot
    (sal/1000).hist(ax=ax, bins=16)
    ax.set_xlim(0, 260)
    ax.set_title(f'{saltype}', fontsize='xx-large')

    return sal.max(), sal.median(), sal.quantile(.9), sal.sum(), ind.sum()


if __name__ == '__main__':
    main()
