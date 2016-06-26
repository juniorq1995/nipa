import pandas as pd
import numpy as np
import os, math
from matplotlib import pyplot as plt
import time
#Set up environment variable dictionary
EV = dict(os.environ)

def extract_ghcn_daily(fp = None, debug = False):
	
	assert fp is not None, 'Filepath is not valid'
	#Open the file for reading
	f = open(fp, 'r')

	#Make an empty list to load the filestrings into
	rawdata = []


	for line in f.readlines():
		rawdata.append(line)
	f.close()


	startyr = rawdata[0][11:15]
	startmon = rawdata[0][15:17]
	endyr = rawdata[-1][11:15]
	endmon = rawdata[-1][15:17]

	index = pd.date_range(start = startyr + '-' + startmon, end = endyr + '-' + endmon, freq = 'D') # create index
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
		#if debug:
		#	print 'Importing daily %s data from %s which has %i days.' % (elem, date, ndays)
		#	import time
		#	time.sleep(5)
		for i, lims in enumerate(values_idx): # indexes values_idx
			data[i] = line[lims[0]:lims[1]] # what is lims?
			#if debug:
			#	print 'Data for day %i is located between columns %i and %i, the value is %i' % (i+1, lims[0], lims[1], data[i])
				#time.sleep(1)
			if data[i] == -9999: # replace -9999 with nan
				data[i] = np.nan
			if i + 1 == ndays:
				break			# stop code if i is greater than 365/366 days depending on year
		df.loc[date,elem] = data #inserts data into elem for these dates
	return df

def extract_stations(var, years, lat, lon):
	#reads a file	
	station_list = []
	fp = EV['DATA'] + 'ghcnd-inventory.txt'
	assert fp is not None, 'Filepath is not valid'
	f = open(fp,'r')
	rawdata = []
	#checks each line in file against paramters
	for line in f.readlines():
		rawdata.append(line)
	f.close
	for line in rawdata:
		if(lat[1]>=float(line[12:20]) >= lat[0]):
			if(lon[1]>=float(line[21:30]) >= lon[0]):	
				if (line[31:35] == var):
					if (int(line[36:40])<=years[0] and int(line[41:45])>=years[1]):
						#if everything checks out the id of the station is added to a list
						if(hcn_stations(line[0:11])):
							station_list.append(line[0:11]) 
	#the master dictionary is created 
	info = {}
	#each station that matches will be placed in its own sub-dictionary which lies inside the master 	
	for i,lines in enumerate (station_list):
		info[station_list[i]] = station_dict(station_list[i])
	return info

def hcn_stations(number):
	fp2 = EV['DATA'] + 'ghcnd-stations.txt'
	assert fp2 is not None, 'Filepath is not valid'
	f2 = open(fp2,'r')
	rawdata2 = []	
	info2 = {}
	for line2 in f2.readlines():
		rawdata2.append(line2)
	f2.close
	for line2 in rawdata2:
		#checks id of station to see that it passed through the previous module
		if (line2[0:11] == number):
			if (line2[76:79] == "HCN"):
				return True
			else:
				return False
						
#creates the sub-dictionaries								
def station_dict(number):
	#read file
	fp2 = EV['DATA'] + 'ghcnd-stations.txt'
	assert fp2 is not None, 'Filepath is not valid'
	f2 = open(fp2,'r')
	rawdata2 = []	
	info2 = {}
	for line2 in f2.readlines():
		rawdata2.append(line2)
	f2.close
	for line2 in rawdata2:
		#checks id of station to see that it passed through the previous module
		if (line2[0:11] == number):
			#check HCN flag
			if(line2[76:79]=="HCN"):
				info2["Station ID"] = line2[0:11]
				info2["Station Name"] = line2[41:71]
				info2["Station Lat"] = line2[12:20]
				info2["Station Lon"] = line2[21:30]
				info2["Station Elevation"] = line2[31:37]
				info2['Tag'] = line2[76:79]
				
					
			
					
		
				
	return info2		
		
