#%matplotlib inline
from matplotlib import cm, colors, rcParams
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap
from os import environ as EV
from pprint import pprint
import numpy as np
from utilityF import *
#from sList import *



#_set the path to the shapefile
fp = EV['SHPFILES'] + \
        '/CONUS_CLIMATE_DIVISIONS/GIS_OFFICIAL_CLIM_DIVISIONS'

#data is a pandas series that contains the division of each station paired with the mean precip
fig, ax, m = valueMap(data, fp)
ax.set_title('Average MAMJ precipitation by climate division');                