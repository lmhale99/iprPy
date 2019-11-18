# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

# iprPy imports
from ...analysis import assign_currentIPR
from .. import boolean

__all__ = ['crystalprototype']

def crystalprototype(database, keys, content_dict=None, 
                     record='crystal_prototype', query=None, **kwargs):
    
    if content_dict is None:
        content_dict = {}

    # Check if potential info is in keys
    if 'potential_file' in keys or 'potential_dir' in keys:
        include_potentials = True
        
        # Extract kwargs starting with "potential"
        potential_kwargs = {}
        for key in list(kwargs.keys()):
            if key[:10] == 'potential_':
                potential_kwargs[key[10:]] = kwargs.pop(key)
    else:
        include_potentials = False

    # Fetch prototype records
    prototypes, prototype_df = database.get_records(style=record, return_df=True,
                                                 query=query, **kwargs)
    
    # Initialize inputs keys
    inputs = {}
    for key in keys:
        inputs[key] = []
    
    # Build with potentials
    if include_potentials:

        # Pull out potential get_records parameters
        potential_record = potential_kwargs.pop('record', 'potential_LAMMPS')
        potential_query = potential_kwargs.pop('query', None)
        currentIPR = potential_kwargs.pop('currentIPR', potential_record=='potential_LAMMPS')
        currentIPR = boolean(currentIPR)
        
        # Fetch potential records 
        potentials, potential_df = database.get_records(style=potential_record, return_df=True,
                                                        query=potential_query, **potential_kwargs)
        
        # Filter by currentIPR (note that DataFrame index is unchanged)
        if currentIPR:
            assign_currentIPR(pot_df=potential_df)
            potential_df = potential_df[potential_df.currentIPR == True]

        # Loop over prototypes
        for i, prototype_series in prototype_df.iterrows():
            prototype = prototypes[i]
            content_dict[prototype.name] = prototype.content
            natypes = prototype_series.natypes
            
            # Loop over potentials
            for j, potential_series in potential_df.iterrows():
                potential = potentials[j]
                content_dict[potential.name] = potential.content
                allsymbols = potential_series.symbols
                
                # Loop over all symbol combinations
                for symbols in itersymbols(allsymbols, natypes):
                    
                    # Loop over input keys
                    for key in keys:
                        if key == 'potential_file':
                            inputs['potential_file'].append(f'{potential.name}.json')
                        elif key == 'potential_content':
                            inputs['potential_content'].append(f'record {potential.name}')
                        elif key == 'potential_dir':
                            inputs['potential_dir'].append(potential.name)
                        elif key == 'potential_dir_content':
                            inputs['potential_dir_content'].append(f'tar {potential.name}')
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
        for i, prototype_series in prototype_df.iterrows():
            prototype = prototypes[i]
            content_dict[prototype.name] = prototype.content
            
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