def initialize_info(data, var = 'PRCP', debug = False):
	#Put in a variable to initilize the info dictionary
	info = {}
	info['var'] = var
	var_data = data[var]
	info['alldata'] = var_data
	return info
	
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
	for y in phase["years"]:
		for m in phase["season"]:
			index = '%d-%d' % (y,m)
			data = pd.concat((data, sourceData[index]))
	
	info['phase_data'] = data		
	return info
#converts dict to series so it can compare, then turns it back into dictionary	
def enso_threshold(info, threshold):
	data = []
	sourceData = pd.Series()
	sourceData = info['phase_data']
	for i in range(len(sourceData)):
		if sourceData[i] > threshold:
			data.append(sourceData[i])
	return data
		
def calc_stats(info):
	#Data run through enso_threshold should be accessed below
	info = np.asarray(info)
	info2 = {}
	info2['std'] = info.std()
	info2['mean'] = info.mean()
	info2['count'] = len(info)
	
	return info2
	
#Generates 3 dictionaries (3 thresholds) for EN phase		
def phase_dicts(data, phase, season, years, var, threshold1, threshold2, threshold3):
	info = initialize_info(data, var)
	one = gen_phase(phase, season, years, threshold1)
	info = extract_particular_data(info, one)
	info = enso_threshold(info, threshold1)
	one['data'] = info
	info = calc_stats(info)
	one ['std'] = info['std']
	one ['mean'] = info['mean']
	one ['count'] = info['count']
	
	info = initialize_info(data, var)
	two = gen_phase(phase, season, years, threshold2)
	info = extract_particular_data(info, two)
	info = enso_threshold(info, threshold2)
	two['data'] = info
	info = calc_stats(info)
	two ['std'] = info['std']
	two ['mean'] = info['mean']
	two ['count'] = info['count']
	
	info = initialize_info(data, var)
	three = gen_phase(phase, season, years, threshold3)
	info = extract_particular_data(info, three)
	info = enso_threshold(info, threshold3)
	three['data'] = info
	info = calc_stats(info)
	three ['std'] = info['std']
	three ['mean'] = info['mean']
	three ['count'] = info['count']
	
	return one, two, three
	

