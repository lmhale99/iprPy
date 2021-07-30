# http://www.numpy.org/
import numpy as np

import potentials

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

__all__ = ['atomicreference']

def atomicreference(database, keys, content_dict=None, 
                    record='reference_crystal', elements=None,
                    **kwargs):
    
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
    else:
        include_potentials = False
    
    # Fetch reference records
    references, reference_df = database.get_records(style=record, return_df=True,
                                                    **kwargs)
    print(len(reference_df), 'matching atomic references found')
    if len(reference_df) == 0:
        return inputs, content_dict

    # Build with potentials
    if include_potentials:
        
        # Set all status value
        if 'status' in potkwargs and potkwargs['status'] == 'all':
            potkwargs['status'] = None

        # Fetch potential records 
        potdb = potentials.Database(local_database=database, local=True, remote=False)
        lmppots, lmppots_df = potdb.get_lammps_potentials(return_df=True, **potkwargs)
        print(len(lmppots_df), 'matching interatomic potentials found')
        if len(lmppots_df) == 0:
            return inputs, content_dict
        
        # Loop over all unique reference element sets
        reference_df['elementstr'] = reference_df.symbols.apply(' '.join)
        for elementstr in np.unique(reference_df.elementstr):
            reference_symbols = elementstr.split()
            
            # Loop over all potentials
            for j in lmppots_df.index:
                lmppot = lmppots[j]
                lmppot_series = lmppots_df.loc[j]
                content_dict[lmppot.name] = lmppot.build_model()
                lmppot_symbols = lmppot_series.symbols
                lmppot_elements = lmppot_series.elements
                
                # Loop over all potential element-symbol sets
                for symbolstr in symbolstrings(reference_symbols, lmppot_elements, lmppot_symbols):
                    
                    # Loop over all references with the reference element set
                    for i in reference_df[reference_df.elementstr==elementstr].index:
                        reference = references[i]
                        content_dict[reference.name] = reference.build_model()
                
                        # Loop over input keys
                        for key in keys:
                            if key == 'potential_file':
                                inputs['potential_file'].append(lmppot.name + '.json')
                            elif key == 'potential_content':
                                inputs['potential_content'].append(f'record {lmppot.name}')
                            elif key == 'potential_dir' and lmppot.pair_style != 'kim':
                                inputs['potential_dir'].append(lmppot.name)
                            elif key == 'potential_dir_content' and lmppot.pair_style != 'kim':
                                inputs['potential_dir_content'].append(f'tar {lmppot.name}')
                            elif key == 'potential_kim_id' and lmppot.pair_style == 'kim':
                                inputs['potential_kim_id'].append(lmppot.id)
                            elif key == 'load_file':
                                inputs['load_file'].append(reference.name+'.json')
                            elif key == 'load_content':
                                inputs['load_content'].append(f'record {reference.name}')
                            elif key == 'load_style':
                                inputs['load_style'].append('system_model')
                            elif key == 'family':
                                inputs['family'].append(reference.name)
                            elif key == 'symbols':
                                if elementstr == symbolstr:
                                    inputs['symbols'].append('')
                                else:
                                    inputs['symbols'].append(symbolstr)
                            else:
                                inputs[key].append('')
    
    # Build without potentials
    else:
        # Loop over all references
        for i in reference_df.index:
            reference = references[i]
            content_dict[reference.name] = reference.build_model()
            
            # Loop over input keys
            for key in keys:
                if key == 'load_file':
                    inputs['load_file'].append(reference.name+'.json')
                elif key == 'load_content':
                    inputs['load_content'].append(f'record {reference.name}')
                elif key == 'load_style':
                    inputs['load_style'].append('system_model')
                elif key == 'family':
                    inputs['family'].append(reference.name)
                else:
                    inputs[key].append('')
    
    return inputs, content_dict

def symbolstrings(reference_symbols, potential_elements, potential_symbols):
    
    reference_symbol = reference_symbols[0]
    matches = np.where(np.asarray(potential_elements, dtype=str) == str(reference_symbol))[0]
    for match in matches:
        pot_symbol = potential_symbols[match]
        if len(reference_symbols) == 1:
            yield pot_symbol
        else:
            for child in symbolstrings(reference_symbols[1:], potential_elements, potential_symbols):
                yield pot_symbol + ' ' + child      