#! /Users/jquintero/anaconda/bin/python
import Tkinter as tk
import tkMessageBox as tkM
import station_module as sm

class dw_gui(object):
    def displayPhaseTerminal(self, ref):
        print "\nPhase", ":", ref.phase

    def displayStatsTerminal(self, ref):
        print "\nMean"
        for key1 in ref.mean:
            print key1
            for key2 in ref.mean[key1]:
                print key2, ":", ref.mean[key1][key2]

        print "\nStandard Deviation"
        for key1 in ref.std:
            print key1
            for key2 in ref.std[key1]:
                print key2, ":", ref.std[key1][key2]

        #json.dump(ref.std, open(ref.phase + "std.txt", 'w'))
        #json.dump(ref.mean, open(ref.phase + "mean.txt", 'w'))

    def displayYearTerminal(self, ref):
        print "\nYears"
        for item in ref.years:
            print item
        #json.dump(ref.years, open(ref.phase + "years.txt", 'w'))

    def displaySeasonTerminal(self, ref):
        tempSeason = ''
        if ref.months == [12,1,2,3]:
            tempSeason = 'DJFM'
        elif ref.months == [3,4,5,6]:
            tempSeason = 'MAMJ'
        print "\nSeason", ":", tempSeason
        #tkM.showinfo("Season", tempSeason)

    def displayTDataTerminal(self, ref):
        # a dict where each key contains one pandas df
        print "\nThreshold Data"
        for key1 in ref.Tdata:
            print key1
            print key2

    def displayThresholdsTerminal(self, ref):
        print "\nThresholds", ":", ref.thresholds
        #tkM.showinfo("Thresholds", ref.thresholds)

    def displayDataTerminal(self, ref):
        print "\nData"
        print ref.data
        #ref.data.to_excel("data.xlsx")

    def displayStationTerminal(self, ref):
        print "\nStation ID", ":", ref.stationID
        #tkM.showinfo("Station ID", ref.stationID)

    def addThreshold(self, thresh, ref):
        thresh = thresh.split(',', 1)
        for i, item in enumerate(thresh):
            thresh[i] = int(item)
        for item in self.thresholds:
            thresh.append(item)
        ref.threshold(thresh)
        ref.otherstatistics()

    def pickStation(self):
        ps = tk.Tk()
        ps.title("Pick the Station ID for this phase")
        tk.Label(ps, text = "The format should be: 'USC00410832'(no spacing)").grid(row = 0, column = 2)

        bs1 = tk.Button(ps, text = "Get Station ID from Filename", command = lambda:self.pickStationUpload(ps))
        fs1 = tk.Frame(ps)
        es1 = tk.Entry(fs1).pack(side = tk.RIGHT)
        bs2 = tk.Button(fs1, text = "Type in Station ID", command = lambda:self.typeStation(es1.get(), ps)).pack(side = tk.LEFT)
        fs1.grid(row = 1, column = 2)
        bs1.grid(row = 1, column = 0)
        ps.mainloop()

    def typeStation(self, station_string, caller):
        caller.destroy()
        self.stationID = station_string[0:-1]

    def pickStationUpload(self, caller):
        fileName = pickfile(multiple = False)
        caller.destroy()
        self.stationID = fileName[-15:-4]

    def pickThreshold(self):
        pt = tk.Tk()
        pt.title("Pick the threshold(s) for this phase")
        tk.Label(pt, text = "The format should be: 254,508, ...(no spacing) units are in mm").grid(row = 0, column = 2)

        ptB = tk.Button(pt, text = "Upload Threshold List from File", command = lambda:self.pickThresholdUpload(pt))
        ptB2 = tk.Button(pt, text = "Create Threshold List", command = lambda:self.pickThresholdCreate(textV1.get("1.0",'end-1c').split(","), pt))
        textV1 = tk.Text(pt)
        textV1.grid(row = 1, column = 2)
        ptB.grid(row = 1, column = 0)
        ptB2.grid(row = 2, column = 2)

    def pickThresholdUpload(self, caller):
        fileName = pickfile(multiple = False)
        fo = open(fileName, "r")
        text = fo.read()
        temp = text[0:-1].split(",")
        for item in temp:
            threshold_list.append(int(intem))
        fo.close()
        caller.destroy()
        self.thresholds = temp

    def pickThresholdCreate(self, tList, caller):
        for i, item in enumerate(tList):
            tList[i] = int(item)
        caller.destroy()
        self.thresholds = tList

    def pickYear(self, phaseYear):
        py = tk.Tk()
        py.title("Pick the Year(s) for this phase")
        tk.Label(py, text = "The format should be: 2000,2001, ...(no spacing)").grid(row = 0, column = 2)

        pyB = tk.Button(py, text = "Upload Year List from File", command = lambda:self.pickYearUpload(phaseYear, py))
        pyB2 = tk.Button(py, text = "Create Year List", command = lambda:self.pickYearCreate(phaseYear, textV3.get("1.0",'end-1c').split(","), py))
        textV3 = tk.Text(py)
        textV3.grid(row = 1, column = 2)
        pyB.grid(row = 1, column = 0)
        pyB2.grid(row = 2, column = 2)

    def pickYearUpload(self, phaseYear, caller):
        fileName = pickfile(multiple = False)
        fo = open(fileName, "r")
        temp = fo.read();
        temp = temp[0:-1].split(",")
        for i, item in enumerate(temp):
            temp[i] = int(item)
        fo.close()
        caller.destroy()
        self.assignPhaseYear(temp, phaseYear)

    def pickYearCreate(self, phaseYear, yList, caller):
        for i, item in enumerate(yList):
            yList[i] = int(item)
        caller.destroy()
        self.assignPhaseYear(yList, phaseYear)

    def assignPhaseYear(self, ylist, yphase):
        if yphase == 'EN':
            self.EN_years = ylist
        if yphase == 'NP':
            self.NP_years = ylist
        if yphase == 'NN':
            self.NN_years = ylist
        if yphase == 'LN':
            self.LN_years = ylist

    def interact(self, caller):
        #add 4 buttons to use the 4 methods at the  top
        caller.destroy()
        play = tk.Tk()
        #play.geometry("500x100")
        play.title("Interaction")

        for i in self.phaseList:
            if i == 'EN':
                tk.Label(play,text = "El Nino").grid(row = 0, column = 0)
                button1_2 = tk.Button(play, text = "Months", width = 20, command = lambda:self.displaySeasonTerminal(self.EN))
                button1_2.grid(row = 1, column = 0)

                button1_3 = tk.Button(play, text = "Years", width = 20, command = lambda:self.displayYearTerminal(self.EN))
                button1_3.grid(row = 2, column = 0)

                button1_4 = tk.Button(play, text = "Station ID", width = 20, command = lambda:self.displayStationTerminal(self.EN))
                button1_4.grid(row = 3, column = 0)

                button1_5 = tk.Button(play, text = "Mean/Standard Deviation", width = 20, command = lambda:self.displayStatsTerminal(self.EN))
                button1_5.grid(row = 4, column = 0)

                button1_6 = tk.Button(play, text = "Phase", width = 20, command = lambda:self.displayPhaseTerminal(self.EN))
                button1_6.grid(row = 5, column = 0)

                button1_7 = tk.Button(play, text = "Data", width = 20, command = lambda:self.displayDataTerminal(self.EN))
                button1_7.grid(row = 6, column = 0)

                button1_8 = tk.Button(play, text = "Threshold Data", width = 20, command = lambda:self.displayTDataTerminal(self.EN))
                button1_8.grid(row = 7, column = 0)

                button1_9 = tk.Button(play, text = "Thresholds", width = 20, command = lambda:self.displayThresholdsTerminal(self.EN))
                button1_9.grid(row = 8, column = 0)

                #thresh_frame1_10 = tk.Frame(play).grid(row = 9, column = 0)

                entry1_10 = tk.Entry(play)
                button1_10 = tk.Button(play, text = "Add Threshold", width = 10, command = lambda:self.addThreshold(entry1_10.get(), self.EN))
                entry1_10.grid(row = 9, column = 0)
                button1_10.grid(row = 9, column = 1)

            if i == 'NP':
                tk.Label(play,text = "Neutral Positive").grid(row = 0, column = 1)
                button2_2 = tk.Button(play, text = "Months", width = 10, command = lambda:self.displaySeasonTerminal(self.NP))
                button2_2.grid(row = 1, column = 1)

                button2_3 = tk.Button(play, text = "Years", width = 10, command = lambda:self.displayYearTerminal(self.NP))
                button2_3.grid(row = 2, column = 1)

                button2_4 = tk.Button(play, text = "Station ID", width = 10, command = lambda:self.displayStationTerminal(self.NP))
                button2_4.grid(row = 3, column = 1)

                button2_5 = tk.Button(play, text="Mean/Standard Deviation", width=10, command=lambda:self.displayStatsTerminal(self.NP))
                button2_5.grid(row = 4, column = 1)

                button2_6 = tk.Button(play, text="Phase", width=10, command=lambda:self.displayPhaseTerminal(self.NP))
                button2_6.grid(row = 5, column = 1)

                button2_7 = tk.Button(play, text="Data", width=10, command=lambda:self.displayDataTerminal(self.NP))
                button2_7.grid(row = 6, column = 1)

                button2_8 = tk.Button(play, text="Threshold Data", width=10, command=lambda:self.displayTDataTerminal(self.NP))
                button2_8.grid(row = 7, column = 1)

                button2_9 = tk.Button(play, text = "Thresholds", width = 10, command = lambda:self.displayThresholdsTerminal(self.NP))
                button2_9.grid(row = 8, column = 1)

                thresh_frame2_10 = tk.Frame(play).grid(row = 9, column = 1)

                entry2_10 = tk.Entry(thresh_frame2_10).grid(row = 0, column = 0)#pack(side = tk.LEFT)

                button2_10 = tk.Button(thresh_frame2_10, text = "Add Threshold", width = 10, command = lambda:self.addThreshold(int(entry2_10.get()), self.NP)).grid(row = 0, column = 1)#pack(side = tk.RIGHT)

            if i == 'NN':
                tk.Label(play,text = "Neutral Negative").grid(row = 0, column = 2)
                button3_2 = tk.Button(play, text = "Months", width = 10, command = lambda:self.displaySeasonTerminal(self.NN))
                button3_2.grid(row = 1, column = 2)

                button3_3 = tk.Button(play, text = "Years", width = 10, command = lambda:self.displayYearTerminal(self.NN))
                button3_3.grid(row = 2, column = 2)

                button3_4 = tk.Button(play, text = "Station ID", width = 10, command = lambda:self.displayStationTerminal(self.NN))
                button3_4.grid(row = 3, column = 2)

                button3_5 = tk.Button(play, text = "Mean/Standard Deviation", width = 10, command = lambda:self.displayStatsTerminal(self.NN))
                button3_5.grid(row = 4, column = 2)

                button3_6 = tk.Button(play, text = "Phase", width = 10, command = lambda:self.displayPhaseTerminal(self.NN))
                button3_6.grid(row = 5, column = 2)

                button3_7 = tk.Button(play, text = "Data", width = 10, command = lambda:self.displayDataTerminal(self.NN))
                button3_7.grid(row = 6, column = 2)

                button3_8 = tk.Button(play, text = "Threshold Data", width = 10, command = lambda:self.displayTDataTerminal(self.NN))
                button3_8.grid(row = 7, column = 2)

                button3_9 = tk.Button(play, text = "Thresholds", width = 10, command = lambda:self.displayThresholdsTerminal(self.NN))
                button3_9.grid(row = 8, column = 2)

                thresh_frame3_10 = tk.Frame(play).grid(row = 9, column = 2)

                entry3_10 = tk.Entry(thresh_frame3_10).pack(side = tk.LEFT)

                button3_10 = tk.Button(thresh_frame3_10, text = "Add Threshold", width = 10, command = lambda:self.addThreshold(int(entry3_10.get()), self.NN)).pack(side = tk.RIGHT)



            if i == 'LN':
                tk.Label(play,text = "La Nina").grid(row = 0, column = 3)
                button4_2 = tk.Button(play, text = "Months", width = 10, command = lambda:self.displaySeasonTerminal(self.LN))
                button4_2.grid(row = 1, column = 3)

                button4_3 = tk.Button(play, text = "Years", width = 10, command = lambda:self.displayYearTerminal(self.LN))
                button4_3.grid(row = 2, column = 3)

                button4_4 = tk.Button(play, text = "Station ID", width=10, command = lambda:self.displayStationTerminal(self.LN))
                button4_4.grid(row = 3, column = 3)

                button4_5 = tk.Button(play, text = "Mean/Standard Deviation", width = 10, command = lambda:self.displayStatsTerminal(self.LN))
                button4_5.grid(row = 4, column = 3)

                button4_6 = tk.Button(play, text = "Phase", width = 10, command = lambda:self.displayPhaseTerminal(self.LN))
                button4_6.grid(row = 5, column = 3)

                button4_7 = tk.Button(play, text = "Data", width = 10, command=lambda:self.displayDataTerminal(self.LN))
                button4_7.grid(row = 6, column = 3)

                button4_8 = tk.Button(play, text = "Threshold Data", width = 10, command = lambda:self.displayTDataTerminal(self.LN))
                button4_8.grid(row = 7, column = 3)

                button4_9 = tk.Button(play, text = "Thresholds", width = 10, command = lambda:self.displayThresholdsTerminal(self.LN))
                button4_9.grid(row = 8, column = 3)

                thresh_frame4_10 = tk.Frame(play).grid(row = 9, column = 1)

                entry4_10 = tk.Entry(thresh_frame4_10).pack(side = tk.LEFT)

                button4_10 = tk.Button(thresh_frame4_10, text = "Add Threshold", width = 10, command = lambda:self.addThreshold(int(entry4_10.get()), self.LN)).pack(side = tk.RIGHT)


        play.mainloop()

    def calculate(self):

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
        load = tk.Tk()
        load.title("Calculating...")
        load.geometry("500x100")
        tk.Label(load, text = "Please wait for the program to complete").pack()

        self.phases = []
        for data in NIPAdata:
            self.var = self.varFiles.get()
            station = sm.stationDaily(self.var, self.stationID, data)
            station.threshold(self.thresholds)
            station.otherstatistics()
            self.phases.append(station)

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


            self.interact(load)
            load.mainloop()

    def __init__(self):
        self.phaseList = []
        app = tk.Tk()
        app.title("Single Station Module Fields")
        self.CheckVar1 = tk.IntVar()
        self.CheckVar2 = tk.IntVar()
        self.CheckVar3 = tk.IntVar()
        self.CheckVar4 = tk.IntVar()
        C1 = tk.Checkbutton(app, text = "El Nino", variable = self.CheckVar1, onvalue = 1, offvalue = 0)

        C2 = tk.Checkbutton(app, text = "Neutral Positive", variable = self.CheckVar2, onvalue = 1, offvalue = 0)

        C3 = tk.Checkbutton(app, text = "Neutral Negative", variable = self.CheckVar3, onvalue = 1, offvalue = 0)

        C4 = tk.Checkbutton(app, text = "La Nina", variable = self.CheckVar4, onvalue = 1, offvalue = 0)

        C1.grid(row = 0,column = 0, sticky = tk.W)
        C2.grid(row = 1,column = 0, sticky = tk.W)
        C3.grid(row = 2,column = 0, sticky = tk.W)
        C4.grid(row = 3,column = 0, sticky = tk.W)

        #Buttons for threshold, stations, year --> opens another window with further options
        #dropdowns for variable and phase

        #El Nino options
        #variable
        self.varFiles = tk.StringVar(app)
        self.varFiles.set(None)
        vfiles = ['PRCP', 'SNOW', 'TMAX', 'TMIN']
        varDropDown = tk.OptionMenu(app, self.varFiles, *vfiles)
        varDropDown.grid(row = 0,column = 1, sticky = tk.W)

        #Seasons
        self.sFiles = tk.StringVar(app)
        self.sFiles.set(None)
        sfiles = ['MAMJ', 'DJFM']
        seasonDropDown = tk.OptionMenu(app, self.sFiles, *sfiles)
        seasonDropDown.grid(row = 0,column = 2, sticky = tk.W)

        station1B = tk.Button(app, text = "Station", command = self.pickStation)
        station1B.grid(row = 0,column = 3, sticky = tk.W)

        year1B = tk.Button(app, text = "Year(s)", command = lambda:self.pickYear('EN'))
        year1B.grid(row = 0,column = 4, sticky = tk.W)

        thresh1 = tk.Button(app, text = "Threshold(s)", command = self.pickThreshold)
        thresh1.grid(row = 0,column = 5, sticky = tk.W)

        #Neutral Positive options

        #variable
        varDropDown2 = tk.OptionMenu(app, self.varFiles, *vfiles)
        varDropDown2.grid(row = 1,column = 1, sticky = tk.W)

        #Seasons
        seasonDropDown2 = tk.OptionMenu(app, self.sFiles, *sfiles)
        seasonDropDown2.grid(row = 1,column = 2, sticky = tk.W)

        station2 = tk.Button(app, text = "Station", command = self.pickStation)
        station2.grid(row = 1,column = 3, sticky = tk.W)

        year2B = tk.Button(app, text = "Year(s)", command = lambda:self.pickYear('NP'))
        year2B.grid(row = 1,column = 4, sticky = tk.W)

        thresh2 = tk.Button(app, text = "Threshold(s)", command = self.pickThreshold)
        thresh2.grid(row = 1,column = 5, sticky = tk.W)


        #Neutral Negative Options

        #variable
        varDropDown3 = tk.OptionMenu(app, self.varFiles, *vfiles)
        varDropDown3.grid(row = 2,column = 1, sticky = tk.W)

        #Seasons
        seasonDropDown3 = tk.OptionMenu(app, self.sFiles, *sfiles)
        seasonDropDown3.grid(row = 2,column = 2, sticky = tk.W)

        station3B = tk.Button(app, text = "Station", command = self.pickStation)
        station3B.grid(row = 2,column = 3, sticky = tk.W)

        year3B = tk.Button(app, text = "Year(s)", command = lambda:self.pickYear('NN'))
        year3B.grid(row = 2,column = 4, sticky = tk.W)

        thresh3 = tk.Button(app, text = "Threshold(s)", command = self.pickThreshold)
        thresh3.grid(row = 2,column = 5, sticky = tk.W)

        #La Nina

        #variable
        varDropDown4 = tk.OptionMenu(app, self.varFiles, *vfiles)
        varDropDown4.grid(row = 3,column = 1, sticky = tk.W)

        #Seasons
        seasonDropDown4 = tk.OptionMenu(app, self.sFiles, *sfiles)
        seasonDropDown4.grid(row = 3,column = 2, sticky = tk.W)

        station4B = tk.Button(app, text="Station", command = self.pickStation)
        station4B.grid(row = 3,column = 3, sticky = tk.W)

        year4B = tk.Button(app, text = "Year(s)", command = lambda:self.pickYear('LN'))
        year4B.grid(row = 3,column = 4, sticky = tk.W)

        thresh4 = tk.Button(app, text = "Threshold(s)", command = self.pickThreshold)
        thresh4.grid(row = 3,column = 5, sticky = tk.W)

        tk.Label(app, text="Division").grid(row=4,column=0, sticky=tk.E)

        division =  tk.Entry(app)
        division.grid(row = 4, column = 1, sticky = tk.W)
        tk.Label(app, text="Number of Years").grid(row=5,column=0, sticky=tk.E)

        numberYears =  tk.Entry(app)
        numberYears.grid(row = 5, column = 1, sticky = tk.W)

        tk.Label(app, text="Start Year").grid(row=6,column=0, sticky=tk.E)

        startYear =  tk.Entry(app)
        startYear.grid(row = 6, column = 1, sticky = tk.W)

        tk.Label(app, text="Number of Months SST").grid(row=7,column=0, sticky=tk.E)

        noMoSST =  tk.Entry(app)
        noMoSST.grid(row = 7, column = 1, sticky = tk.W)

        tk.Label(app, text="Number of Months MEI").grid(row=8,column=0, sticky=tk.E)

        noMoMEI =  tk.Entry(app)
        noMoMEI.grid(row = 8, column = 1, sticky = tk.W)

        tk.Label(app, text="Number of Months SLP").grid(row=9,column=0, sticky=tk.E)

        noMoSLP =  tk.Entry(app)
        noMoSLP.grid(row = 9, column = 1, sticky = tk.W)

        tk.Label(app, text="MEI Log").grid(row=10,column=0, sticky=tk.E)

        mei_log =  tk.Entry(app)
        mei_log.grid(row = 10, column = 1, sticky = tk.W)

        tk.Label(app, text="SST Log").grid(row=11,column=0, sticky=tk.E)

        sst_log =  tk.Entry(app)
        sst_log.grid(row = 11, column = 1, sticky = tk.W)

        tk.Label(app, text="SLP Log").grid(row=12,column=0, sticky=tk.E)

        slp_log =  tk.Entry(app)
        slp_log.grid(row = 12, column = 1, sticky = tk.W)

        submit = tk.Button(app, text = "Submit", command = self.calculate)
        submit.grid(row = 12,column = 5,sticky = tk.E)

        app.mainloop()

if __name__ == '__main__':
    gui = dw_gui()
#2 more things
# need bounds dict and separate months entry for kwgroups(select 3 months instead of 4!!!)
# when you hit submit a separate window pops up with the options, or hav buttons on same window
