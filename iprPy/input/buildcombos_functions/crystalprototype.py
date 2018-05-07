# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

# iprPy imports
from .interatomicpotential import interatomicpotential

__all__ = ['crystalprototype']

def crystalprototype(database, keys, record='crystal_prototype', query=None,
              **kwargs):
    
    # Get potentials
    if 'potential_file' in keys:
        potential_kwargs = {}
        for key in list(kwargs.keys()):
            if key[:10] == 'potential_':
                potential_kwargs[key[10:]] = kwargs.pop(key)
        
        pot_inputs = interatomicpotential(database, **potential_kwargs)
        
        potentials = {}
        potsymbols = {}
        for i in range(len(pot_inputs['potential_dir'])):
            potentials[pot_inputs['potential_dir'][i]] = pot_inputs['potential_content'][i]
            potsymbols[pot_inputs['potential_dir'][i]] = lmp.Potential(pot_inputs['potential_content'][i]).symbols
    
    else:
        potentials = {'empty': ''}
        potsymbols = {'empty': None}
    
    prototypes, prototype_df = database.get_records(style=record, return_df=True,
                                                 query=query, **kwargs)
    
    inputs = {}
    for key in keys:
        inputs[key] = []
    
    for i, prototype_info in prototype_df.iterrows():
        prototype = prototypes[i]
        natypes = prototype_info.natypes
        
        for potential_name in potentials:
            potential_content = potentials[potential_name]
            allsymbols = potsymbols[potential_name]
            
            for symbols in itersymbols(allsymbols, natypes):
                for key in keys:
                    if key == 'potential_file':
                        inputs['potential_file'].append(potential_name + '.json')
                    elif key == 'potential_content':
                        inputs['potential_content'].append(potential_content)
                    elif key == 'potential_dir':
                        inputs['potential_dir'].append(potential_name)
                    elif key == 'load_file':
                        inputs['load_file'].append(prototype.name+'.json')
                    elif key == 'load_content':
                        inputs['load_content'].append('record ' + prototype.name)
                    elif key == 'load_style':
                        inputs['load_style'].append('system_model')
                    elif key == 'family':
                        inputs['family'].append(prototype.name)
                    elif key == 'symbols':
                        inputs['symbols'].append(' '.join(symbols).strip())
                    else:
                        inputs[key].append('')
    
    return inputs

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