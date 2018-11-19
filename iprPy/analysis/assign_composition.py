# Standard Python libraries
from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

from DataModelDict import DataModelDict as DM
import numpy as np

def assign_composition(df, database):
    """
    Assigns compositions to calculations.
    """
    # Build counts for available prototypes
    prototypes = database.get_records(style='crystal_prototype')
    counts = {}
    for prototype in prototypes:
        counts[prototype.name] = np.unique(prototype.content.finds('component'), return_counts=True)[1]
    
    # Identify compositions
    compositions = []
    for i, series in df.iterrows():
        
        # Use ucell system if available (crystal_space_group)
        if 'ucell' in series:
            if series.ucell.symbols[0] is not None:
                counts = np.unique(series.ucell.atoms.atype, return_counts=True)[1]
                compositions.append(composition_str(series.ucell.symbols, counts))
            else:
                compositions.append(np.nan)
        
        # Use symbols and family info if available (E_vs_r_scan, relax_*)  
        elif 'symbols' in series and series.family in counts:
            compositions.append(composition_str(series.symbols, counts[series.family]))
        else:
            compositions.append(np.nan)
    df['composition'] = compositions

def composition_str(symbols, counts):
    """
    Generates a composition string for a unit cell.
    
    Parameters
    ----------
    symbols : list
        All element model symbols.
    count : list
        How many unique sites are occupied by each symbol.
    
    Returns
    -------
    str
        The composition string.
    """
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]
    
    sym_dict = {}
    for i in range(len(symbols)):
        sym_dict[symbols[i]] = counts[i]
    
    for prime in primes:
        if max(sym_dict.values()) < prime:
            break
        
        while True:
            breaktime = False
            for value in sym_dict.values():
                if value % prime != 0:
                    breaktime = True
                    break
            if breaktime:
                break
            for key in sym_dict:
                sym_dict[key] /= prime
    
    composition =''
    for key in sorted(sym_dict):
        if sym_dict[key] > 0:
            composition += key
            if sym_dict[key] != 1:
                composition += str(int(sym_dict[key]))
    
    return composition