if __name__ == '__main__':#debugging tool, sets name = main if 'run' else loiter at this spot if imported
	#Set the base folder for filepaths to .dly files
	phases = ['El Nino', 'La Nina', 'Neutral Negative', 'Neutral Positive']
	base_fp = EV['DATA'] + 'ghcn/ghcnd_hcn/'
	info = extract_stations(var = 'PRCP', years =(1921,2010),lat = (30,32.5),lon = (-102,-98))
	n = 0
	for station in info:
		n += 1
	print n	 
	#Pick out the file you want, and create a filepath to it
	fp = base_fp + 'USC00011084.dly'
	data = extract_ghcn_daily(fp = fp, debug = True)#final dataframe
	#for id in info:
		#fp = base_fp + id + '.dly'
		#data = extract_ghcn_daily(fp = fp, debug = True)
	#indent	
		#years = {}
		#years['El Nino'] = [1926, 1931, 1941, 1942, 1958, 1966, 1973, 1983, 1992, 1995, 1998, 2010]
		#years['La Nina'] = [1934, 1943, 1950, 1951, 1955, 1956, 1971, 1974, 1975, 1976, 1989, 1999, 2000, 2008]
		#open/create file 
		#f = open('Results'+info[id]+['Station Name'], 'w')
		#create phase dicts
		#for phase in phases:
		#	for year in years[phase]:
		#		EN1, EN2, EN3 = phase_dicts(data, 'El Nino', [3, 4, 5, 6],var = 'PRCP',threshold1 = 0, \
		#									threshold2 = 125, threshold3 = 250)
				#Calculate some stuff
		
				
	
	
	EN1, EN2, EN3 = phase_dicts(data, 'El Nino', [3, 4, 5, 6],[1926, 1931, 1941, 1942, 1958, 1966, 1973, 1983, 1992, 1995, 1998, 2010],var = 'PRCP',threshold1 = 0, threshold2 = 125, threshold3 = 250)
	
	LN1, LN2, LN3 = phase_dicts(data, 'La Nina', [3, 4, 5, 6],[1934, 1943, 1950, 1951, 1955, 1956, 1971, 1974, 1975, 1976, 1989, 1999, 2000, 2008],var = 'PRCP',threshold1 = 0, threshold2 = 125, threshold3 = 250)
	#NN1, NN2, NN3 = phase_dicts(data, 'Neutral Negative', [3,4,5,6],[1921, 1922, 1923, 1929, 1933, 1935, 1938, 1939, 1944, 1945, 1946, 1948, 1949, 1953, 1957, 1960, 1961, 1962, 1963, 1965, 1967, 1968, 1972, 1981, 1982, 1984, 1985, 1986, 1996, 1997, 2001, 2002, 2006, 2009],var = 'PRCP',threshold1 = 0, threshold2 = 125, threshold3 = 250)
	#NP1, NP2, NP3 = phase_dicts(data, 'Neutral Positive',[3,4,5,6],[1924, 1927, 1928, 1930, 1932, 1936, 1937, 1940, 1947, 1952, 1954, 1959, 1964, 1969, 1970, 1977, 1978, 1979, 1980, 1987, 1988, 1990, 1991, 1993, 1994, 2003, 2004, 2005, 2007],var = 'PRCP',threshold1 = 0, threshold2 = 125, threshold3 = 250) 
	 #create a list of dictionaries
	d1 = [LN1, EN1]#removed NN & NP
	d2 = [LN2, EN2]
	d3 = [LN3, EN3]
	for d in [d1, d2, d3]:
		for item in d:
			p = item['phase']
			x = item['count']
			t = item['threshold']
			m = item['mean']
			#print 'There were %.0f %s events over %.0f tenths mm' % (x,p, t)
			#line = 'events = %.0f, threshold =  %.0f,   %.0f' %(x,t)
			#f.write(line)
			#f.close()
	
			#print item['count']
			#print float(item['count'])/len(item['years'])
	#sdfl = [1,2,3,4,5,6,7,8,9,10]
	
	#create plots
	fig = plt.figure(figsize = (10,12))
	ax1 = fig.add_subplot(221)
	ax2 = fig.add_subplot(222)
	ax3 = fig.add_subplot(223)
	ax4 = fig.add_subplot(224)
	
	ax1.hist(EN1['data'])
	#fp = '/Users/quinteroj/Desktop/pic1'
	#fig.savefig(fp)
			
	#plt.hist(EN1['data'])
	#plt.show()
	#figure out which stations are in a states region i.e. Texas 01
	#four phases per station
	#different thresholds per phase
	#info['data'] = data
	#return info
	# 4 phases, 3 thresholds for each,so 12 info dictionaries
	#El Nino

	#[1926, 1931, 1941, 1942, 1958, 1966, 1973, 1983, 1992, 1995, 1998, 2010]

	#La Nina

	#[1925, 1934, 1943, 1950, 1951, 1955, 1956, 1971, 1974, 1975, 1976, 1989, 1999, 2000, 2008]

	#Neutral Positive

	#[1924, 1927, 1928, 1930, 1932, 1936, 1937, 1940, 1947, 1952, 1954, 1959, 1964, 1969, 1970, 1977, 1978, 1979, 1980, 1987, 1988, 1990, 1991, 1993, 1994, 2003, 2004, 2005, 2007]

	#Neutral Negative

	#[1921, 1922, 1923, 1929, 1933, 1935, 1938, 1939, 1944, 1945, 1946, 1948, 1949, 1953, 1957, 1960, 1961, 1962, 1963, 1965, 1967, 1968, 1972, 1981, 1982, 1984, 1985, 1986, 1996, 1997, 2001, 2002, 2006, 2009]

