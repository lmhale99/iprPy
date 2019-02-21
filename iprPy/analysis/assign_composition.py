# Standard Python libraries
from __future__ import (print_function, division, absolute_import,
                        unicode_literals)
import os
from DataModelDict import DataModelDict as DM
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am

# iprPy imports
from .. import rootdir

def assign_composition(df, database, lib_directory=None):
    """
    Assigns compositions to calculations.
    """
    # Build counts for available prototypes
    prototypes = database.get_records(style='crystal_prototype')
    counts = {}
    for prototype in prototypes:
        counts[prototype.name] = np.unique(prototype.content.finds('component'), return_counts=True)[1]
    
    # Set default lib_directory (for ref structures)
    if lib_directory is None:
        lib_directory = os.path.join(os.path.dirname(rootdir), 'library')
    
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
        elif 'symbols' in series and 'family' in series:
            
            # If family is a prototype
            if series.family in counts:
                compositions.append(composition_str(series.symbols, counts[series.family]))
            
            # If family is a ref
            else:
                elements = '-'.join(np.unique(series.symbols))
                fname = os.path.join(lib_directory, 'ref', elements, series.family + '.poscar')
                try:
                    ucell = am.load('poscar', fname)
                except:
                    compositions.append(np.nan)
                else:
                    count = np.unique(ucell.atoms.atype, return_counts=True)[1]
                    compositions.append(composition_str(ucell.symbols, count))
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