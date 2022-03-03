# coding: utf-8

# Standard Python libraries
from typing import Optional, Tuple

# https://github.com/usnistgov/potentials
import potentials

__all__ = ['diatom']

def diatom(database,
           keys: list,
           content_dict: Optional[dict] = None,
           **kwargs) -> Tuple[dict, dict]:
    """
    Build parameter sets related to interatomic potentials plus two symbols.

    Parameters
    ----------
    database : iprPy.database.Database
        The database to use in building combos
    keys : list
        The calculation multikey set to build combos for
    content_dict : dict, optional
        Contains loaded file content.  If not given, an empty
        dict will be created
    kwargs : any
        Additional keyword arguments will be used to limit which records from
        the database are used in building combos values.

    Returns
    -------
    inputs : dict
        Contains the values generated for each key
    content_dict : dict
        Contains loaded file content
    """
    # Initialize inputs and content dict
    inputs = {}
    for key in keys:
        inputs[key] = []
    if content_dict is None:
        content_dict = {}

    # Pull out potential kwargs
    potkwargs = {}
    for key in kwargs:
        if key[:10] == 'potential_':
            potkwargs[key[10:]] = kwargs[key]

    # Set all status value
    if 'status' in potkwargs and potkwargs['status'] == 'all':
        potkwargs['status'] = None

    # Fetch potential records and df
    potdb = potentials.Database(local_database=database, local=True, remote=False)
    lmppots, lmppots_df = potdb.get_lammps_potentials(return_df=True, **potkwargs)
    print(len(lmppots_df), 'matching interatomic potentials found')
    if len(lmppots_df) == 0:
        return inputs, content_dict
    
    # Loop over all potentials 
    for i in lmppots_df.index:
        lmppot = lmppots[i]
        if lmppot.name not in content_dict:
            content_dict[lmppot.name] = lmppot.model
            
        # Loop over symbol sets
        for symbols in itersymbolpairs(lmppot.symbols):
            for key in keys:
                if key == 'potential_file':
                    inputs['potential_file'].append(f'{lmppot.name}.json')
                elif key == 'potential_content':
                    inputs['potential_content'].append(f'record {lmppot.name}')
                elif key == 'potential_dir' and lmppot.pair_style != 'kim':
                    inputs['potential_dir'].append(lmppot.name)
                elif key == 'potential_dir_content' and lmppot.pair_style != 'kim':
                    inputs['potential_dir_content'].append(f'tar {lmppot.name}')
                elif key == 'potential_kim_id' and lmppot.pair_style == 'kim':
                    inputs['potential_kim_id'].append(lmppot.id)
                elif key == 'potential_kim_potid' and lmppot.pair_style == 'kim' and len(lmppot.potids) > 1:
                    inputs['potential_kim_potid'].append(lmppot.potid)
                elif key == 'symbols':
                    inputs['symbols'].append(' '.join(sorted(symbols)).strip())
                else:
                    inputs[key].append('')

    return inputs, content_dict

def itersymbolpairs(symbols):
    for i in range(len(symbols)):
        for j in range(i, len(symbols)):
            yield [symbols[i], symbols[j]]