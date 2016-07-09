#!/usr/bin/env python
"""
Module for loading atmospheric and oceanic data necessary to run NIPA
"""

import os
from os import environ as EV

def weightsst(sst):
	from numpy import cos, radians
	weights = cos(radians(sst.lat))
	for i, weight in enumerate(weights):
		sst.data[:,i,:] *= weight
	return sst

def sig_test(r, n, twotailed = True):
	import numpy as np
	from scipy.stats import t as tdist
	df = n - 2

	#Create t-statistic
		#Use absolute value to be able to deal with negative scores
	t = np.abs(r * np.sqrt(df/(1-r**2)))
	p = (1 - tdist.cdf(t,df))
	if twotailed:
		p = p * 2
	return p

def vcorr(X, y):
	import numpy as np
	from scipy.stats import pearsonr
	from time import time

	t = X.shape[0]
	nlat = X.shape[1]
	nlon = X.shape[2]
	N = nlat * nlon

	y = y.reshape(1,t)
	X = X.reshape(t,N).T
	Xm = X.mean(axis = 1).reshape(N,1)
	ym = y.mean()
	r_num = np.sum((X-Xm) * (y-ym), axis = 1)
	r_den = np.sqrt(np.sum((X-Xm)**2, axis = 1) * np.sum((y-ym)**2))
	r = (r_num/r_den).reshape(nlat, nlon)
	return r

def openDAPsst(version = '4', debug = False, anomalies = True, newFormat = False, **kwargs):
	"""
	This function downloads data from the new ERSSTv4 on the IRI data library
	kwargs should contain: startyr, endyr, startmon, endmon, nbox
	"""
	from transform import int_to_month
	from os.path import isfile
	from pydap.client import open_url
	from numpy import arange
	import pickle
	import re
	from collections import namedtuple


	SSTurl = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCDC/.ERSST/.version' + version + '/' + \
	'.anom/T/%28startmon%20startyr%29%28endmon%20endyr%29RANGEEDGES/T/nbox/0.0/boxAverage/dods'

	if not anomalies:
		SSTurl = 'http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCDC/.ERSST/.version' + version + '/' + \
		'.sst/T/%28startmon%20startyr%29%28endmon%20endyr%29RANGEEDGES/T/nbox/0.0/boxAverage/dods'
	print SSTurl

	i2m = int_to_month()

	DLargs = {
		'startmon'	: i2m[kwargs['months'][0]],
		'endmon'	: i2m[kwargs['months'][-1]],
		'startyr'	: str(kwargs['startyr']),
		'endyr'		: str(kwargs['endyr']),
		'nbox'	 	: str(kwargs['n_mon'])
			}
	fp = EV['DATA'] + '/nipa/SST/' + DLargs['startmon'] + DLargs['startyr'] + \
		'_' + DLargs['endmon'] + DLargs['endyr'] + '_nbox_' + DLargs['nbox'] + '_version' + version + 'anoms'
	if not anomalies:
		fp = fp + '_ssts'

	seasonal_var = namedtuple('seasonal_var', ('data','lat','lon'))
	if isfile(fp):
		#print('Using pickled SST')
		f = open(fp)
		sstdata = pickle.load(f)
		f.close()
		var = seasonal_var(sstdata['grid'], sstdata['lat'], sstdata['lon'])
		if newFormat:
			return var
		return sstdata
	else:
		print('New SST field, will save to')
		print(fp)

	for kw in DLargs:
		SSTurl = re.sub(kw, DLargs[kw], SSTurl)

	dataset = open_url(SSTurl)
	if anomalies: arg = 'anom'
	if not anomalies: arg = 'sst'
	sst = dataset[arg]
	time = dataset['T']
	print('Starting download...')
	grid = sst.array[:,:,:,:].squeeze()
	t = time.data[:].squeeze()
	sstlat = dataset['Y'][:]
	sstlon = dataset['X'][:]
	print('Download finished.')

	#_Grid has shape (ntim, nlat, nlon)

	nseasons = 12 / kwargs['n_mon']
	if debug:
		print('Number of seasons is %i, number of months is %i' % (nseasons, kwargs['n_mon']))
	ntime = len(t)



	idx = arange(0, ntime, nseasons)
	sst = grid[idx]

	var = seasonal_var(sst, sstlat, sstlon)

	sstdata = {
		'grid'	: sst,
		'lon'	: sstlon,
		'lat'	: sstlat
			}

	f = open(fp,'w')
	pickle.dump(sstdata,f)
	f.close()
	if newFormat:
		return var


	return sstdata

