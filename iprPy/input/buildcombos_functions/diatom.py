# http://www.numpy.org/
import numpy as np

import potentials

__all__ = ['diatom']

def diatom(database, keys, content_dict=None, **kwargs):
    """
    Builds parameter sets related to interatomic potentials plus two symbols.
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
        content_dict[lmppot.name] = lmppot.build_model()
            
        # Loop over symbol sets
        for symbols in itersymbolsets(lmppot.symbolsets):
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

def itersymbolsets(symbolsets):
    for symbols in symbolsets:
        for i in range(len(symbols)):
            for j in range(i, len(symbols)):
                yield [symbols[i], symbols[j]]