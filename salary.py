#!/usr/bin/env python3
"""
Example of using 2014 MBTA salary data extracted from PDF with pandas for quick analysis

First you must download http://www.mbta.com/uploadedfiles/Smart_Forms/News,_Events_and_Press_Releases/Wages2014.pdf
to this directory and run
pdftotext -layout Wages2014.pdf

there are more efficient ways to index, but this is a rather small dataset.


tested with Python 3.5
Michael Hirsch
"""
from numpy import ones
from pandas import read_csv,DataFrame,option_context
from matplotlib.pyplot import subplots,close,figure


def main():
    close('all')
    fn = 'Wages2014.txt'
    lowerthres=0 # dollars, lower salary threshold
    #janky column spacing, require at least two spaces.
    #http://www.cheatography.com/davechild/cheat-sheets/regular-expressions/
    data = read_csv(fn,sep='\s{2,}',skiprows=2,engine='python',header=None, usecols=range(2,7),
            names=['DeptID','Descr','Title','2015Proj','2014Salary'])
#%% remove zero salaries
    data = data.loc[data['2014Salary']>0,:]

    st = DataFrame(columns=['max','median','90th','subtot','num'],dtype=float)
    fg,ax =  subplots(2,5,figsize=(25,12),sharex=True)
#%% easy example--police salary
    police = data['DeptID']==741 #by quick inspection of text file
    st.loc['police',:] = doplot(data,police,'police',lowerthres,ax[0,0])
#%% trickier example-- bus operator salary
    busops = data['Descr'].str.contains('Bus ') & data['Title'].str.contains('Operator')
    busops_ft = busops & ~data['Title'].str.contains('P-T')
    busops_pt = busops & data['Title'].str.contains('P-T')
    st.loc['bus-ft',:]=doplot(data,busops_ft,'full-time bus operators',lowerthres,ax[0,1])
    st.loc['bus-pt',:]=doplot(data,busops_pt,'part-time bus operators',100,ax[1,1])
#%% maintenance staff
    # we arbitrarily include Maintenance of Way, machinists, etc. in the same bucket
    maint = (data['Descr'].str.contains('MOW ')   |
             data['Descr'].str.contains('Maint')  |
             data['Descr'].str.contains('Repair') |
             data['Title'].str.contains('Technician'))
    st.loc['maint',:]=doplot(data,maint,'maintenance/repair',lowerthres,ax[0,2])
#%% Signaling staff
    signals = data['Descr'].str.contains('Signals')
    st.loc['signal',:]=doplot(data,signals,'signals',lowerthres,ax[1,0])
#%% subway operators, a.k.a. light rail
    subway = data['Descr'].str.contains('LRail')
    st.loc['subway',:]=doplot(data,subway,'subway operators',lowerthres,ax[1,2])
#%% commuter rail, a.k.a. heavy rail
    comm = data['Descr'].str.contains('HRail')
    st.loc['heavy',:] = doplot(data,comm,'commuter rail',lowerthres,ax[0,3])
#%% operations/training
    opstrn = data['Descr'].str.contains('OCC')
    st.loc['ops',:] = doplot(data,opstrn,'operations',lowerthres,ax[1,3])
#%% sort by median salary
    st.sort_values('median',ascending=False,inplace=True)
#%% everyone else e.g. general manager
    rest = ~(police | busops | maint | signals | subway | comm | opstrn)
    st.loc['rest',:] = doplot(data,rest,'the rest',lowerthres,ax[1,4])
#%% overall
    evry1= ones(data.shape[0],dtype=bool)
    st.loc['all',:] = doplot(data,evry1,'all',lowerthres,ax[0,4])
#%% finish up
    [a.set_ylabel('Number of occurrences') for a in ax[:,0]]
    [a.set_xlabel('2014 Salary [$USD]') for a in ax[1,:]]
    fg.tight_layout()

    maxearner = data.loc[data['2014Salary'].idxmax(),:]
    maxsalary = maxearner['2014Salary']
    maxearnerOT =  maxsalary - maxearner['2015Proj']
    print('\nhighest earning MBTA staff ${:.0f} in 2014 was a {}, including estimated ${:.0f} overtime.\n'.format(maxsalary,maxearner['Title'],maxearnerOT))
#%%
    ax=figure().gca()
    (st.ix[:-1,'subtot']/1e8).sort_values().plot(kind='bar')
    ax.set_ylabel('expenditure [$10M]')
    ax.set_title('MBTA salary expenditure by category')

    return st,data,{'maint':maint,'police':police,'signals':signals}


def doplot(data,ind,saltype,thres,ax):
#%% for analysis, remove new trainees arbitrarily chosen making less than threshold
    sal = data['2014Salary'][ind]
    sal = sal[sal>thres]
#%% plot
    sal.hist(ax=ax,bins=16)
    ax.set_xlim(0,250e3)
    ax.set_title('MBTA 2014 {} Salaries'.format(saltype))

    return sal.max(), sal.median(), sal.quantile(.9),sal.sum(),ind.sum()

if __name__ == '__main__':
    stats,data,sel = main()
    with option_context('precision',0):
        print(stats)