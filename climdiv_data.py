#!/usr/bin/env python
"""
Module for loading climate division data for running NIPA
"""

import os
from division_data import *
from atmos_ocean_data import *
from os import environ as EV



def get_data(kwgroups):
	alldivDF, regionalDF, stateDF = load_climdiv_dataframes(**kwgroups['climdiv'])
	sst = openDAPsst(newFormat = True, anomalies = False, **kwgroups['sst'])
	mei, phaseind = create_phase_index(**kwgroups['mei'])
	return alldivDF, sst, mei, phaseind

def load_climdiv_dataframes(debug = False, **kwargs):

	##################
	###LOAD MODULES###
	##################
	import numpy as np
	import pandas as pd
	#_when you call the function, you use **kwgroups['climdiv']
	#_then, print within the function is kwgroups['climdiv']
	#_kwgroups is made by calling create_kwgroups (line 177 in data_load)
	fp = (kwargs['filin'])

	#_see importStates function
	states = importStates()
	#_see importDivs function
	divnums = importDivs()

	#_look at the text file that fp points to
	#_we use loadtxt with dtype set to 'string', so that every element in dat is a string
	#_the first column is the division code (see the readme in the climdiv folder)
	dat = np.genfromtxt(fp, dtype='str')

	def to_str(bytes_or_str):
		if isinstance(bytes_or_str, bytes):
			value = bytes_or_str.decode('utf-8')
		else:
			value = bytes_or_str
		return value

	# rows, cols = dat.shape
	# for i in range(rows):
	# 	for j in range(cols):
	# 		dat[i,j] = to_str(dat[i,j])


	#_now we'll split dat into an nx1 array containing division codes,
	#_and the data into a nx12 array containing the monthly data
	climcodes = dat[:,0]
	climdata = dat[:,1:]

	#_now i needed to extract the division codes from the year/month part of climcodes
	divcodes = []
	years = []
	for item in climcodes:
		divcodes.append(item[:4]) #_take through the 4th letter in the string
		years.append(item[-4:]) #_take from 4 from the end to the end.
		#_the middle items are left out because we know it's precipitation

	#_now to the lists into arrays

	divcodes = np.array(divcodes)
	#_okay this is where we loop through all our arrays, and append the data for one
	#_division into one long monthly time series.
	#_alldata is a dictionary where the key is the division name (i.e. 'Alabama-01', a string)
	#_use the 'next' command with pdb uncommented to see what is what at every step through the loop.

	alldata = {}
	divnames = []
	#import pdb; pdb.set_trace()
	for sc in sorted(states):
		for dc in divnums:
			division = sc+dc
			idx = np.where(divcodes == division)[0] #_np.where returns a tuple
			divdata = []
			if len(idx) > 0:
				for year in idx:
					yearlydata = climdata[year]
					for month in range(12):
						divdata.append(np.float(yearlydata[month]))
				divname = states[sc] + '-' + dc
				divnames.append(divname)
				alldata[divname] = divdata
			else:
				pass

	#import pdb; pdb.set_trace()

	#_calculate the number of months
	nperiods = 12*(int(years[-1]) - int(years[0]) + 1)
	#_start the year at the first year
	indstartyr = to_str(years[0])

	#_use pandas date_range function to form an index for the data frame. use the help command to see how it works.
	index = pd.date_range(indstartyr, periods = nperiods, freq = 'M')

	#_make a data frame from a dictionary (pandas method, which is why we put all the data in a dictinoary earlier)
	#_it automatically sets the column names as the dictionary keys
	data = pd.DataFrame.from_dict(alldata)

	#_now we set the index in the data frame to the one we created
	data = data.set_index(index)

	#_replace the missing values with nans to make calculations work corerctly
	data = data.replace(to_replace = -9.99, value = np.nan)


	######################################################
	#_from here on out, use pdb.set_trace() to chug through
	#_and figure out what's going on.  It's a little hacky,
	#_but that's how I roll.

	#_data is now a data frame with all the months and years in it in order:
	#_we need data output as seasonal totals for the set of years we
	#_want to analyze. so all the if statements make new dataframes after
	#_combining the data the appropriate way, depending on how kwgroups['climdiv'] is set
	#_through the create_kwgroups function.
	n = len(index)
	#print n
	#_transform for start date
	from transform import slp_tf
	tf = slp_tf()

	#_Now extract
	nmon = len(kwargs['months'])
	if kwargs['months'][-1] > 12:
		start = str(kwargs['startyr'] + 1) + '-' + tf[kwargs['months'][-1]]
		nperiods = kwargs['endyr'] - kwargs['startyr']
		rangeyrs = range(kwargs['startyr'] + 1 , kwargs['endyr'] + 1)
	else:
		start = str(kwargs['startyr']) + '-' + tf[kwargs['months'][-1]]
		nperiods = kwargs['endyr'] - kwargs['startyr'] + 1
		rangeyrs = range(kwargs['startyr'], kwargs['endyr'] + 1)
	if debug:
		print(len(rangeyrs))
		print('Start string is %s' % (start))
	index = pd.date_range(start, periods = nperiods, freq = '12M')
	#print index
	#time.sleep(3)
	newdataframe = pd.DataFrame(columns = index)
	indyears = data.index.year
	indmonths = data.index.month

	for year in rangeyrs:
		idx = np.repeat(False, n)
		bools = (indyears==year) & (indmonths == month)
		month = kwargs['months'][0]
		x = len(kwargs['months'])
		bools = (indyears==year) & (indmonths == month)
		loc = np.where(bools)[0]
		for y in range(x):
			idx[loc+y] = True
		"""
		This was the old code, they should both basically do the same thing
		though now it can split over years (i.e. start in N)
		for month in kwargs['months']:
			bools.append((indyears==year) & (indmonths == month))
		for b in bools:
			idx = idx | b
			"""
		newdataframe[str(year)] = data[idx].sum()

	newdataframe = newdataframe.T
	#if fp == EV['TAVG']:
	#	newdataframe = newdataframe / len(kwargs['months'])
	dataframes = {}
	for code in states:
		state = states[code]
		divlist = []
		for div in divnames:
			if div[:-3] == state:
				divlist.append(div)
		dataframes[state] = pd.DataFrame()
		for div in divlist:
			dataframes[state][div] = newdataframe[div]
	regions = importRegions()
	regionalDF = {}
	alldivDF = pd.DataFrame(index = dataframes['Wisconsin'].index)
	#import pdb; pdb.set_trace()
	for region in regions:
		regionalDF[region] = pd.DataFrame(index = dataframes['Wisconsin'].index)
		for state in regions[region]:
			for div in dataframes[state]:
				alldivDF[div] = dataframes[state][div]
				regionalDF[region][div] = dataframes[state][div]

	return alldivDF, regionalDF, dataframes

