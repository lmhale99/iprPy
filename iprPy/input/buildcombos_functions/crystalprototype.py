import potentials

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

__all__ = ['crystalprototype']

def crystalprototype(database, keys, content_dict=None, 
                     record='crystal_prototype', **kwargs):
    
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

    # Fetch prototype records
    prototypes, prototype_df = database.get_records(style=record, return_df=True,
                                                    **kwargs)
    print(len(prototype_df), 'matching crystal prototypes found')
    if len(prototype_df) == 0:
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

        # Loop over prototypes
        for i in prototype_df.index:
            prototype = prototypes[i]
            prototype_series = prototype_df.loc[i]
            content_dict[prototype.name] = prototype.model
            natypes = prototype_series.natypes
            
            # Loop over potentials
            for j in lmppots_df.index:
                lmppot = lmppots[j]
                lmppot_series = lmppots_df.loc[j]
                if lmppot.name not in content_dict:
                    content_dict[lmppot.name] = lmppot.model
                allsymbols = lmppot_series.symbols
                
                # Loop over all symbol combinations
                for symbols in itersymbols(allsymbols, natypes):
                    
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
                            inputs['load_file'].append(f'{prototype.name}.json')
                        elif key == 'load_content':
                            inputs['load_content'].append(f'record {prototype.name}')
                        elif key == 'load_style':
                            inputs['load_style'].append('system_model')
                        elif key == 'family':
                            inputs['family'].append(prototype.name)
                        elif key == 'symbols':
                            inputs['symbols'].append(' '.join(symbols).strip())
                        else:
                            inputs[key].append('')
    
    # Build without potentials
    else:
        # Loop over prototypes
        for i in prototype_df.index:
            prototype = prototypes[i]
            content_dict[prototype.name] = prototype.model
            
            # Loop over input keys
            for key in keys:
                if key == 'load_file':
                    inputs['load_file'].append(f'{prototype.name}.json')
                elif key == 'load_content':
                    inputs['load_content'].append(f'record {prototype.name}')
                elif key == 'load_style':
                    inputs['load_style'].append('system_model')
                elif key == 'family':
                    inputs['family'].append(prototype.name)
                else:
                    inputs[key].append('')
    
    return inputs, content_dict

def itersymbols(symbols, nsites):
    if symbols is None:
        yield ['' for i in range(nsites)]
    else:
        if nsites == 0:
            yield []
        else:
            for i in range(len(symbols)):
                for subset in itersymbols(symbols[:i]+symbols[i+1:], nsites-1):
                    yield [symbols[i]] + subset