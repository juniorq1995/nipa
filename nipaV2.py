#!/usr/bin/env python
"""
New NIPA module
"""

import os
import pandas as pd
import numpy as np
from collections import namedtuple
seasonal_var = namedtuple('seasonal_var', ('data','lat','lon'))
from os import environ as EV
from matplotlib import cm, pyplot as plt


class NIPAphase(object):
    """
    Class and methods for operations on phases as determined by the MEI.

    _INPUTS
    phaseind:    dictionary containing phase names as keys and corresponding booleans as index vectors
    clim_data:    n x 1 pandas time series of the climate data (predictands)
    sst:        dictionary containing the keys 'data', 'lat', and 'lon'
    slp:        dictionary containing the keys 'data', 'lat', and 'lon'
    mei:        n x 1 pandas time series containing averaged MEI values

    _ATTRIBUTES
    sstcorr_grid
    slpcorr_grid

    """
    def __init__(self, clim_data, sst, mei, phaseind):

        self.clim_data = clim_data[phaseind]
        self.sst = seasonal_var(sst.data[phaseind], sst.lat, sst.lon)
        self.mei = mei[phaseind]
        self.flags = {}

        """
        sst is a named tuple

        """


    def gen_corr_grid(    self, corrconf = 0.99, debug = False, quick = True    ):
        from numpy import meshgrid, zeros, ma, isnan, linspace
        from atmos_ocean_data import vcorr, sig_test

        corrlevel = 1 - corrconf

        fieldData = self.sst.data
        clim_data = self.clim_data

        corr_grid = vcorr(X = fieldData, y = clim_data)

        n_yrs = len(clim_data)

        p_value = sig_test(corr_grid, n_yrs)

        #Mask insignificant gridpoints
        corr_grid = ma.masked_array(corr_grid, ~(p_value < corrlevel))
        #Mask land
        corr_grid = ma.masked_array(corr_grid, isnan(corr_grid))
        #Mask northern/southern ocean
        corr_grid.mask[self.sst.lat > 60] = True
        corr_grid.mask[self.sst.lat < -30] = True
        nlat, nlon = len(self.sst.lat), len(self.sst.lon)
        self.corr_grid = corr_grid
        self.n_grid = nlat * nlon - corr_grid.mask.sum()

        return

    def sstMap(self,  cmap = cm.RdBu_r, fig = None, ax = None):
        from mpl_toolkits.basemap import Basemap
        from numpy import linspace
        if fig == None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        m = Basemap(ax = ax, projection = 'robin', lon_0 = 270, resolution = 'i')
        m.drawmapboundary(fill_color='#5f6c7a')
        m.drawcoastlines(linewidth = 0.25)
        m.drawcountries()
        m.fillcontinents(color='#698B22',lake_color='#5f6c7a')
        parallels = np.linspace(m.llcrnrlat, m.urcrnrlat, 4)
        meridians = np.linspace(m.llcrnrlon, m.urcrnrlon, 4)
        m.drawparallels(parallels, linewidth = 1, labels = [0,0,0,0])
        m.drawmeridians(meridians, linewidth = 1, labels = [0,0,0,0])



        lons = self.sst.lon
        lats = self.sst.lat

        data = self.corr_grid
        levels = linspace(-0.8,0.8,9)

        lons, lats = np.meshgrid(lons,lats)
        im1 = m.pcolormesh(lons,lats,data, vmin = np.min(levels), \
            vmax=np.max(levels), cmap = cmap, latlon=True)
        cb = m.colorbar(im1,'bottom', size="5%", pad="2%")
        return fig, ax, m

    def pcr(self):
        import numpy as np
        from numpy import array
        from scipy.stats import pearsonr as corr
        from scipy.stats import linregress
        from matplotlib import pyplot as plt
        from atmos_ocean_data import weightsst
        from eofs.standard import Eof

        predictand = self.clim_data
        n = len(predictand)

        mask = np.tile(self.corr_grid.mask, [n, 1, 1])
        ssts = np.ma.masked_array(data = self.sst.data, mask = mask)

        yhat = np.zeros(n)
        e = np.zeros(n)

        #set up weighting vector for EOF analysis
        lats = self.sst.lat
        wgts = np.sqrt(np.abs(np.cos(np.radians(lats))))[..., np.newaxis]

        from eofs.standard import Eof
        solver = Eof(ssts, weights = wgts)
        pc1 = solver.pcs(npcs=1, pcscaling = 1).squeeze()

        slope, intecept, r, p, err = linregress(pc1, predictand)

        self.pc1 = pc1
        self.correlation = r

        return