def loadAllMonbyDiv(filin = EV['PRCP']):

	"""
	Loads all months by division. Used by wetSeason to create boxplots and such.
	"""

	import numpy as np
	import pandas as pd
	fp = filin
	states = importStates()
	divnums = importDivs()
	dat = np.loadtxt(fp, dtype=str)
	climcodes = dat[:,0]
	climdata = dat[:,1:]
	divcodes = []
	years = []
	for item in climcodes:
		divcodes.append(item[:4])
		years.append(item[-4:])
	divcodes = np.array(divcodes)
	alldata = {}
	divnames = []
	for sc in sorted(states):
		for dc in divnums:
			division = sc+dc
			idx = np.where(divcodes == division)[0] #_np.where returns a tuple
			divdata = []
			if len(idx) > 0:
				for year in idx:
					yearlydata = climdata[year]
					for month in range(12):
						divdata.append(np.float(yearlydata[month]))
				divname = states[sc] + '-' + dc
				divnames.append(divname)
				alldata[divname] = divdata
			else:
				pass
	indstartyr = years[0]
	nperiods = 12*(int(years[-1]) - int(years[0]) + 1)
	index = pd.date_range(indstartyr, periods = nperiods, freq = 'M')
	data = pd.DataFrame.from_dict(alldata)
	data = data.set_index(index)
	data = data.replace(to_replace = -9.99, value = np.nan)
	return data


