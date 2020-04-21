# coding: utf-8

# Standard Python libraries
from pathlib import Path

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am

# iprPy imports
from .. import Settings

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
        lib_directory = Settings().library_directory
    
    # Identify compositions
    compositions = []
    for i in range(len(df)):
        series = df.iloc[i]
        
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
                fname = Path(lib_directory, 'reference_crystal', series.family + '.json')
                try:
                    ucell = am.load('system_model', fname)
                except:
                    compositions.append(np.nan)
                else:
                    count = np.unique(ucell.atoms.atype, return_counts=True)[1]
                    compositions.append(am.tools.compositionstr(ucell.symbols, count))
        else:
            compositions.append(np.nan)
    df['composition'] = compositions