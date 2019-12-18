from matplotlib.pyplot import figure
import typing
import pandas
import numpy as np


def doplot(
    data: pandas.DataFrame, ind: np.ndarray, saltype: str, thres: float, ax
) -> typing.Tuple[float, float, float, float, float]:
    # %% for analysis, remove new trainees arbitrarily chosen making less than threshold
    sal = data['Salary'][ind]
    sal = sal[sal > thres]
    # %% plot
    if ax is not None:
        (sal / 1000).hist(ax=ax, bins=16)
        ax.set_xlim(0, 260)
        ax.set_title(f'{saltype}')

    return sal.max(), sal.median(), sal.quantile(0.9), sal.sum(), ind.sum()


def summaryplot(fg, ax, st: pandas.DataFrame, data: pandas.DataFrame, year: int):
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
        print(
            f'\nhighest earning MBTA staff ${maxsalary:.0f} in {year} was a {maxearner["Title"]},'
            f' including estimated ${maxearnerOT:.0f} overtime.\n'
        )
    except KeyError:
        print(f'\nhighest earning MBTA staff ${maxsalary:.0f} in {year} was a {maxearner["Title"]}')
    # %%
    fg = figure()
    ax = fg.gca()
    (st.ix[:-1, 'subtot'] / 1e8).sort_values().plot(kind='bar')
    ax.set_ylabel('expenditure [$10M]')
    ax.set_title('MBTA {} salary expenditure by category'.format(year))
    fg.subplots_adjust(bottom=0.15)
