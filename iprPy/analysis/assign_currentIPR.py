# Standard Python libraries
from __future__ import (print_function, division, absolute_import,
                        unicode_literals)
                        
import numpy as np

def assign_currentIPR(calc_df, database):
    """
    Identifies which calculations use currentIPR potentials.
    """
    pot_df = database.get_records_df(style='potential_LAMMPS')
    currentids = current_ipr_potential_ids(pot_df)
    calc_df['currentIPR'] = calc_df.potential_LAMMPS_id.isin(currentids)

def current_ipr_potential_ids(pot_df):
    """
    Builds list of potential_ids for current IPR potentials.
    """

    # Extract versionstyle and versionnumber from potential implementation ids
    versionstyle = []
    versionnumber = []
    for name in pot_df['id'].values:
        version = name.split('--')[-1]
        try:
            versionnumber.append(int(version[-1]))
        except:
            versionnumber.append(np.nan)
            versionstyle.append(version)
        else:
            versionstyle.append(version[:-1])

    pot_df['versionstyle'] = versionstyle
    pot_df['versionnumber'] = versionnumber

    # Loop through unique potential id's
    currentids = []
    for pot_id in np.unique(pot_df.pot_id.values):
        check_df = pot_df[pot_df.pot_id == pot_id]
        check_df = check_df[check_df.versionstyle == 'ipr']
        check_df = check_df[check_df.versionnumber == check_df.versionnumber.max()]
        if len(check_df) == 1:
            currentids.append(check_df['id'].values[0])
        elif len(check_df) > 1:
            raise ValueError('Bad currentIPR check for '+pot_id)
    
    return currentids