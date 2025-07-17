from typing import Union
from pathlib import Path

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import atomman as am 
import iprPy

from . import load_transition_temp, save_transition_temp, noval





def find_transition_temps(database,
                          transition_temp_csv: Union[Path, str] = 'transition_temp.csv',
                          search_temp: float = 500,
                          threshold: float = 0.015):
    """
    Method to automatically identify the transition temperature of crystalline
    phases upon heating based on the measured enthalpy and lattice constants.

    Algorithm details: Estimates of the measured values H, a, b, and c are 
    obtained by linearly extrapolating from the two previous temperatures.
    A prediction error is then calculated between the estimate and the actual
    measured values.  The transition temperature is then identified as the
    first temperature at which the error of at least one of the properties
    is greater than some threshold.

    Parameters
    ----------
    database : iprPy.database.Database
        The database containing the md_solid_properties records to evaluate.
    transition_temp_csv : str or Path, optional
        The csv file containing already known transition temperatures on a
        relaxed_crystal basis.  Default is 'transition_temp.csv'.
    search_temp : float, optional
        The minimum temperature (in K) that a relaxed_crystal must have been
        heated up to before including in this search.  Default value is 300.
    threshold : float, optional
        The error threshold to use for identifying likely transition points.
    """
    
    # Load the transition temperatures already identified
    transition_temp = load_transition_temp(transition_temp_csv)
    print(len(transition_temp), 'relaxed_crystals already known')

    # Fetch md_solid_properties records
    results_df = database.get_records_df('md_solid_properties')
    print(len(results_df), 'md_solid_properties records found')

    # Add any missing crystals to transition_temp(_csv)
    add_new_crystals(results_df, transition_temp, transition_temp_csv)

    # Find all unique relaxed_crystals heated to at least the search_temp
    keys = np.unique(results_df[results_df['T (K)'] == search_temp].relaxed_crystal_key.values)

    # Filter out the crystals that already have a transition temp value
    relaxed_crystal_keys = []
    for key in keys:
        if transition_temp[key] == noval:
            relaxed_crystal_keys.append(key)
    print(len(relaxed_crystal_keys), 'crystals to investigate')

    # Iterate over the crystals
    num_temps_found = 0
    for relaxed_crystal_key in tqdm(relaxed_crystal_keys):
        crystal_results_df = results_df[results_df.relaxed_crystal_key == relaxed_crystal_key].sort_values('T (K)')
        T = crystal_results_df['T (K)'].values
        H = crystal_results_df['H (eV/atom)'].values
        a = crystal_results_df['a'].values
        b = crystal_results_df['b'].values
        c = crystal_results_df['c'].values
        
        # Guess the transition temp based on the different properties
        indices = [
            guess_transition_index(H, threshold=threshold),
            guess_transition_index(a, threshold=threshold),
            guess_transition_index(b, threshold=threshold),
            guess_transition_index(c, threshold=threshold)
        ]
        
        # Update the transition temp if a transition is found
        if not np.all(np.isnan(indices)):
            T_trans = T[int(np.nanmin(indices))]
            transition_temp[relaxed_crystal_key] = T_trans
            num_temps_found += 1

    print(num_temps_found, 'transition temperatures identified')

    if num_temps_found > 0:
        save_transition_temp(transition_temp, transition_temp_csv)






    



def add_new_crystals(results_df,
                     transition_temp: dict,
                     transition_temp_csv: Union[Path, str]):
    """
    Searches the dataframe for any relaxed crystals that are not already in
    the transition_temp dict and csv file.  Missing entries are added to the
    dict and the csv file is updated.
    """
    crystal_keys = np.unique(results_df.relaxed_crystal_key)
    print(len(crystal_keys), 'relaxed_crystals in the md_solid_properties records')

    num_added: int = 0
    for crystal_key in crystal_keys:
        if crystal_key not in transition_temp:
            transition_temp[crystal_key] = noval
            num_added += 1
    transition_temp = dict(sorted(transition_temp.items()))

    print(num_added, 'new relaxed_crystals added')
    if num_added > 0:
        save_transition_temp(transition_temp, transition_temp_csv)

