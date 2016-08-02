from os import listdir, environ as EV
from matplotlib import cm, pyplot as plt
from climdiv_data import *
from nipaV2 import *
import Tkinter as tk

class nipa_guiF(object):

    def calculate(self):
        #_these are the possible options for running the NIPA module
        #phases = ['allyears', 'elnino', 'lanina', 'neutpos', 'neutneg']
        #seasons = ['MAM', 'JJA', 'SON', 'DJF']
        self.months = {'MAM':[3, 4, 5], 'JJA' : [6, 7, 8],
                  'SON' : [9, 10, 11], 'DJF' :[12, 13, 14]}

        #_these are the parameters that need to be set by the user
        #lag = 3
        #season = 'MAM'
        #phase = 'lanina'
        #div = 'New Mexico-06'
        #climdiv_startyr = 1921
        #n_yrs = 90
        self.seasonVar = self.months[self.seasonVar.get()]
        self.lagVar = self.lagVar.get()
        self.division = self.divisionVar1.get() + "-" + self.divisionVar2.get()
        self.startYearVar = int(self.startYearVar.get("1.0",'end-1c'))
        self.numberYears = int(self.numberYearsVar.get("1.0",'end-1c'))
        self.phaseVar = self.phaseVar.get()

        kwgroups = create_kwgroups(climdiv_months = self.seasonVar, sst_lag = self.lagVar,
                                    mei_lag = self.lagVar, debug = True, climdiv_startyr = self.startYearVar,
                                    n_yrs = self.numberYears)

        alldivDF, sst, mei, phaseind = get_data(kwgroups)

        # posind = phaseind['elnino'] | phaseind['neutpos']
        # negind = phaseind['neutneg'] | phaseind['lanina']


        # if clim_data is imported, change this. if division is selected, use this.
        clim_data = alldivDF[self.division]

        #initilize nipa phase object
        model = NIPAphase(clim_data, sst, mei, phaseind[self.phase])
        #_run behind the scenes
        model.gen_corr_grid()


        fig, (ax1, ax2) = plt.subplots(2, 1)
        #create SST map
        fig, ax1, m = model.sstMap(fig = fig, ax = ax1)

        self.display()

    def display(self):
        #_run principle component regression, plot Results
        model.pcr()
        ax2.scatter(model.clim_data, model.pc1)
        plt.show()
        print 'Model hindcast correlation is %.2f' % model.correlation

    def __init__(self):
        root = tk.Tk()
        root.title("NIPA")
        root.configure(background='black')

        tk.Label(root, text = "Division").grid(row = 0, column = 0, sticky = tk.W)

        self.divisionVar1 = tk.StringVar(root)
        self.divisionVar1.set(None)
        dFiles1 = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
            'Kansas', 'Kentucky', 'Lousianna', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana' , 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
            'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas',
            'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
        varDropDown = tk.OptionMenu(root, self.divisionVar1, *dFiles1)
        varDropDown.grid(row = 0, column = 1, sticky = tk.W)

        self.divisionVar2 = tk.StringVar(root)
        self.divisionVar2.set(None)
        dFiles2 = ['01','02','03','04','05','06','07','08','09','10','11','12','13']
        varDropDown2 = tk.OptionMenu(root, self.divisionVar2, *dFiles2)
        varDropDown2.grid(row = 0, column = 2, sticky = tk.W)

        tk.Label(root, text = "Season").grid(row = 1, column = 0, sticky = tk.W)

        self.seasonVar = tk.StringVar(root)
        self.seasonVar.set(None)
        seasonFiles = ['MAM','JJA','SON','DJF']
        seasonDropDown = tk.OptionMenu(root, self.seasonVar, *seasonFiles)
        seasonDropDown.grid(row = 1, column = 1)

        tk.Label(root, text = "Lag").grid(row = 2, column = 0, sticky = tk.W)

        self.lagVar = tk.IntVar(root)
        self.lagVar.set(0)
        lagFiles = [0,1,2,3,4,5,6,7,8,9,10,11,12]
        lagDropDown = tk.OptionMenu(root, self.lagVar, *lagFiles)
        lagDropDown.grid(row = 2, column = 1, sticky = tk.W)

        tk.Label(root, text = "Start Year").grid(row = 3, column = 0, sticky = tk.W)

        self.startYearVar = tk.Text(root, height = 1, width = 4)
        self.startYearVar.grid(row = 3, column = 1, sticky = tk.W)

        tk.Label(root, text = "Number of Years").grid(row = 4, column = 0, sticky = tk.W)

        self.numberYearsVar = tk.Text(root, height = 1, width = 3)
        self.numberYearsVar.grid(row = 4, column = 1, sticky = tk.W)

        tk.Label(root, text = "Phase").grid(row = 5, column = 0, sticky = tk.W)

        self.phaseVar = tk.StringVar(root)
        self.phaseVar.set(None)
        phaseFiles = ['allyears','elnino','neutpos','neutneg','lanina']
        phaseDropDown = tk.OptionMenu(root, self.phaseVar, *phaseFiles)
        phaseDropDown.grid(row = 5, column = 1, sticky = tk.W)


        submit = tk.Button(root, text = "Submit", command = self.calculate)
        submit.grid(row = 6,column = 2,sticky = tk.E)

        root.mainloop()

if __name__ == '__main__':
    nipa_guiF()
#add code to catch years, divisions, & number of years that do not work
