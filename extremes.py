from matplotlib import pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF
from scipy.stats import t, gamma, norm
from scipy.stats import genextreme as gev
from numpy import max, ceil, arange, linspace, ndarray, array, zeros, vstack, corrcoef
from matplotlib import pyplot as plt
from numpy import arange, isnan
from dw import *
from station_module import *


#########
# This is the master file for the homework. Should construct an ipython notebook
# document out of it once everything is working.
#########
def probability():
    from scipy.stats import bernoulli as bl
    from numpy import arange, zeros, array
    #_Generate two bernoulli trials with p = 0.01 twenty times

    n = 1000
    x = []
    for i in xrange(n):
        count = 0
        trigger = True
        while trigger:
            count += 1
            trials = (bl.rvs(p = 0.01, size = 20))
            for i in arange(len(trials)-1):
                if (trials[i] == 1) & (trials[i+1] == 1):
                    trigger = False
        x.append(count) #count is # of 20 yr periods, prob is inverse
    plt.hist(100./array(x), n/10); plt.show()
    print np.median(1./array(x))
    return x

def bootstrp(x, nboot = 1000):
    from numpy.random import randint
    x = x[~isnan(x)]
    m = {'Shape' : [], 'Location' : [], 'Scale' :[], '100yrEvent': []}
    for i in xrange(nboot):
        idx = randint(0, len(x) - 1, len(x))
        shp, loc, scl = gev.fit(x[idx])
        m['Shape'].append(shp)
        m['Location'].append(loc)
        m['Scale'].append(scl)
        m['100yrEvent'].append(gev.ppf(0.99, shp, loc, scl))
    for var in m:
        m[var] = array(m[var])
    return m
def get_data(div = 'Wisconsin-08', startyr = 1901, n_yrs = 114, season = 'JJA'):
    from pandas import DataFrame
    endyr = startyr + n_yrs - 1
    months = {'MAM' : [3, 4, 5],
                'All' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                 'JJA' : [6, 7, 8]}
    bounds = {'Texas-06' : [30, 32.5, -102, -97], \
                'Texas-09': [28, 30, -101, -96], \
                 'Wisconsin-08' : [42, 44, -91.5, -88.5] }
    kwgroups = create_kwgroups( climdiv_months = months[season], \
                            climdiv_startyr = startyr, n_yrs = n_yrs, \
                            )
    mei, phaseind = create_phase_index(**kwgroups['mei'])
    base_fp = EV['GHCND_HCN']
    year_list = np.arange(startyr, endyr + 1)
    lat = (bounds[div][0], bounds[div][1])
    lon = (bounds[div][2], bounds[div][3])
    year_lim = (year_list.min(), \
                year_list.max())
    station_info = extract_stations(var = 'PRCP', years = year_lim, lat = lat, lon = lon)
    stations = {}
    for stationID in station_info:
        NIPAdata = ('Allyears', months[season], list(arange(startyr, startyr + n_yrs)))
        var = 'PRCP'
        x = stationDaily(var, stationID, NIPAdata).data.max()
        x = x[~isnan(x)]/100
        stations[station_info[stationID]['name'].strip()] = x

    return DataFrame.from_dict(stations)

def getSDdata(div = 'California-06', startyr = 1901, n_yrs = 100, season = 'DJF'):
    from pandas import DataFrame
    endyr = startyr + n_yrs - 1
    months = {'MAM' : [3, 4, 5],
                'All' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                 'JJA' : [6, 7, 8],
			 		'DJF' : [12, 1, 2]}
    bounds = {'Texas-06' : [30, 32.5, -102, -97], \
                'Texas-09': [28, 30, -101, -96], \
                 'Wisconsin-08' : [42, 44, -91.5, -88.5],
			 		'California-06': [32.5, 33.5, -117.5, -116.5]}

    kwgroups = create_kwgroups( climdiv_months = months[season],
                            climdiv_startyr = startyr, n_yrs = n_yrs,
							mei_lag = 2, debug = True
                            )
    mei, phaseind = create_phase_index(**kwgroups['mei'])
    base_fp = EV['GHCND_HCN']
    year_list = np.arange(startyr, endyr + 1)
    lat = (bounds[div][0], bounds[div][1])
    lon = (bounds[div][2], bounds[div][3])
    year_lim = (year_list.min(), \
                year_list.max())
    station_info = extract_stations(var = 'PRCP', years = year_lim, lat = lat, lon = lon)
    stations = {}
    for stationID in station_info:
        NIPAdata = ('Allyears', months[season], list(arange(startyr, startyr + n_yrs)))
        var = 'PRCP'
        x = stationDaily(var, stationID, NIPAdata).data.max()
        x = x[~isnan(x)]/100
        stations[station_info[stationID]['name'].strip()] = x

    return mei, DataFrame.from_dict(stations)