def create_kwgroups(debug = False, climdiv_startyr = 1895, n_yrs = 120, \
	climdiv_months = [3, 4, 5], n_mon_sst = 3, sst_lag = 3, n_mon_slp = 2, \
	slp_lag = 2, n_mon_mei = 3, mei_lag = 3, filin = EV['PRCP']):

	"""
	This function takes information about the seasons, years, and type of divisional
	data to look at, and creates appropriate kwgroups (parameters) to be input into
	data loading and openDap modules.
	"""

	#_Check a few things
	assert os.path.isfile(filin), 'File does not exist'
	assert climdiv_startyr >= 1895, 'Divisional data only extends to 1895'
	assert climdiv_months[0] >= 1, 'Divisonal data can only wrap to the following year'
	assert climdiv_months[-1] <= 15, 'DJFM (i.e. [12, 13, 14, 15]) is the biggest wrap allowed'

	#_Following block sets the appropriate start month for the SST and SLP fields
	#_based on the input climdiv_months and the specified lags
	sst_months = []
	slp_months = []
	mei_months = []
	sst_start = climdiv_months[0] - sst_lag
	sst_months.append(sst_start)
	slp_start = climdiv_months[0] - slp_lag
	slp_months.append(slp_start)
	mei_start = climdiv_months[0] - mei_lag
	mei_months.append(mei_start)

	#_The for loops then populate the rest of the sst(slp)_months based n_mon_sst(slp)
	for i in range(1, n_mon_sst):
		sst_months.append(sst_start + i)
	for i in range(1, n_mon_slp):
		slp_months.append(slp_start + i)
	for i in range(1, n_mon_mei):
		mei_months.append(mei_start + i)

	assert sst_months[0] >= -8, 'sst_lag set too high, only goes to -8'
	assert slp_months[0] >= -8, 'slp_lag set too high, only goes to -8'
	assert mei_months[0] >= -8, 'mei_lag set too high, only goes to -8'

	#_Next block of code checks start years and end years and sets appropriately.
	#_So hacky..
	#########################################################
	#########################################################
	if climdiv_months[-1] <= 12:
		climdiv_endyr = climdiv_startyr + n_yrs - 1
		if sst_months[0] < 1 and sst_months[-1] < 1:
			sst_startyr = climdiv_startyr - 1
			sst_endyr = climdiv_endyr - 1
		elif sst_months[0] < 1 and sst_months[-1] >= 1:
			sst_startyr = climdiv_startyr - 1
			sst_endyr = climdiv_endyr
		elif sst_months[0] >=1 and sst_months[-1] >= 1:
			sst_startyr = climdiv_startyr
			sst_endyr = climdiv_endyr
	elif climdiv_months[-1] > 12:
		climdiv_endyr = climdiv_startyr + n_yrs
		if sst_months[0] < 1 and sst_months[-1] < 1:
			sst_startyr = climdiv_startyr - 1
			sst_endyr = climdiv_endyr - 2
		elif sst_months[0] < 1 and sst_months[-1] >= 1:
			sst_startyr = climdiv_startyr - 1
			sst_endyr = climdiv_endyr - 1
		elif sst_months[0] >=1 and 1 <= sst_months[-1] <= 12:
			sst_startyr = climdiv_startyr
			sst_endyr = climdiv_endyr - 1
		elif sst_months[0] >=1 and sst_months[-1] > 12:
			sst_startyr = climdiv_startyr
			sst_endyr = climdiv_endyr
	if climdiv_months[-1] <= 12:
		climdiv_endyr = climdiv_startyr + n_yrs - 1
		if mei_months[0] < 1 and mei_months[-1] < 1:
			mei_startyr = climdiv_startyr - 1
			mei_endyr = climdiv_endyr - 1
		elif mei_months[0] < 1 and mei_months[-1] >= 1:
			mei_startyr = climdiv_startyr - 1
			mei_endyr = climdiv_endyr
		elif mei_months[0] >=1 and mei_months[-1] >= 1:
			mei_startyr = climdiv_startyr
			mei_endyr = climdiv_endyr
	elif climdiv_months[-1] > 12:
		climdiv_endyr = climdiv_startyr + n_yrs
		if mei_months[0] < 1 and mei_months[-1] < 1:
			mei_startyr = climdiv_startyr - 1
			mei_endyr = climdiv_endyr - 2
		elif mei_months[0] < 1 and mei_months[-1] >= 1:
			mei_startyr = climdiv_startyr - 1
			mei_endyr = climdiv_endyr - 1
		elif mei_months[0] >=1 and 1 <= mei_months[-1] <= 12:
			mei_startyr = climdiv_startyr
			mei_endyr = climdiv_endyr - 1
		elif mei_months[0] >=1 and mei_months[-1] > 12:
			mei_startyr = climdiv_startyr
			mei_endyr = climdiv_endyr
	if climdiv_months[-1] <= 12:
		climdiv_endyr = climdiv_startyr + n_yrs - 1
		if slp_months[0] < 1 and slp_months[-1] < 1:
			slp_startyr = climdiv_startyr - 1
			slp_endyr = climdiv_endyr - 1
		elif slp_months[0] < 1 and slp_months[-1] >= 1:
			slp_startyr = climdiv_startyr - 1
			slp_endyr = climdiv_endyr
		elif slp_months[0] >=1 and slp_months[-1] >= 1:
			slp_startyr = climdiv_startyr
			slp_endyr = climdiv_endyr
	elif climdiv_months[-1] > 12:
		climdiv_endyr = climdiv_startyr + n_yrs
		if slp_months[0] < 1 and slp_months[-1] < 1:
			slp_startyr = climdiv_startyr - 1
			slp_endyr = climdiv_endyr - 2
		elif slp_months[0] < 1 and slp_months[-1] >= 1:
			slp_startyr = climdiv_startyr - 1
			slp_endyr = climdiv_endyr - 1
		elif slp_months[0] >=1 and 1 <= slp_months[-1] <= 12:
			slp_startyr = climdiv_startyr
			slp_endyr = climdiv_endyr - 1
		elif slp_months[0] >=1 and slp_months[-1] > 12:
			slp_startyr = climdiv_startyr
			slp_endyr = climdiv_endyr
	#########################################################
	#########################################################

	if debug:
		from transform import int_to_month
		i2m = int_to_month()
		print('Precip starts in %s-%d, ends in %s-%d' % \
			(i2m[climdiv_months[0]], climdiv_startyr, i2m[climdiv_months[-1]], climdiv_endyr))
		print('SST starts in %s-%d, ends in %s-%d' % \
			(i2m[sst_months[0]], sst_startyr, i2m[sst_months[-1]], sst_endyr))
		print('SLP starts in %s-%d, ends in %s-%d' % \
			(i2m[slp_months[0]], slp_startyr, i2m[slp_months[-1]], slp_endyr))
		print('MEI starts in %s-%d, ends in %s-%d' % \
			(i2m[mei_months[0]], mei_startyr, i2m[mei_months[-1]], mei_endyr))

	#_Create function output
	kwgroups = {
		'climdiv'	: {	'filin'		: filin,
						'startyr'	: climdiv_startyr,
						'endyr'		: climdiv_endyr,
						'months'	: climdiv_months
						},

		'sst'		: {	'n_mon'		: n_mon_sst,
						'months'	: sst_months,
						'startyr'	: sst_startyr,
						'endyr'		: sst_endyr
						},

		'slp'		: {	'n_mon'		: n_mon_slp,
						'months'	: slp_months,
						'startyr'	: slp_startyr,
						'endyr'		: slp_endyr,
						'n_year'	: n_yrs
						},
		'mei'		: {	'n_mon'		: n_mon_mei,
						'months'	: mei_months,
						'startyr'	: mei_startyr,
						'endyr'		: mei_endyr,
						'n_year'	: n_yrs
						}
				}



	return kwgroups

