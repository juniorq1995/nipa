import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib import cm, colors, rcParams
import matplotlib.pyplot as plt
import matplotlib as mpl
from pprint import pprint
import os, math
from matplotlib import pyplot as plt
import time
from climdiv_data import *
from atmos_ocean_data import *
#Set up environment variable dictionary
EV = dict(os.environ)

#extracts all data for specific dates
def extract_ghcn_daily(fp = None, debug = False):

    assert fp is not None, 'Filepath is not valid'
    #Open the file for reading
    f = open(fp, 'r')

    #Make an empty list to load the filestrings into
    rawdata = []

    #read data
    for line in f.readlines():
        rawdata.append(line)
    f.close()

    startyr = rawdata[0][11:15]
    startmon = rawdata[0][15:17]
    endyr = rawdata[-1][11:15]
    endmon = rawdata[-1][15:17]

    index = pd.date_range(start = startyr + '-' + startmon, end = endyr + \
            '-' + endmon, freq = 'D') # create index
    years = index.year
    months = index.month
    df = pd.DataFrame(index = index)#empty dataframe with index based on startyr and endyr

    values_idx = []

    for n in np.arange(31):
        values_idx.append((21+(8*n), 26+(8*n)))#creates slicing parameters

    for line in rawdata:
        elem = line[17:21] # slice element
        yr = line[11:15] # slice year
        mon = line[15:17] # slice month
        date = yr + '-' + mon # save year and month
        idx = (years == int(yr)) & (months == int(mon)) # saves values when year in data is equal to year in prebuilt index as well as month and days
        ndays = idx.sum() # 365 or 366 days
        data = np.zeros(ndays) # create an array of size = ndays

        for i, lims in enumerate(values_idx): # indexes values_idx
            data[i] = line[lims[0]:lims[1]] # create new list

            if data[i] == -9999: # replace -9999 with nan
                data[i] = np.nan

            if i + 1 == ndays:
                break            # stop code if i is greater than 365/366 days depending on year

        df.loc[date,elem] = data #inserts data into elem for these dates

    return df


#selects stations with req. lat/long
def extract_stations(var, years, lat, lon, HCN = True):
    #reads a file
    station_list = []
    fp = EV['GHCN'] + '/ghcnd-inventory.txt'
    assert fp is not None, 'Filepath is not valid'
    f = open(fp,'r')
    rawdata = []

    #checks each line in file against paramters
    for line in f.readlines():
        rawdata.append(line)
    f.close

    for line in rawdata:
        #check latitude
        if(lat[1]>=float(line[12:20]) >= lat[0]):
            #check longitude
            if(lon[1]>=float(line[21:30]) >= lon[0]):
                #check that it is desired variable
                if (line[31:35] == var):
                    #take only years that user has selected
                    if (int(line[36:40])<=years[0] and int(line[41:45])>=years[1]):
                        #check for hcn flag
                        #if everything checks out the id of the station is added to a list
                        if HCN:
                            if(hcn_stations(line[0:11])):
                                station_list.append(line[0:11])
                        else:
                            station_list.append(line[0:11])
    #the master dictionary is created
    info = {}
    #each station that matches will be placed in its own sub-dictionary which lies inside the master, info
    for i,lines in enumerate (station_list):
        info[station_list[i]] = station_dict(station_list[i])
    return info

#checks if station has hcn flag
def hcn_stations(number):
    #This looks for a station id number in a list and returns true if it has an hcn flag
    fp2 = EV['GHCN'] + '/ghcnd-stations.txt'
    assert fp2 is not None, 'Filepath is not valid'
    ghcnd_stations = open(fp2,'r')
    rawdata2 = []

    for line2 in ghcnd_stations.readlines():
        rawdata2.append(line2)
    ghcnd_stations.close
    for line in rawdata2:
        #checks id of station to see that it passed through the previous module
        if (line[0:11] == number):
            #selects only data with hcn flag
            if (line[76:79] == "HCN"):
                return True
            else:
                return False


