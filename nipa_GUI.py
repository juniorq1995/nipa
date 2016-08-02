from os import listdir, environ as EV
from matplotlib import cm, pyplot as plt
from climdiv_data import *
from nipaV2 import *


#_these are the possible options for running the NIPA module
phases = ['allyears', 'elnino', 'lanina', 'neutpos', 'neutneg']
seasons = ['MAM', 'JJA', 'SON', 'DJF']
months = {'MAM':[3, 4, 5], 'JJA' : [6, 7, 8],
          'SON' : [9, 10, 11], 'DJF' :[12, 13, 14]}

#_these are the parameters that need to be set by the user
lag = 3
season = 'MAM'
phase = 'lanina'
div = 'New Mexico-06'
climdiv_startyr = 1921
n_yrs = 90




kwgroups = create_kwgroups(climdiv_months = months[season], sst_lag = lag,
                            mei_lag = lag, debug = True, climdiv_startyr = climdiv_startyr,
                            n_yrs = n_yrs   )

alldivDF, sst, mei, phaseind = get_data(kwgroups)

# posind = phaseind['elnino'] | phaseind['neutpos']
# negind = phaseind['neutneg'] | phaseind['lanina']


# if clim_data is imported, change this. if division is selected, use this.
clim_data = alldivDF[div]

#initilize nipa phase object
model = NIPAphase(clim_data, sst, mei, phaseind[phase])
#_run behind the scenes
model.gen_corr_grid()


fig, (ax1, ax2) = plt.subplots(2, 1)
#create SST map
fig, ax1, m = model.sstMap(fig = fig, ax = ax1)

#_run principle component regression, plot Results
model.pcr()
ax2.scatter(model.clim_data, model.pc1)
plt.show()




print 'Model hindcast correlation is %.2f' % model.correlation
