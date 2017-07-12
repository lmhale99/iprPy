import pymbar
import numpy as np

def process_thermo(thermo_dict, natoms, sizemults=np.array([[0,1],[0,1],[0,1]]), equilsteps=0):
    """Reduce the thermo results down to mean and standard errors."""
    results = {}
    for key in thermo_dict:
        if key == 'step':
            continue
        elif key == 'lx':
            m = (sizemults[0][1]-sizemults[0][0])
            results['a'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps] / m)
        elif key == 'ly':
            m = (sizemults[1][1]-sizemults[1][0])
            results['b'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps] / m)
        elif key == 'lz':
            m = (sizemults[2][1]-sizemults[2][0])
            results['c'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps] / m)
        elif key == 'pe':
            results['E_coh'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps] / natoms)
        else:
            results[key] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps])
    
    return results
    
def uncorrelated_mean(array):
    mean = np.mean(array)
    g = pymbar.timeseries.statisticalInefficiency(array)
    std = np.std(array) * g**0.5
    
    return np.array([mean, std])    