import matplotlib as mpl
#mpl.use('tkagg')
import pandas as pd
import numpy as np
import os, math, time
from os import environ as EV
from matplotlib import cm ,rcParams, pyplot as plt
from climdiv_data import *
from atmos_ocean_data import *
from dw import *
from station_module import *
from numpy import isnan, sum, zeros
from extremes import bootstrp
#Set up environment variable dictionary
rcParams['lines.linewidth'] = 2





if __name__ == '__main__':
    div = 'Northeast'
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
                'Texas-09': [28, 30, -101, -96],
				'Northeast': [39, 41, -76.5, -75.5]}

    kwgroups = create_kwgroups(    climdiv_months = months['MAM'], \
                            sst_lag = sst_lag, n_mon_sst = n_mon_sst, \
                            mei_lag = mei_lag, n_mon_mei = n_mon_mei, \
                            slp_lag = slp_lag, n_mon_slp = n_mon_slp, \
                            climdiv_startyr = startyr, n_yrs = n_yrs, \
                            )
    season = 'MAM'
    mei, phaseind = create_phase_index(**kwgroups['mei'])

    base_fp = EV['GHCND_HCN']

    year_list = np.arange(startyr, endyr + 1)

    lat = (bounds[div][0], bounds[div][1])
    lon = (bounds[div][2], bounds[div][3])

    year_lim = (year_list.min(), \
                year_list.max())

    station_info = extract_stations(var = 'PRCP', years = year_lim,
                                    lat = lat, lon = lon)
    station_list = ['USC00304174']
    thresholds = (0, 64) #threshold values
    NIPAdata = []
    NIPAdata.append(('El Nino', [3, 4, 5, 6],
                    [1926, 1931, 1941, 1942, 1958, 1966, 1973,
                    1983, 1992, 1995, 1998, 2010]))
    NIPAdata.append(('La Nina', [3, 4, 5, 6], [1925, 1934, 1943,
                    1950, 1951, 1955, 1956, 1957, 1971, 1972, 1974,
                    1975, 1976, 1989, 1999, 2000, 2008]))
    NIPAdata.append(('Neutral Positive', [3, 4, 5, 6], [1924, 1927,
                    1928, 1930, 1932, 1936, 1937, 1940, 1947, 1952, 1954,
                    1959, 1964, 1969, 1970, 1977, 1978, 1979, 1980, 1988,
                    1990, 1991, 1993, 1994, 2004, 2005, 2007]))
    NIPAdata.append(('Neutral Negative', [3, 4, 5, 6], [1921, 1922, 1923,
                        1929, 1933, 1935, 1938, 1939, 1944, 1945, 1946,
                        1948, 1949, 1953, 1960, 1961, 1962, 1963, 1965,
                        1967, 1968, 1981, 1982, 1984, 1985, 1986, 1996,
                        1997, 2001, 2002, 2006, 2009]))
    NIPAdata.append(('All Years', [3, 4, 5, 6], np.arange(1921,2011)))

    stations = []
    for stationID in station_list:
        for data in NIPAdata:
            var = 'PRCP'
            station = stationDaily(var, stationID, data)
            station.threshold(thresholds)
            station.otherstatistics()
            stations.append(station)
            print np.sum(np.isnan(station.data))
	def mean_0(stations):
		for station in stations:
		    print station.phase
		    print np.sum(~np.isnan(station.Tdata['0'])).mean()
		return

	def std_0(stations):
		for station in stations:
		    print station.phase
		    print np.sum(~np.isnan(station.Tdata['0'])).std()
		return

	def gev_0(stations):
		from scipy.stats import genextreme as gev
		ax = plt.subplot()
		lim = 200
		for station in stations:
			data = station.data
			x = data[data > lim].values.ravel()
			x = x[~isnan(x)]
			shp, loc, scl = gev.fit(x)
			p_x = np.arange(0, x.max() + 100, 0.1)
			pdf = gev.pdf(p_x, shp, loc = loc, scale = scl)
			ax.plot(p_x, pdf, label = station.phase)
		plt.legend()
		plt.show()
		return

	def gamma_0(stations):
		from scipy.stats import gamma
		ax = plt.subplot()
		lim = 0
		for station in stations:
			data = station.data
			x = data[data>0].values.ravel()
			x = x[~isnan(x)]
			print len(x)
			shp, loc, scl = gamma.fit(x, floc = 0)
			p_x = np.arange(0, 500, 0.1)
			pdf = gamma.pdf(p_x, shp, scale = scl)
			ax.plot(p_x, pdf, label = station.phase)
		plt.legend()
		plt.show()
		return
