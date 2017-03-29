#Standard library imports
from __future__ import print_function, division
import os
import sys

#http://www.numpy.org/
import numpy as np

#http://pandas.pydata.org/
import pandas as pd

#https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

import matplotlib.pyplot as plt
from matplotlib import cm

from scipy.interpolate import griddata, Rbf

dbase = iprPy.Database('local', 'C:\\Users\\lmh1\\Documents\\calculations\\ipr\\library_test')

record_df = []
for record in dbase.iget_records(style='calculation-generalized-stacking-fault'):
    record_df.append(record.todict())
record_df = pd.DataFrame(record_df)

condition1 = record_df.stackingfault_id == 'A2--W--bcc--112sf'
condition2 = record_df.status == 'finished'

lookie_record_df = record_df[condition1 & condition2]

for i in xrange(len(lookie_record_df)):
    gsf_df = lookie_record_df.iloc[0].gsf_plot
    
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize = [16,7])

    gamma = uc.get_in_units(gsf_df.energy, 'mJ/m^2')
    points = gsf_df.loc[:, ['shift1', 'shift2']]
    print('Data retrieved')
    sys.stdout.flush()
    a1_grid, a2_grid = np.meshgrid(np.linspace(0, 1, 200), np.linspace(0, 1, 200))
    print('Grid built')
    sys.stdout.flush()
    
    E_grid_raw = griddata(points, gamma, (a1_grid, a2_grid), method='nearest')
    print('data on grid')
    sys.stdout.flush()
    
    im = ax1.pcolormesh(a1_grid, a2_grid, E_grid_raw, cmap=cm.bwr)
    print('data added to fig')
    sys.stdout.flush()
    
    
    gsffit = Rbf(gsf_df.shift1, gsf_df.shift2, gamma)
    E_grid_fit = gsffit(a1_grid, a2_grid)
    print('rbf-fit')
    sys.stdout.flush()
    im = ax2.pcolormesh(a1_grid, a2_grid, E_grid_fit, cmap=cm.bwr)
    print('data added to fig')
    sys.stdout.flush()
    
    cbar_ax = fig.add_axes([0.95, 0.12, 0.01, 0.77])
    cbar = fig.colorbar(im, cax=cbar_ax)
    print('colorbar added to fig')
    sys.stdout.flush()
    plt.savefig(str(i)+'.png')
    plt.close()