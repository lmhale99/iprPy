# coding: utf-8

# Standard Python libraries
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

__all__ = ['assign_currentIPR', 'current_ipr_potential_keys']

def assign_currentIPR(calc_df=None, pot_df=None, database=None):
    """
    Assigns the currentIPR field to calc_df and/or pot_df.  The currentIPR
    field indicates if the record is associated with the newest version of a
    potential_LAMMPS record.

    Parameters
    ----------
    calc_df : pandas.DataFrame
        A DataFrame of calculation records containing a 'potential_LAMMPS_id'
        field.
    pot_df : pandas.DataFrame, optional
        A DataFrame of potential_LAMMPS records.  Note that if pot_df
        is a partial set of potential_LAMMPS records, currentIPR will be True
        for the newest versions in pot_df. Either pot_df or database
        needs to be given.
    database : iprPy.Database, optional
        The database whose potential_LAMMPS records should be used.  Either 
        pot_df or database needs to be given.
    """
    # Test if only one parameter given
    if calc_df is not None and pot_df is None and database is None:
        # Rename calc_df to pot_df if it is not for calculation records
        if 'potential_LAMMPS_id' not in calc_df:
            pot_df, calc_df = calc_df, None
    
    # Fetch keys
    currentkeys = current_ipr_potential_keys(pot_df, database)
    
    # Assign currentIPR to calc_df
    if calc_df is not None:
        calc_df['currentIPR'] = calc_df.potential_LAMMPS_key.isin(currentkeys)
    
    # Assign currentIPR to pot_df
    if pot_df is not None:
        pot_df['currentIPR'] = pot_df['key'].isin(currentkeys)

def current_ipr_potential_keys(pot_df=None, database=None):
    """
    Builds list of potential_LAMMPS_keys for current IPR potentials.  Note that this
    only works for the potential_LAMMPS style potentials whose ids follow the
    naming convention of ending in --ipr-#.

    Parameters
    ----------
    pot_df : pandas.DataFrame, optional
        A DataFrame of potential_LAMMPS records.  Note that if pot_df
        is a partial set of potential_LAMMPS records, currentids will be the
        list of newest versions in pot_df. Either pot_df or database
        needs to be given.
    database : iprPy.Database, optional
        The database whose potential_LAMMPS records should be used.  Either 
        pot_df or database needs to be given.

    Returns
    -------
    currentids : list
        A list of all current potential_LAMMPS record ids.
    """
    # Load pot_df from database if not given
    if pot_df is None:
        if database is None:
            raise ValueError('Either pot_df or database needs to be given')
        pot_df = database.get_records_df(style='potential_LAMMPS')
    else:
        pot_df = deepcopy(pot_df)

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
    currentkeys = []
    for pot_id in np.unique(pot_df.pot_id.values):
        check_df = pot_df[pot_df.pot_id == pot_id]
        check_df = check_df[check_df.versionstyle == 'ipr']
        check_df = check_df[check_df.versionnumber == check_df.versionnumber.max()]
        if len(check_df) == 1:
            currentkeys.append(check_df['key'].values[0])
        elif len(check_df) > 1:
            raise ValueError('Bad currentIPR check for '+pot_id)
    
    return currentkeys