def create_phase_index(debug = False, **kwargs):
	# kwargs = kwgroups['mei']
	from numpy import sort
	mei = load_mei()
	from numpy import where, arange, zeros, inf
	from transform import slp_tf
	tran = slp_tf()
	startmon = int(tran[kwargs['months'][0]])
	startyr = kwargs['startyr']
	idx_start = where((mei.index.year == startyr) & (mei.index.month == startmon))
	idx = []
	[idx.extend(arange(kwargs['n_mon']) + idx_start + 12*n) for n in range(kwargs['n_year'])]
	mei_avg = zeros((kwargs['n_year']))
	for year, mons in enumerate(idx):
		mei_avg[year] = mei.values[mons].mean()

	mei = sort(mei_avg)
	pos = mei[mei>0]
	neg = mei[mei<0]
	n_el = int(round(len(pos)*0.34))
	n_la = int(round(len(neg)*0.34))
	n_np = int(len(pos) - n_el)
	n_nn = int(len(neg) - n_la)


	cutoffs = {
		'la'	: (neg[0], neg[n_la-1]),
		'nn'	: (neg[n_la], neg[-1]),
		'np'	: (pos[0], pos[n_np-1]),
		'el'	: (pos[-n_el], pos[-1]),
		'N'		: (neg[n_la + 1], pos[n_np-1])
	}

	phaseind = {
			'elnino' 	: (mei_avg >= cutoffs['el'][0]) & (mei_avg <= \
				cutoffs['el'][1]),
			'lanina' 	: (mei_avg >= cutoffs['la'][0]) & (mei_avg <= \
				cutoffs['la'][1]),
			'neutral'	: (mei_avg >= cutoffs['N'][0]) & (mei_avg <= \
				cutoffs['N'][1]),
			'neutpos'	: (mei_avg >= cutoffs['np'][0]) & (mei_avg <= \
				cutoffs['np'][1]),
			'neutneg'	: (mei_avg >= cutoffs['nn'][0]) & (mei_avg <= \
				cutoffs['nn'][1]),
			'allyears'	: (mei_avg >= -inf)
			}


	return mei_avg, phaseind