def load_slp(newFormat = False, debug = False, anomalies = True, **kwargs):
	"""
	This function loads HADSLP2r data.
	"""
	from transform import slp_tf, int_to_month
	from netCDF4 import Dataset
	from sklearn.preprocessing import scale
	from numpy import arange, zeros, where
	from os.path import isfile
	import pandas as pd
	import pickle

	transform = slp_tf()	#This is for transforming kwargs into DLargs

	DLargs = {
		'startmon'	: transform[kwargs['months'][0]],
		'endmon'	: transform[kwargs['months'][-1]],
		'startyr'	: str(kwargs['startyr']),
		'endyr'		: str(kwargs['endyr']),
		'nbox'		: str(kwargs['n_mon'])
			}
	i2m = int_to_month() #_Use in naming convention
	fp = EV['DATA'] + '/nipa/SLP/' + i2m[kwargs['months'][0]] + \
		DLargs['startyr'] + '_' + i2m[kwargs['months'][-1]] + \
		DLargs['endyr'] + '_nbox_' + DLargs['nbox']

	if isfile(fp):
		f = open(fp)
		slpdata = pickle.load(f)
		f.close()
		if newFormat:
			from collections import namedtuple
			seasonal_var = namedtuple('seasonal_var', ('data','lat','lon'))
			slp = seasonal_var(slpdata['grid'], slpdata['lat'], slpdata['lon'])
			return slp
		return slpdata
	print('Creating new SLP pickle from netCDF file')

	#_Next block takes the netCDF file and extracts the time to make
	#_a time index.
	nc_fp = EV['DATA'] + '/netCDF/slp.mnmean.real.nc'
	dat = Dataset(nc_fp)
	t = dat.variables['time']
	extractargs = {
		'start'		: '1850-01',
		'periods'	: len(t[:]),
		'freq'		: 'M',
			}
	timeindex = pd.date_range(**extractargs)


	#Need to get start and end out of time index
	startyr = kwargs['startyr']
	startmon = int(DLargs['startmon'])

	idx_start = where((timeindex.year == startyr) & (timeindex.month == startmon))
	idx = []
	[idx.extend(arange(kwargs['n_mon']) + idx_start + 12*n) for n in range(kwargs['n_year'])]

	"""
	This is how sst open dap does it but doesn't work for this
	idx = ((timeindex.year >= int(DLargs['startyr'])) & \
			((timeindex.month >= int(DLargs['startmon'])) & \
			 (timeindex.month <= int(DLargs['endmon'])))) & \
				((timeindex.year <= int(DLargs['endyr'])))
	"""


	if debug:
		print(timeindex[idx][:10])

	lat = dat.variables['lat'][:]
	lon = dat.variables['lon'][:]
	slp = dat.variables['slp'][:]

	nlat = len(lat)
	nlon = len(lon)
	time = timeindex[idx]
	slpavg = zeros((kwargs['n_year'], nlat, nlon))

	for year, mons in enumerate(idx):
		slpavg[year] = slp[mons].mean(axis=0)
		if debug:
			print('Averaging ', mons)

	#WHERE TO SCALE THE DATA?
	for i in range(nlat):
		for j in range(nlon):
			slpavg[:,i,j] = scale(slpavg[:,i,j])
	slpdata = {
			'grid'	:	slpavg,
			'lat'	:	lat,
			'lon'	:	lon
			}
	f = open(fp,'w')
	pickle.dump(slpdata,f)
	print('SLP data saved to %s' % (fp))
	f.close()
	if newFormat:
		from collections import namedtuple
		seasonal_var = namedtuple('seasonal_var', ('data','lat','lon'))
		slp = seasonal_var(slpdata['grid'], slpdata['lat'], slpdata['lon'])
		return slp
	return slpdata

def load_mei(debug = False):
	import numpy as np
	import pandas as pd
	import pickle
	 #_Store all bash environment variables in the dict 'EV'

	fp = EV['DATA'] + 'mca/mei/mei.pkl'
	if os.path.isfile(fp):
		if debug:
			print('Using pickled mei')
		f = open(fp)
		mei = pickle.load(f)
		f.close()
		return mei
	else:
		if debug:
			print('Creating mei from .txt files')
		#First load extended MEI
		fp = EV['DATA'] + '/mca/mei/extended_mei.txt'
		df = pd.read_csv(fp, sep = '\t', index_col = 0, skiprows = 7)
		values = df.values.reshape(df.values.size) #reshape to 1-D

		timeargs = {
			'start'		: '1871-01',
			'periods'	: len(values),
			'freq'		: 'M'
					}
		timeindex = pd.date_range(**timeargs)	#create time index based on month(i)

		ext_mei = pd.DataFrame(index = timeindex)
		ext_mei['mei'] = values

		#Now load MEI, and add to extended MEI (from 1950)
		#_also had to remove some lines from bottom of textfile.
		fp = EV['DATA'] + '/mca/mei/mei.txt'
		df = pd.read_csv(fp, sep = '\t', index_col = 0, skiprows = 47)
		values = df.values.reshape(df.values.size)

		timeargs = {
			'start'		: '1950-01',
			'periods'	: len(values),
			'freq'		: 'M'
					}
		timeindex = pd.date_range(**timeargs)

		new_mei = pd.DataFrame(index = timeindex)
		new_mei['mei'] = values

		mei = pd.concat((ext_mei[:948],new_mei[:])) #only use ext_mei up to dec 1949

		fp = EV['DATA'] + '/mca/mei/mei.pkl'

		f = open(fp,'w')

		pickle.dump(mei,f)

		f.close()
		return mei
