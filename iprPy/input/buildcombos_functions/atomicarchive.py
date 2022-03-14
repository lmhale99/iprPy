# coding: utf-8

# Standard Python libraries
from typing import Optional, Tuple

# https://github.com/usnistgov/potentials
import potentials

# https://numpy.org/
import numpy as np

__all__ = ['atomicarchive']

def atomicarchive(database,
                  keys: list,
                  content_dict: Optional[dict] = None,
                  record: Optional[str] = None,
                  load_key: str = 'atomic-system',
                  **kwargs) -> Tuple[dict, dict]:
    """
    Build parameter sets based on loading system files from within a
    calculation tar archive.

    Parameters
    ----------
    database : iprPy.database.Database
        The database to use in building combos
    keys : list
        The calculation multikey set to build combos for
    content_dict : dict, optional
        Contains loaded file content.  If not given, an empty
        dict will be created
    record : str, optional
        The record style to search
    load_key : str, optional
        The key of the record where the system info is listed
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

    # Check if potential info is in keys
    if 'potential_file' in keys:
        include_potentials = True
        
        # Extract kwargs starting with "potential"
        potkwargs = {}
        for key in list(kwargs.keys()):
            if key[:10] == 'potential_':
                potkwargs[key[10:]] = kwargs.pop(key)
        
        # Set all status value
        if 'status' in potkwargs and potkwargs['status'] == 'all':
            potkwargs['status'] = None
        
        # Fetch potential records 
        potdb = potentials.Database(local_database=database, local=True, remote=False)
        lmppots, lmppots_df = potdb.get_lammps_potentials(return_df=True, **potkwargs)
        print(len(lmppots_df), 'matching interatomic potentials found')
        if len(lmppots_df) == 0:
            return inputs, content_dict
        kwargs['potential_LAMMPS_key'] = list(np.unique(lmppots_df.key))
    else:
        include_potentials = False

    # Fetch reference records
    parents, parent_df = database.get_records(style=record, return_df=True,
                                              **kwargs)
    print(len(parent_df), 'matching atomic archives found')
    if len(parent_df) == 0:
        return inputs, content_dict

    # Loop over all parents
    for i in parent_df.index:
        parent = parents[i]
        parent_series = parent_df.loc[i]
        
        # Find potential
        if include_potentials:
            try:
                potential_LAMMPS_key = parent_series.potential_LAMMPS_key
                potential_key = parent_series.potential_key
            except:
                # Search grandparents for name of potential
                potential_LAMMPS_key = None
                potential_key = None
                for grandparent in database.get_parent_records(record=parent):
                    try:
                        grandmeta = grandparent.metadata()
                        potential_LAMMPS_key = grandmeta['potential_LAMMPS_key']
                        potential_key = grandmeta['potential_key']
                    except:
                        pass
                    else:
                        break
                if potential_LAMMPS_key is None or potential_key is None:
                    raise ValueError('potential info not found')
            try:
                match = (lmppots_df.key == potential_LAMMPS_key) & (lmppots_df.potkey == potential_key)
                assert match.sum() == 1

            except:
                continue
            
            lmppot = lmppots[match][0]
            if lmppot.name not in content_dict:
                content_dict[lmppot.name] = lmppot.model
        
        # Loop over each system in parent
        for load_info in parent.model.finds(load_key):
            
            # Extract system load info
            load_file = load_info['artifact']['file']
            load_style = load_info['artifact']['format']
            load_options = load_info['artifact'].get('load_options', '')
            symbols = ' '.join(load_info.aslist('symbols'))

            # Loop over input keys
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
                elif key == 'load_file':
                    inputs['load_file'].append(f'{parent.name}/{load_file}')
                elif key == 'load_content':
                    inputs['load_content'].append(f'tarfile {parent.name} {load_file}')
                elif key == 'load_style':
                    inputs['load_style'].append(load_style)
                elif key == 'load_options':
                    inputs['load_options'].append(load_options)
                elif key == 'symbols':
                    inputs['symbols'].append(symbols)
                elif key == 'family':
                    inputs['family'].append(parent_series.family)
                elif key == 'elasticconstants_file':
                    inputs['elasticconstants_file'].append(f'{parent.name}.json')
                elif key == 'elasticconstants_content':
                    inputs['elasticconstants_content'].append(f'record {parent.name}')
                else:
                    inputs[key].append('')
    
    return inputs, content_dict