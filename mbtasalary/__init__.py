from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from matplotlib.pyplot import figure

from .plots import doplot, summaryplot


def parsefilt(fn: Path, year: int, lowerthres: float = 0.0) -> Tuple[pd.DataFrame, pd.DataFrame]:

    fn = Path(fn).expanduser()

    assert fn.suffix in (
        '.csv',
        '.txt',
        '.xls',
        '.xlsx',
    ), 'you must use a spreadsheet file or the PDF converted to text as per README.rst'

    # janky column spacing, require at least two spaces.
    # http://www.cheatography.com/davechild/cheat-sheets/regular-expressions/
    if year == 2015:  # NOTE this is a preliminary result using in-progess CY2015 data
        data = procxl(fn)
    elif year == 2014:
        data = pd.read_csv(
            fn,
            sep=r'\s{2,}',
            skiprows=2,
            engine='python',
            header=None,
            usecols=(2, 3, 4, 5, 6),
            names=['DeptID', 'Descr', 'Title', 'ProjSal', 'Salary'],
        )
    elif year == 2013:
        data = pd.read_csv(
            fn,
            sep=r'\s{2,}',
            skiprows=2,
            engine='python',
            header=None,
            usecols=(1, 2, 3, 4),
            names=['DeptID', 'Descr', 'Title', 'Salary'],
        )
    else:
        raise ValueError('year must be 2013 or 2014')
    # %% remove zero salaries (thresholding is SEPARATE step)
    data = data.loc[data['Salary'] > 0, :]

    st = pd.DataFrame(columns=['max', 'median', '90th', 'subtot', 'num'], dtype=float)

    fg = figure(figsize=(25, 12))
    ax = fg.subplots(2, 5, sharex=True)

    # %% easy case--police salary
    police = data['DeptID'] == 741  # by quick inspection of text file
    st.loc['police', :] = doplot(data, police, 'police', lowerthres, ax[0, 0])
    # %% trickier example-- bus operator salary
    busops = data['Descr'].str.contains('Bus ') & data['Title'].str.contains('Operator')
    busops_ft = busops & ~data['Title'].str.contains('P-T')
    busops_pt = busops & data['Title'].str.contains('P-T')
    st.loc['bus-ft', :] = doplot(data, busops_ft, 'full-time bus operators', lowerthres, ax[0, 1])
    st.loc['bus-pt', :] = doplot(data, busops_pt, 'part-time bus operators', 100, ax[1, 1])
    # %% maintenance staff
    # we arbitrarily include Maintenance of Way, machinists, etc. in the same bucket
    maint = (
        data['Descr'].str.contains('MOW ')
        | data['Descr'].str.contains('Maint')
        | data['Descr'].str.contains('Repair')
        | data['Title'].str.contains('Technician')
    )
    st.loc['maint', :] = doplot(data, maint, 'maintenance/repair', lowerthres, ax[0, 2])
    # %% Signaling staff
    signals = data['Descr'].str.contains('Signals')
    st.loc['signal', :] = doplot(data, signals, 'signals', lowerthres, ax[1, 0])
    # %% subway operators, a.k.a. light rail
    subway = data['Descr'].str.contains('LRail')
    st.loc['subway', :] = doplot(data, subway, 'subway operators', lowerthres, ax[1, 2])
    # %% commuter rail, a.k.a. heavy rail
    comm = data['Descr'].str.contains('HRail')
    st.loc['heavy', :] = doplot(data, comm, 'commuter rail', lowerthres, ax[0, 3])
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
    if ax[0, 0] is not None:
        summaryplot(fg, ax, st, data, year)

    return st, data


def procxl(fn: Path) -> pd.DataFrame:
    """
    This function is for interim 2015 MBTA salary data--format may change in whole-year 2015 data.

    Note: at this time I don't include Backpay as by my current understanding,
    it is an increase in base salary that was backdated. It's for the previous year,
    but paid in the current year.

    Michael Hirsch
    """

    xldat = pd.read_excel(fn, sheetname=0, header=0, skip_footer=1, parse_cols='B:E,G:H,J')
    data = pd.DataFrame(columns=['DeptID', 'Descr', 'Title', 'ProjSal', 'Salary'])

    data[['DeptID', 'Descr', 'Title', 'ProjSal']] = xldat[['DeptID', 'Descr', 'Job Title', 'Annual Rate']]

    data['Salary'] = data['ProjSal'] + xldat['Overtime']

    return data