#creates a dict for each station
def station_dict(number):
    fp3 = EV['GHCN'] + '/ghcnd-stations.txt'
    assert fp3 is not None, 'Filepath is not valid'
    ghcnd_stations = open(fp3,'r')
    rawdata2 = []
    station_dict = {}
    #assemble list of stations and data
    for line in ghcnd_stations.readlines():
        rawdata2.append(line)
    ghcnd_stations.close
    #if the station id matches then the selected data will be added to station_dict
    for line in rawdata2:
        if (line[0:11] == number):
            station_dict["id"] = line[0:11]
            station_dict["name"] = line[41:71].strip()
            station_dict["lat"] = line[12:20]
            station_dict["lon"] = line[21:30]
            station_dict["elevation"] = line[31:37]
    return station_dict
def US_basemap():
    #_initialize figure and axes objects
    fig, ax = plt.subplots(1, 1)

    #_initizlize a basemap object
    #_there are many more options - see the readthedocs for a basic
    m = Basemap(  ax = ax, projection = 'merc', 
                  llcrnrlon=-130, llcrnrlat = 25,
                  urcrnrlon = -60, urcrnrlat=50, 
                  resolution = 'i')
    m.drawmapboundary()
    m.drawcountries()
    m.drawcoastlines()
    m.fillcontinents(lake_color = 'turquoise');
    return fig, ax, m
def add_shapefile(fp):
    #_initilize the map with our US_basemap function from above.
    fig, ax, m = US_basemap()
    output = m.readshapefile(shapefile = fp, name = 'climdivs')
    
    #_lets print the number of distinct shapes. type 
    #_help(m.readshapefile) to see what the output is
    
    print('Number of distinct shapes is %i' % output[0])
    
    return fig, ax, m

def colorMapper(data, scale):
    #_this helper function returns mapper that will normalize
    #_the colors in your dataset for plotting
    maxima = max(data.values)
    norm = mpl.colors.Normalize(vmin = -5,
                                vmax = scale,
                                clip = True)
    mapper = mpl.cm.ScalarMappable(norm = norm)
    return norm, mapper
def valueMap(data, fp, scale):
    from division_data import reverseStates, importStates
    fig, ax, m = add_shapefile(fp)
    norm, mapper = colorMapper(data, scale)
    
    #_importStates returns a dictionary where keys are states and
    #_values are the state code; reverseStates switches keys/values
    codes = reverseStates(importStates())
    
    #_the names in data.index are in the form 'statename-yy'
    #_where yy is the within state division code. However, we
    #_can see above that we need to change this to be 'yyxx' to
    #_match the shapefile info['CLIMDIV'], where yy is the state code
    
    #_we want to loop through every climate division, assign a color
    #_based on the value of data, and then plot it on the map
    for name in data.index:
        #_we use the codes dictionary to generate state codes from
        #_state names, and then add the in-state code
        divcode = codes[name[:-3]] + name[-2:]
        
        #_get the data value
        data_value = data[name]
        color = mapper.to_rgba(data_value)
        
        #_initizlize a list that can contain multiple polygons;
        #_remember, some shapes are made of several polygons
        patches = []
        
        #_loop through all the polygons and info
        for info, polygon in zip(m.climdivs_info, m.climdivs):
            if info['CLIMDIV'] == int(divcode):
                poly = mpl.patches.Polygon(np.array(polygon))
                patches.append(poly)
                
        #_add all patches that make the shape to the axis as a 
        #_collection with the same color 
        ax.add_collection(mpl.collections.PatchCollection(patches,
                            facecolor = color, edgecolor = 'k',
                            linewidths = 1., zorder = 2))
    
    #_add a colorbar
    c_ax = fig.add_axes([.925, .3, .025, .4])
    cb = mpl.colorbar.ColorbarBase(c_ax, norm = norm)
    c_ax.set_title('Events', fontsize = 8)
    
    return fig, ax, m