def get_100yr(x):
    x = x[~isnan(x)]
    shp, loc, scl = gev.fit(x)
    return gev.ppf(0.99, shp, loc, scl)
def get_CI(m, var = '100yrEvent'):
    from numpy import percentile
    CI = percentile(m[var], (2.5, 97.5))
    return CI
def plot_hist(x, ax):
    from numpy import isnan
    x = x[~isnan(x)]
    shp, loc, scl = gev.fit(x)
    dx = 1
    nbins = 16
    p_x = arange(0, nbins, 0.1)
    p_gev = gev.pdf(p_x, shp, loc, scl)
    ax.hist(x, bins = 16, normed = True, color = 'grey')
    ax.plot(p_x, p_gev, color = 'black', linewidth = 2)
    ax.set_xlabel('Precipitation, cm')
    line = 'Parameters:\nShape: %.2f\nLocation: %.2f\nScale: %.2f' % (-shp, loc, scl) #_Shape negative for convention
    ax.text(10,0.17,line)
    return ax

def gev_figs(x):
    shp, loc, scl = gev.fit(x)
    dx = 1
    nbins = ceil(max(x))
    p_x = arange(0, nbins, 0.1)
    p_gev = gev.pdf(p_x, shp, loc, scl)
    fig, axes = plt.subplots(3,3, figsize = (12,12))
    axes[0,0].hist(x, bins = nbins, normed = True, color= 'grey')
    axes[0,0].plot(p_x, p_gev, '-k', linewidth = 2)
    axes[0,0].set_title('Histogram and Generalized Exterme Value Distribution')
    axes[0,0].set_ylabel('Probability Density'); axes[0,0].set_xlabel('Block Maximum');

    cdf = ECDF(x)

    axes[0,1].step(cdf.x, cdf.y)
    f_gev = gev.cdf(p_x, shp, loc, scl)
    axes[0,1].plot(p_x, f_gev)
    axes[0,1].set_title('CDF')

    from numpy.random import randint
    nboot = 1000
    m = bootstrp(x, nboot)

    for var, ax in zip(m, (axes[1,0], axes[1,1], axes[1,2])):
        ax.hist(m[var], bins = 20, color = 'grey')
        ax.set_xlabel(var + ' Parameter')

    axes[2,0].scatter(m['Shape'], m['Location'], c = 'k', marker = '.')
    axes[2,0].scatter(shp, loc, s = 100, c = 'r', marker = 'o')
    axes[2,0].set_xlabel('Shape Parameter'); axes[2,0].set_ylabel('Location Parameter')

    axes[2,1].scatter(m['Shape'], m['Scale'], c = 'k', marker = '.')
    axes[2,1].scatter(shp, scl, s = 100, c = 'r', marker = 'o')
    axes[2,1].set_xlabel('Shape Parameter'); axes[2,1].set_ylabel('Scale Parameter')

    axes[2,2].scatter(m['Location'], m['Scale'], c = 'k', marker = '.')
    axes[2,2].scatter(loc, scl, s = 100,  c = 'r', marker = 'o')
    axes[2,2].set_xlabel('Location Parameter'); axes[2,2].set_ylabel('Scale Parameter');

    R = gev.ppf(0.99, shp, loc, scl)
    from numpy import sort, floor
    Rboot = zeros((nboot))
    for i in xrange(nboot):
        Rboot[i] = gev.ppf(0.99, m['Shape'][i], m['Location'][i], m['Scale'][i])
    axes[0,2].hist(Rboot, bins = 30, color = 'grey', normed = True);
    r_sort = sort(Rboot)

    axes[0,2].vlines(r_sort[int(floor(nboot * 0.025))], 0, .2, colors = 'b', linestyles = '--')
    axes[0,2].vlines(r_sort[int(floor(nboot * 0.975))], 0, .2, colors = 'b', linestyles = '--')
    axes[0,2].vlines(r_sort[int(floor(nboot * 0.5))], 0, .2, colors = 'b', linewidth = 2)
    axes[0,2].set_ylabel('Probability Density'); axes[0,2].set_xlabel('100yr Return Level')
    axes[0,2].set_title('Bootstrapped 100 "Year" Return Intervals and Confidence Limits');
    return fig
