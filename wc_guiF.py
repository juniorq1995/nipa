#! /Users/jquintero/anaconda/bin/python
import Tkinter as tk
import tkMessageBox as tkM
import matplotlib as mpl
import climdiv_data as cd
import atmos_ocean_data as aod
from numpy import isnan, sum, zeros
from extremes import bootstrp
import os, math, time
import numpy as np
from os import environ as EV
from matplotlib import cm ,rcParams, pyplot as plt
import station_module as sm
import dw as dw
from scipy.stats import genextreme as gev
from scipy.stats import gamma
from tkFileDialog import askopenfilename as pickfile


'''
display stationID button
display thresholds
add threshold
display std_0
display mean_0
display gamma
display gev
for each phase:
    display Data button
    display threshold Data button
'''
class dw_gui(object):

    def mean_0(self,stations):
        print "\nMean\n"
        for station in stations:
		    print station.phase
		    print np.sum(~np.isnan(station.Tdata['0'])).mean()
        return

    def std_0(self,stations):
        print "\nStandard Deviation\n"
        for station in stations:
		    print station.phase
		    print np.sum(~np.isnan(station.Tdata['0'])).std()
        return

    def gev_0(self,stations):
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

    def gamma_0(self,stations):
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

    def addThreshold(self):

        thresh = thresh.split(',', 1)
        for i, item in enumerate(thresh):
            thresh[i] = int(item)
        for item in self.thresholds:
            thresh.append(item)
        ref.threshold(thresh)
        ref.otherstatistics()

    def grabThresholds(self):
        self.threshVar = self.threshVar.get().split(",")
        for item in self.threshVar:
            self.thresholds.append(int(item))

    def grabYears(self):
        self.EN_years = []
        self.year1 = self.year1.get("1.0",'end-1c').split(",")
        for item in self.year1:
            self.EN_years.append(int(item))

        self.NP_years = []
        self.year2 = self.year2.get("1.0",'end-1c').split(",")
        for item in self.year2:
            self.NP_years.append(int(item))

        self.NN_years = []
        self.year3 = self.year3.get("1.0",'end-1c').split(",")
        for item in self.year3:
            self.NN_years.append(int(item))

        self.LN_years = []
        self.year4 = self.year4.get("1.0",'end-1c').split(",")
        for item in self.year3:
            self.LN_years.append(int(item))

    def displayTDataTerminal(self, ref):
        # a dict where each key contains one pandas df
        print "\nThreshold Data"
        for key1 in ref.Tdata:
            print key1
            print ref.Tdata[key1]
        print "\n"

    def displayThresholdsTerminal(self):
        print "\nThresholds", ":", self.thresholds

    def displayDataTerminal(self, ref):
        #ref is the reference for phase data
        print "\nData"
        print ref.data + "\n"

    def pickStation(self):
        fileName = pickfile(multiple = False)
        self.stationID = fileName[-15:-4]

    def displayStationIDTerminal(self):
        print "\nStationID: " + self.stationID + "\n"

    def createPhaseList(self):
        for item in self.phases:
            if item.phase == 'El Nino':
                self.EN = item
                self.phaseList.append('EN')

            if item.phase == 'Neutral Positive':
                self.NP = item
                self.phaseList.append('NP')

            if item.phase == 'Neutral Negative':
                self.NN = item
                self.phaseList.append('NN')

            if item.phase == 'La Nina':
                self.LN = item
                self.phaseList.append('LN')

    def calculate(self):
        self.grabYears()
        NIPAdata = []

        if 'MAMJ'== self.sFiles.get():
            self.season = [3,4,5,6]
        elif 'DJFM' == self.sFiles.get():
            self.season = [12,1,2,3]
        else:
            tkM.showinfo("ERROR","Please choose a season")
            return

        if(self.CheckVar1.get() == 0 and self.CheckVar2.get() == 0 and self.CheckVar3.get() == 0 and self.CheckVar4.get() == 0):
            tkM.showinfo("ERROR","Please select a Phase")
            return

        if self.CheckVar1.get() == 1:
            if len(self.EN_years) == 0:
                tkM.showinfo("ERROR","Please upload or create a list of years for the El Nino Phase")
                return
            else:
                NIPAdata.append(('El Nino', self.season, self.EN_years))

        if self.CheckVar2.get() == 1:
            if len(self.NP_years) == 0:
                tkM.showinfo("ERROR","Please upload or create a list of years for the Neutral Positive Phase")
                return
            else:
                NIPAdata.append(('Neutral Positive', self.season, self.NP_years))

        if self.CheckVar3.get() == 1:
            if len(self.NN_years) == 0:
                tkM.showinfo("ERROR","Please upload or create a list of years for the Neutral Negative Phase")
                return
            else:
                NIPAdata.append(('Neutral Negative', self.season, self.NN_years))
        if self.CheckVar4.get() == 1:
            if len(self.LN_years) == 0:
                tkM.showinfo("ERROR","Please upload or create a list of years for the La Nina Phase")
                return
            else:
                NIPAdata.append(('La Nina', self.season, self.LN_years))
        self.phases = []
        self.grabThresholds()
        for data in NIPAdata:
            self.var = self.varFiles.get()
            station = sm.stationDaily(self.var, self.stationID, data)
            station.threshold(self.thresholds)
            station.otherstatistics()
            self.phases.append(station)

        self.createPhaseList()

        #kw calculations
        self.divisionVar = self.divisionVar.get()
        self.numberYearsVar = (int)(self.numberYearsVar.get())
        self.startYearVar = (int)(self.startYearVar.get())
        self.endYear = self.startYearVar + (self.numberYearsVar-1)
        self.noMoSSTVar = (int)(self.noMoSSTVar.get())
        self.noMoMEIVar = (int)(self.noMoMEIVar.get())
        self.noMoSLPVar = (int)(self.noMoSLPVar.get())
        self.mei_lagVar = (int)(self.mei_lagVar.get())
        self.sst_lagVar = (int)(self.sst_lagVar.get())
        self.slp_lagVar = (int)(self.slp_lagVar.get())

        months = {'MAM' : [3, 4, 5]}
        bounds = {'Texas-06' : [30, 32.5, -102, -97], \
                        'Texas-09': [28, 30, -101, -96],
        				'Northeast': [39, 41, -76.5, -75.5]}

        kwgroups = cd.create_kwgroups(    climdiv_months = months['MAM'], \
                                    sst_lag = self.sst_lagVar, n_mon_sst = self.noMoSSTVar, \
                                    mei_lag = self.mei_lagVar, n_mon_mei = self.noMoMEIVar, \
                                    slp_lag = self.slp_lagVar, n_mon_slp = self.noMoSLPVar, \
                                    climdiv_startyr = self.startYearVar, n_yrs = self.numberYearsVar)
        #season = 'MAM'
        mei, phaseind = cd.create_phase_index(**kwgroups['mei'])

        base_fp = EV['GHCND_HCN']

        year_list = np.arange(self.startYearVar, self.endYear + 1)

        lat = (bounds[self.divisionVar][0], bounds[self.divisionVar][1])
        lon = (bounds[self.divisionVar][2], bounds[self.divisionVar][3])

        year_lim = (year_list.min(), year_list.max())

        station_info = dw.extract_stations(var = self.var, years = year_lim,
                                            lat = lat, lon = lon)

    def __init__(self):
        self.thresholds = [0]
        self.phaseList = []

        app = tk.Tk()
        self.CheckVar1 = tk.IntVar()
        self.CheckVar2 = tk.IntVar()
        self.CheckVar3 = tk.IntVar()
        self.CheckVar4 = tk.IntVar()

        frameLeft = tk.Frame(app)
        frameRight = tk.Frame(app)
        frameLeft.pack(side = tk.LEFT)
        frameRight.pack(side = tk.LEFT,fill = tk.Y)

        frame1 = tk.Frame(frameLeft, bg = "#00ffff")
        frame1.pack(fill = tk.X)

        stationB = tk.Button(frame1, text = "Station", command = self.pickStation)
        stationB.pack(side = tk.LEFT)

        self.varFiles = tk.StringVar(app)
        self.varFiles.set(None)
        vfiles = ['PRCP', 'SNOW', 'TMAX', 'TMIN']
        varDropDown = tk.OptionMenu(frame1, self.varFiles, *vfiles)
        varDropDown.pack(side = tk.LEFT)

        #Seasons
        self.sFiles = tk.StringVar(app)
        self.sFiles.set(None)
        sfiles = ['MAMJ', 'DJFM','MAM', 'DJF']
        seasonDropDown = tk.OptionMenu(frame1, self.sFiles, *sfiles)
        seasonDropDown.pack(side = tk.LEFT)

        tk.Label(frame1, text="Thresholds").pack(side = tk.LEFT)
        self.threshVar = tk.StringVar(app)
        self.threshVar.set("127,254")
        threshEntry =  tk.Entry(frame1, textvariable = self.threshVar)
        threshEntry.pack(side = tk.LEFT)

        frame2 = tk.Frame(frameLeft, bg = "green")
        frame2.pack(fill = tk.X)

        C1 = tk.Checkbutton(frame2, text = "El Nino", variable = self.CheckVar1, onvalue = 1, offvalue = 0)

        C2 = tk.Checkbutton(frame2, text = "Neutral Positive", variable = self.CheckVar2, onvalue = 1, offvalue = 0)

        C3 = tk.Checkbutton(frame2, text = "Neutral Negative", variable = self.CheckVar3, onvalue = 1, offvalue = 0)

        C4 = tk.Checkbutton(frame2, text = "La Nina", variable = self.CheckVar4, onvalue = 1, offvalue = 0)

        C1.grid(row = 0,column = 0, sticky = tk.W)
        self.year1 = tk.Text(frame2, height = 2, width = 100)
        self.year1.insert(tk.INSERT,"1926,1931,1941,1942,1958,1966,1973,1983,1992,1995,1998,2010")
        self.year1.grid(row = 0, column = 1, sticky = tk.W)

        C2.grid(row = 1,column = 0, sticky = tk.W)
        self.year2 = tk.Text(frame2, height = 2, width = 100)
        self.year2.insert(tk.INSERT,"1925, 1934, 1943,1950, 1951, 1955, 1956, 1957, 1971, 1972, 1974,1975, 1976, 1989, 1999, 2000, 2008")
        self.year2.grid(row = 1, column = 1, sticky = tk.W)

        C3.grid(row = 2,column = 0, sticky = tk.W)
        self.year3 = tk.Text(frame2, height = 2, width = 100)
        yearL1 = "1924, 1927,1928, 1930, 1932, 1936, 1937, 1940, 1947, 1952, 1954,\
                    1959, 1964, 1969, 1970, 1977, 1978, 1979, 1980, 1988,\
                    1990, 1991, 1993, 1994, 2004, 2005, 2007"
        yearL1 = yearL1.replace(" ", "")
        self.year3.insert(tk.INSERT,yearL1)
        self.year3.grid(row = 2, column = 1, sticky = tk.W)

        C4.grid(row = 3,column = 0, sticky = tk.W)
        self.year4 = tk.Text(frame2, height = 2, width = 100)
        yearL2 = "1921, 1922, 1923,\
                        1929, 1933, 1935, 1938, 1939, 1944, 1945, 1946,\
                        1948, 1949, 1953, 1960, 1961, 1962, 1963, 1965,\
                        1967, 1968, 1981, 1982, 1984, 1985, 1986, 1996,\
                        1997, 2001, 2002, 2006, 2009"
        yearL2 =yearL2.replace(" ", "")
        self.year4.insert(tk.INSERT,yearL2)
        self.year4.grid(row = 3, column = 1, sticky = tk.W)

        frame3 = tk.Frame(frameLeft, bg = "black")
        frame3.pack(fill = tk.X)

        tk.Label(frame3, text="Division").grid(row=0,column=0, sticky=tk.E)
        self.divisionVar = tk.StringVar(app)
        self.divisionVar.set("Northeast")
        division =  tk.Entry(frame3, textvariable = self.divisionVar)
        division.grid(row = 0, column = 1, sticky = tk.W)

        tk.Label(frame3, text="Number of Years").grid(row=1,column=0, sticky=tk.E)
        self.numberYearsVar = tk.StringVar(app)
        self.numberYearsVar.set("50")
        numberYears =  tk.Entry(frame3, textvariable = self.numberYearsVar)
        numberYears.grid(row = 1, column = 1, sticky = tk.W)

        tk.Label(frame3, text="Start Year").grid(row=2,column=0, sticky=tk.E)
        self.startYearVar = tk.StringVar(app)
        self.startYearVar.set("1945")
        startYear =  tk.Entry(frame3, textvariable = self.startYearVar)
        startYear.grid(row = 2, column = 1, sticky = tk.W)

        tk.Label(frame3, text="Number of Months SST").grid(row=3,column=0, sticky=tk.E)
        self.noMoSSTVar = tk.StringVar(app)
        self.noMoSSTVar.set("3")
        noMoSST =  tk.Entry(frame3, textvariable = self.noMoSSTVar)
        noMoSST.grid(row = 3, column = 1, sticky = tk.W)

        tk.Label(frame3, text="Number of Months MEI").grid(row=4,column=0, sticky=tk.E)
        self.noMoMEIVar = tk.StringVar(app)
        self.noMoMEIVar.set("3")
        noMoMEI =  tk.Entry(frame3, textvariable = self.noMoMEIVar)
        noMoMEI.grid(row = 4, column = 1, sticky = tk.W)

        tk.Label(frame3, text="Number of Months SLP").grid(row=5,column=0, sticky=tk.E)
        self.noMoSLPVar = tk.StringVar(app)
        self.noMoSLPVar.set("2")
        noMoSLP =  tk.Entry(frame3, textvariable = self.noMoSLPVar)
        noMoSLP.grid(row = 5, column = 1, sticky = tk.W)

        tk.Label(frame3, text="MEI Lag").grid(row=6,column=0, sticky=tk.E)
        self.mei_lagVar = tk.StringVar(app)
        self.mei_lagVar.set("3")
        mei_lag =  tk.Entry(frame3, textvariable = self.mei_lagVar)
        mei_lag.grid(row = 6, column = 1, sticky = tk.W)

        tk.Label(frame3, text="SST Lag").grid(row=7,column=0, sticky=tk.E)
        self.sst_lagVar = tk.StringVar(app)
        self.sst_lagVar.set("3")
        sst_lag =  tk.Entry(frame3, textvariable = self.sst_lagVar)
        sst_lag.grid(row = 7, column = 1, sticky = tk.W)

        tk.Label(frame3, text="SLP Lag").grid(row=8,column=0, sticky=tk.E)
        self.slp_lagVar = tk.StringVar(app)
        self.slp_lagVar.set("2")
        slp_lag =  tk.Entry(frame3, textvariable = self.slp_lagVar)
        slp_lag.grid(row = 8, column = 1, sticky = tk.W)


        tk.Label(frameRight, text = "Display Options").grid(column = 0, row = 0)

        button_mean1_11 = tk.Button(frameRight, text = "Display Mean", width = 10, command = lambda:self.mean_0(self.phases) )
        button_mean1_11.grid(row = 1, column = 0)

        button_std1_11 = tk.Button(frameRight, text = "Display STD", width = 10, command = lambda:self.std_0(self.phases))
        button_std1_11.grid(row = 2, column = 0)

        button_gev1_11 = tk.Button(frameRight, text = "Display Gev_0", width = 10, command = lambda:self.gev_0(self.phases))
        button_gev1_11.grid(row = 3, column = 0)

        button_gamma1_11 = tk.Button(frameRight, text = "Display Gamma_0", command = lambda:self.gamma_0(self.phases))
        button_gamma1_11.grid(row = 4, column = 0)

        button1_4 = tk.Button(frameRight, text = "Display Station ID", command = self.displayStationIDTerminal)
        button1_4.grid(row = 5, column = 0)



        dataFrame = tk.Frame(frameRight)
        dataFrame.grid(row = 6, column = 0)

        button1 = tk.Button(dataFrame, text = "Display EN Data", command = lambda: self.displayDataTerminal(self.EN))
        button1.grid(row = 0, column = 0)

        button1_2 = tk.Button(dataFrame, text = "Display EN Threshold Data", command = lambda: self.displayTDataTerminal(self.EN))
        button1_2.grid(row = 0, column = 1)

        button2 = tk.Button(dataFrame, text = "Display NP Data", command = lambda: self.displayDataTerminal(self.NP))
        button2.grid(row = 1, column = 0)

        button2_1 = tk.Button(dataFrame, text = "Display NP Threshold Data", command = lambda: self.displayTDataTerminal(self.NP))
        button2_1.grid(row = 1, column = 1)

        button3 = tk.Button(dataFrame, text = "Display NN Data", command = lambda: self.displayDataTerminal(self.NN))
        button3.grid(row = 2, column = 0)

        button3_1 = tk.Button(dataFrame, text = "Display NN Threshold Data", command = lambda: self.displayTDataTerminal(self.NN))
        button3_1.grid(row = 2, column = 1)

        button4 = tk.Button(dataFrame, text = "Display LN Data", command = lambda: self.displayDataTerminal(self.LN))
        button4.grid(row = 3, column = 0)

        button4_1 = tk.Button(dataFrame, text = "Display LN Threshold Data", command = lambda: self.displayTDataTerminal(self.LN))
        button4_1.grid(row = 3, column = 1)



        button1_9 = tk.Button(frameRight, text = "Display Thresholds", command = self.displayThresholdsTerminal)
        button1_9.grid(row = 7, column = 0)


        entry1_10 = tk.Entry(frameRight)
        button1_10 = tk.Button(frameRight, text = "Add Threshold", width = 10, command = self.addThreshold)
        entry1_10.grid(row = 9, column = 0)
        button1_10.grid(row = 8, column = 0)



        submit = tk.Button(frame3, text = "Submit", command  = self.calculate)
        submit.grid(row = 9,column = 0,sticky = tk.E)

        app.mainloop()



if __name__ == '__main__':
    gui = dw_gui()
#2 more things
# need bounds dict and separate months entry for kwgroups(select 3 months instead of 4!!!)
# when you hit submit a separate window pops up with the options, or hav buttons on same window
#from extremes import bootstrp

#  File "/Users/jquintero/nipa/extremes.py", line 2, in <module>
#    from statsmodels.distributions.empirical_distribution import ECDF
#ImportError: No module named statsmodels.distributions.empirical_distribution

#only one threshold entry
#one station button
#text field  for each year
#one variable dropdown
#one season dropdown
#move each checkbox next to year text entry