def forward_extrapolation_error(v):
    """
    Computes the error associated with linearly predicting a value of v from
    the previous two data points.
    
    Returns
    -------
    error : numpy.ndarray
        The prediction errors for the points in v.  Note that the first two
        in the array are zero as such extrapolations cannot be performed.
    
    """
    
    pred = 2 * v[1:-1] - v[:-2]
    
    error = np.zeros_like(v)
    error[2:] = np.abs( (v[2:] - pred) / v[2:] )
    return error

def reverse_extrapolation_error(v):
    """
    Computes the error associated with linearly predicting a value of v from the
    following two data points.
    
    Returns
    -------
    error : numpy.ndarray
        The prediction errors for the points in v.  Note that the last two
        in the array are zero as such extrapolations cannot be performed.
    
    """
    
    pred = 2 * v[1:-1] - v[2:]
    
    error = np.zeros_like(v)
    error[:-2] = np.abs( (v[:-2] - pred) / v[:-2] )
    return error

def neighbor_interpolation_error(v):
    """
    Computes the error associated with linearly predicting a value of v from
    the +- neighboring two data points.
    
    Returns
    -------
    error : numpy.ndarray
        The prediction errors for the points in v.  Note that the first and
        last values in the array are zero as such extrapolations cannot be
        performed.
    """

    pred = v[:-2] + (v[2:] - v[:-2]) / 2
    
    error = np.zeros_like(v)
    error[1:-1] = np.abs( (v[1:-1] - pred) / v[1:-1] )
    return error


def guess_transition_index(v, threshold=0.01, method='forward'):
    
    if method == 'forward':
        error = forward_extrapolation_error(v)
        indices = np.where(error > threshold)[0]
        
    elif method == 'center':
        error = 2 * neighbor_interpolation_error(v)
        indices = np.where(error > threshold)[0] + 1
    
    elif method == 'reverse':
        error = reverse_extrapolation_error(v)
        indices = np.where(error > threshold)[0] + 2
        
    else:
        raise ValueError('unsupported method style')
    
    if len(indices) == 0:
        index = np.nan
    
    
    # One peak at lowest index implies transition already occured
    elif indices[0] == 2 and 3 not in indices:
        index = 1
    
    else:
        index = indices[0]
        
    return index


def plot_H(df, relaxed_crystal_key, T_trans):

    T = df['T (K)'].values
    H = df['H (eV/atom)'].values

    hastrans = T >= T_trans

    T1 = T[~hastrans]
    T2 = T[hastrans]
    H1 = H[~hastrans]
    H2 = H[hastrans]

    plt.title(relaxed_crystal_key)
    plt.plot(T1, H1, 'o:')
    plt.plot(T2, H2, 'o:')
    plt.xlim(0, T.max())

    plt.savefig(f'H/{relaxed_crystal_key}.png')
    plt.close()
    
def plot_abc(df, relaxed_crystal_key, T_trans):

    T = df['T (K)'].values
    a = df['a'].values
    b = df['b'].values
    c = df['c'].values

    max_abc = max(a[0], b[0], c[0]) * 1.2
    
    hastrans = T >= T_trans

    T1 = T[~hastrans]
    T2 = T[hastrans]
    a1 = a[~hastrans]
    a2 = a[hastrans]
    b1 = b[~hastrans]
    b2 = b[hastrans]
    c1 = c[~hastrans]
    c2 = c[hastrans]

    plt.title(relaxed_crystal_key)
    plt.plot(T1, a1, 'o:', color='tab:blue')
    plt.plot(T1, b1, 'o:', color='tab:blue')
    plt.plot(T1, c1, 'o:', color='tab:blue')
    plt.plot(T2, a2, 'o:', color='tab:orange')
    plt.plot(T2, b2, 'o:', color='tab:orange')
    plt.plot(T2, c2, 'o:', color='tab:orange')
    plt.xlim(0, T.max())
    plt.ylim(None, max_abc)

    
    plt.savefig(f'abc/{relaxed_crystal_key}.png')
    plt.close()