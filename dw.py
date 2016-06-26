import pandas as pd
import numpy as np
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
				break			# stop code if i is greater than 365/366 days depending on year

		df.loc[date,elem] = data #inserts data into elem for these dates

	return df


#selects stations with req. lat/long
def extract_stations(var, years, lat, lon):
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
						if(hcn_stations(line[0:11])):
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
			station_dict["name"] = line[41:71]
			station_dict["lat"] = line[12:20]
			station_dict["lon"] = line[21:30]
			station_dict["elevation"] = line[31:37]
	return station_dict

#creates master dictionary
def initialize_info(data, var = 'PRCP', debug = False):
	#Put in a variable to initilize the info dictionary
	info = {}
	info['var'] = var
	#add the data for the variable
	var_data = data[var]
	info['alldata'] = var_data
	return info


#initializes part of dict
def gen_phase(name, season, years, threshold):
	phase = {}
	phase['phase'] = name
	phase['season'] = season
	phase['years'] = years
	phase['threshold'] = threshold
	return phase

#converts dict to series so it can extract data easier, then turns it back into dictionary
def extract_particular_data(info, phase):
	"""
	Info is the initialized info, phase is a dictionary containing phase name
	season, and years.

	Variable will be a pandas series with a daily index
	Season will be a list of months, i.e. [3, 4, 5, 6] or [6, 7, 8]
	Years will be a list of years, i.e. [1928, 1956, 1972, 1999, 2001]
	"""

	data = pd.Series()
	sourceData = pd.Series()
	sourceData = info['alldata']

	for y in [phase["years"]]:

		for m in phase["season"]:

			index = '%d-%d' % (y,m)
			data = pd.concat((data, sourceData[index]))

	info['phase_data'] = data
	return info


#Selects data that is above threshold
def enso_threshold(info, threshold):
	data = []
	sourceData = pd.Series()
	sourceData = info['phase_data']

	for i in range(len(sourceData)):
		#selects data above threshold
		if (sourceData[i] > threshold[0]) & (sourceData[i] <= threshold[1]):
			data.append(sourceData[i])

	return data

#Calculate various statistics and places them in dict
def calc_stats(info):
	#Data run through enso_threshold should be accessed below
	info = np.asarray(info)
	info2 = {}
	info2['std'] = info.std()
	info2['mean'] = info.mean()
	info2['count'] = len(info)

	return info2


#Generates 3 dictionaries (3 thresholds) for EN phase
def phase_dicts(data, phase, months, year, var, threshold1, threshold2, threshold3):
	info = initialize_info(data, var)
	one = gen_phase(phase, months, year, threshold1)
	info = extract_particular_data(info, one)
	info = enso_threshold(info, (threshold1, threshold2))
	one['data'] = info
	info = calc_stats(info)
	one ['std'] = info['std']
	one ['mean'] = info['mean']
	one ['count'] = info['count']

	info = initialize_info(data, var)
	two = gen_phase(phase, months, year, threshold2)
	info = extract_particular_data(info, two)
	info = enso_threshold(info, (threshold2, threshold3))
	two['data'] = info
	info = calc_stats(info)
	two ['std'] = info['std']
	two ['mean'] = info['mean']
	two ['count'] = info['count']

	info = initialize_info(data, var)
	three = gen_phase(phase, months, year, threshold3)
	info = extract_particular_data(info, three)
	info = enso_threshold(info, (threshold3, np.inf))
	three['data'] = info
	info = calc_stats(info)
	three ['std'] = info['std']
	three ['mean'] = info['mean']
	three ['count'] = info['count']

	return one, two, three


#write dict to a file
def write_data(fp, phase_dict):
	pd = phase_dict
	#open file
	if os.path.isfile(fp):
		f = open(fp, 'a')

	else:
		f = open(fp, 'w')

		#write statement to file
		line = 'Year, T0_count, T0_mean, T1_count \n'
		f.write(line)

	#define new statement to be written
	y = pd[0]['years']
	c0 = pd[0]['count']
	m0 = pd[0]['mean']
	c1 = pd[1]['count']
	#arrange it
	line = '%i, %.0f, %.0f, %.0f \n' % (y,c0, m0, c1)
	#write statement to file
	f.write(line)
	f.close()

	return
#
if __name__ == '__main__':
	#debugging tool, sets name = main if 'run' else
	#loiter at this spot if imported
	div = 'Texas-06'
	n_yrs = 50
	startyr = 1945
	endyr = startyr + n_yrs - 1
	n_mon_sst = 3
	n_mon_mei = 3
	mei_lag = 3
	sst_lag = 3
	slp_lag = 2
	n_mon_slp = 2
	months = {'MAM' : [3, 4, 5]}
	bounds = {'Texas-06' : [30, 32.5, -102, -97], \
				'Texas-09': [28, 30, -101, -96]}

	kwgroups = create_kwgroups(	climdiv_months = months['MAM'], \
							sst_lag = sst_lag, n_mon_sst = n_mon_sst, \
							mei_lag = mei_lag, n_mon_mei = n_mon_mei, \
							slp_lag = slp_lag, n_mon_slp = n_mon_slp, \
							climdiv_startyr = startyr, n_yrs = n_yrs, \
							)
	season = 'MAM'
	mei, phaseind = create_phase_index(**kwgroups['mei'])
#mei = multivariance enso index
	base_fp = EV['GHCND_HCN']

	year_list = np.arange(startyr, endyr + 1)

	lat = (bounds[div][0], bounds[div][1])
	lon = (bounds[div][2], bounds[div][3])

	year_lim = (year_list.min(), \
				year_list.max())

	station_info = extract_stations(var = 'PRCP', years = year_lim, lat = lat, lon = lon)
################################################################################



#####_REPLACE THE FOLLOWING WITH METHODS IN THE STATION MODULE_#################
	for sid in station_info:
		fp = base_fp + sid + '.dly'

		if os.path.isfile(fp):
			data = extract_ghcn_daily(fp = fp, debug = True)
			for phase in phaseind:
				fp = EV['HOME'] + '/Desktop/test/' + season +'/' + station_info[sid]['name'][:10] + '_' + phase + '.txt'
				for year in year_list[phaseind[phase]]:
					PD = phase_dicts(data = data, phase = phase, year = year, \
									months = months[season], var = 'PRCP', \
									threshold1 = 0, threshold2 = 125, threshold3 = 250)
					write_data(fp, phase_dict = PD)
#####_


#
# dw calls station_dailyy for each station in region
# label slices
# add vertical whitespace
# station.Tdata.sum() or .mean() or .std()
# move phase dicts to station_data
# use named tuples instead of tuples
