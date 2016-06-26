import pandas as pd
import pickle
from utilityF import *
from station_module import *
from os import environ as EV
phaseList = ['El Nino','La Nina','Neutral Positive', 'All Years','Neutral Negative']
#use these series to hold the data for El Nino and La Nina individually in order to find diff later
removedStations = []             
dataDiffE = pd.Series()
dataDiffL = pd.Series()
#0, .5 inch, 1 inch, 2 inch, 3 inch
thresholdList = [0, 127, 254]#,762]
for thresh in thresholdList:
    dictDiff = {}
    meanScale = 65
    stdScale = 25
    for phase in phaseList:
        
        if phase == 'El Nino': 
            NIPAdata = (phase, [3, 4, 5, 6],
                        [1926, 1931, 1941, 1942, 1958, 1966, 1973,
                        1983, 1992, 1995, 1998, 2010])
        if phase == 'La Nina':
             NIPAdata = (phase, [3, 4, 5, 6], [1925, 1934, 1943,
                    1950, 1951, 1955, 1956, 1957, 1971, 1972, 1974,
                    1975, 1976, 1989, 1999, 2000, 2008]) 
        if phase == 'Neutral Positive':
            NIPAdata = (phase, [3, 4, 5, 6], [1924, 1927,
                    1928, 1930, 1932, 1936, 1937, 1940, 1947, 1952, 1954,
                    1959, 1964, 1969, 1970, 1977, 1978, 1979, 1980, 1988,
                    1990, 1991, 1993, 1994, 2004, 2005, 2007])
        if phase == 'Neutral Negative':
             NIPAdata = (phase, [3, 4, 5, 6], [1921, 1922, 1923,
                        1929, 1933, 1935, 1938, 1939, 1944, 1945, 1946,
                        1948, 1949, 1953, 1960, 1961, 1962, 1963, 1965,
                        1967, 1968, 1981, 1982, 1984, 1985, 1986, 1996,
                        1997, 2001, 2002, 2006, 2009])
        if phase == 'All Years':
            NIPAdata = (phase, [3, 4, 5, 6], np.arange(1921,2010))
            
        station_list = {}
        import csv
        reader = csv.reader(open('hcn_stations.csv','rb'))
        ss = dict(reader)
        count = 0
        for sid in ss:
            if len(ss[sid].split()) == 3:
                div = ss[sid].split()[0][2:] + ' ' + ss[sid].split()[1][0:-2]
                code = ss[sid].split()[2][1:]
            else:
                div = ss[sid].split()[0][2:-2]
                code = ss[sid].split()[1][1:-2]
            ss[sid] = (div,code)
        #only takes one station, remove id to take all stations    
        station_list = ss
        #keep track of division you have done calls for
        divisions = []

        #initialize data series

        dataM = pd.Series()
        dataSTD = pd.Series()
        for id in station_list:
            try:
                #print id
                station = stationDaily('PRCP', id, NIPAdata)
                station.threshold([thresh])
            #use the ~ which is nan to get the ones that aren't nan, and sum to get total # of events
                events_avg = (~np.isnan(station.Tdata[str(thresh)])).sum().mean()
                events_std = (~np.isnan(station.Tdata[str(thresh)])).sum().std()
                division = station_list[id][0]
                dataM[division] = events_avg
                dataSTD[division] = events_std
                if(phase == 'El Nino'):
                    dataDiffE[division] = events_avg
                elif(phase == 'La Nina'):
                    dataDiffL[division] = events_avg
                    
            except KeyError:
                print ("Removed station " + id )
                removedStations.append(id)
            except ValueError:
                print ("Removed station " + id )
                removedStations.append(id)  
        #_set the path to the shapefile
        dictDiff[phase] = dataM 
    fp = EV['SHPFILES'] + \
                '/CONUS_CLIMATE_DIVISIONS/GIS_OFFICIAL_CLIM_DIVISIONS'
    
    dataDiff1 = dictDiff['El Nino'] - dictDiff['All Years']
    fig, ax, m = valueMap(dataDiff1, fp, 5.0)
    ax.set_title('Mean Difference of El Nino Events over ' + str(thresh/254.0) + ' inches');
    fpDiff = EV['HOME'] + '/Desktop/El Nino' + str(thresh) + '_Diff'
    plt.savefig(fpDiff)    
    
    dataDiff2 = dictDiff['La Nina'] - dictDiff['All Years']
    fig, ax, m = valueMap(dataDiff2, fp,5.0)
    ax.set_title('Mean Difference of La Nina Events over ' + str(thresh/254.0) + ' inches');
    fpDiff = EV['HOME'] + '/Desktop/La Nina' + str(thresh) + '_Diff'
    plt.savefig(fpDiff)
    
    dataDiff3 = dictDiff['Neutral Negative'] - dictDiff['All Years']
    fig, ax, m = valueMap(dataDiff3, fp,5.0)
    ax.set_title('Mean Difference of Neutral Negative Events over ' + str(thresh/254.0) + ' inches');
    fpDiff = EV['HOME'] + '/Desktop/Neutral Negative' + str(thresh) + '_Diff'
    plt.savefig(fpDiff)
    
    dataDiff4 = dictDiff['Neutral Positive'] - dictDiff['All Years']
    fig, ax, m = valueMap(dataDiff4, fp,5.0)
    ax.set_title('Mean Difference of Neutral Positive Events over ' + str(thresh/254.0) + ' inches');
    fpDiff = EV['HOME'] + '/Desktop/Neutral Positive' + str(thresh) + '_Diff'
    plt.savefig(fpDiff)
