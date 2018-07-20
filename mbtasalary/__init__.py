from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
try:
    from matplotlib.pyplot import figure
except ImportError:
    figure = None


def parsefilt(fn: Path, year: int, lowerthres: float=0.) -> Tuple[pd.DataFrame, pd.DataFrame]:

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

    if figure is not None:
        fg = figure(figsize=(25, 12))
        ax = fg.subplots(2, 5, sharex=True)
    else:
        ax = [[None]*5,
              [None]*5]
        ax = np.asarray(ax)
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
    for a in ax[:, 0]:
        a.set_ylabel('Number of occurrences')
    for a in ax[1, :]:
        a.set_xlabel(f'{year} Salary [$1000 USD]')

    fg.suptitle(f'{year} MBTA salary histograms', fontsize='xx-large')
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

    return st, data


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
    if ax is not None:
        (sal/1000).hist(ax=ax, bins=16)
        ax.set_xlim(0, 260)
        ax.set_title(f'{saltype}')

    return sal.max(), sal.median(), sal.quantile(.9), sal.sum(), ind.sum()
