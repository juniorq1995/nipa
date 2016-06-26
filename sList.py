import pandas as pd
import pickle
from utilityF import *
from station_module import *
#from test_point import *
from os import environ as EV
var = 'PRCP'
year_lim = (1945,1994)
lat = (30, 32.5)
lon = (-102, -97)
phaseList = ['All Years']#['El Nino','La Nina','Neutral Positive','Neutral Negative', 'All Years']
#use these series to hold the data for El Nino and La Nina individually in order to find diff later
removedStations = []             
dataDiffE = pd.Series()
dataDiffL = pd.Series()
for phase in phaseList:
    print phase
    #0, .5 inch, 1 inch, 2 inch, 3 inch
    thresholdList = [0,127,254]#,508]#,762]
    for thresh in thresholdList:
        print thresh
        
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
             NIPAdata(phase, [3, 4, 5, 6], [1921, 1922, 1923,
                        1929, 1933, 1935, 1938, 1939, 1944, 1945, 1946,
                        1948, 1949, 1953, 1960, 1961, 1962, 1963, 1965,
                        1967, 1968, 1981, 1982, 1984, 1985, 1986, 1996,
                        1997, 2001, 2002, 2006, 2009])
        if phase == 'All Years':
            NIPAdata = (phase, [3, 4, 5, 6], np.arange(1921,2010))
            
        station_info = extract_stations(var, year_lim,lat,lon, HCN = True)
        #obj = stationDaily(var, station_info.keys()[0], NIPAdata)
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
        station_list['USC00013511'] = ss['USC00013511']
        #USC00013511
        #keep track of division you have done calls for
        divisions = []

        #initialize data series

        dataM = pd.Series()
        dataSTD = pd.Series()
        for id in station_list:
            try:
                print id
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
        fp = EV['SHPFILES'] + \
                '/CONUS_CLIMATE_DIVISIONS/GIS_OFFICIAL_CLIM_DIVISIONS'

        #data is a pandas series that contains the division of each station paired with the mean precip
       
        fig, ax, m = valueMap(dataM, fp)
        ax.set_title('Average Number of Events over ' + str(thresh/254.0) + ' inches during a ' + phase + ' phase' );
        fpM = EV['HOME'] + '/Desktop/' + phase + str(thresh) + '_Mean'
        plt.savefig(fpM)


        fig, ax, m = valueMap(dataSTD, fp)
        ax.set_title('Standard Deviation of Events over ' + str(thresh/254.0) + ' inches during a ' + phase + ' phase' );
        fpSTD = EV['HOME'] + '/Desktop/' + phase + str(thresh) + '_STD'
        plt.savefig(fpSTD)
        
        if(phase == 'La Nina'):
            dataDiff = pd.Series()
            for div in dataDiffE.index:
                dataDiff[div] = dataDiffE[div]-dataDiffL[div]
            fig, ax, m = valueMap(dataSTD, fp)
            ax.set_title('Standard Deviation of Events over ' + str(thresh/254.0) + ' inches during a ' + phase + ' phase' );
            fpSTD = EV['HOME'] + '/Desktop/' + phase + str(thresh) + '_STD'
            plt.savefig(fpSTD)     
#implement difference map functions        


        #insert print statements as needed to see what the loop is doing. What will change is how 'events_avg' is calculated
        #this scrip does the number of events over 100 tenths of a mm, but you could do anything

        #To mess around with how to calculate something, just load one station ID into a station daily object and mess with it
        #until you get the statistic you want, then insert the calculation into the loop.
        #contains the dict we need to create maps





        #once you generate a full data series, then feed it to the value map and add a descriptive title. Difference maps are useful tools-i.e. to calculate number of events over zero in El Nino as a data series , number of events in La Nina as a data series, and then create a new series by subtracting one from the other.

        # It takes a while to loop over all the stations and create the station objects. So you could initialize a whole bunch of 'data' series, and put them into a dict. Then, in the loop, every time you pass through a station object, you can calculate mean # events over 0, mean # events over i inch, std of events over 0 and put them in their respective data series. That way you don't have to loop through for every statistic, only for each phase  

