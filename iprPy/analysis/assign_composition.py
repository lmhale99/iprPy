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
            composition = series.ucell.composition
            if composition is not None:
                compositions.append(composition)
            else:
                compositions.append(np.nan)
        
        # Use symbols and family info if available (E_vs_r_scan, relax_*)  
        elif 'symbols' in series and 'family' in series:
            
            # If family is a prototype
            if series.family in counts:
                compositions.append(am.tools.compositionstr(series.symbols, counts[series.family]))
            
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
                    compositions.append(am.tools.compositionstr(ucell.symbols, count))
        else:
            compositions.append(np.nan)
    df['composition'] = compositions