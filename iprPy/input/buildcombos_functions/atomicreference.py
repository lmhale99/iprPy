# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import glob

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

# iprPy imports
from ... import rootdir
from ...tools import aslist
from .interatomicpotential import interatomicpotential

__all__ = ['atomicreference']

def atomicreference(database, keys, lib_directory=None, elements=None, **kwargs):
    
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
        potsymbols = None
    
    if lib_directory is None:
        lib_directory = os.path.join(os.path.dirname(rootdir), 'library')
    
    if elements is not None:
        elements = aslist(elements)
        allelements = set()
        for i in range(len(elements)):
            e = elements[i].split()
            allelements.update(e)
            e.sort()
            elements[i] = '-'.join(e)
    
    if potsymbols is None:
        if elements is not None:
            potsymbols = {'empty': list(allelements)}
        else:
            potsymbols = {'empty': ['*']}
    
    inputs = {}
    for key in keys:
        inputs[key] = []
    
    # Get reference file names for searching
    names = aslist(kwargs.get('name', '*'))
    
    for potential_name in potentials:
        potential_content = potentials[potential_name]
        allsymbols = potsymbols[potential_name]
        allsymbols.sort()
        
        for symbols in subsets(allsymbols):
            symbol_str = '-'.join(symbols)
            if elements is not None and symbol_str != '*'  and symbol_str not in elements:
                continue
            for name in names:
                for fname in glob.iglob(os.path.join(lib_directory, 'ref', symbol_str, name)):
                    load_file = os.path.basename(fname)
                    load_name, load_ext = os.path.splitext(load_file)
                    with open(fname) as f:
                        load_content = f.read()
                    
                    load_style = load_ext[1:]
                    if load_style in ['xml', 'json']: load_style = 'system_model'
                    elif load_style == 'dump': load_style = 'atom_dump'
                    elif load_style == 'dat': load_style = 'atom_data'
                    
                    for key in keys:
                        if key == 'potential_file':
                            inputs['potential_file'].append(potential_name + '.json')
                        elif key == 'potential_content':
                            inputs['potential_content'].append(potential_content)
                        elif key == 'potential_dir':
                            inputs['potential_dir'].append(potential_name)
                        elif key == 'load_file':
                            inputs['load_file'].append(load_file)
                        elif key == 'load_content':
                            inputs['load_content'].append('file ' + os.path.abspath(fname))
                        elif key == 'load_style':
                            inputs['load_style'].append(load_style)
                        elif key == 'family':
                            inputs['family'].append(load_name)
                        else:
                            inputs[key].append('')
    
    return inputs

# Define subset generator
def subsets(fullset):
    for i, item in enumerate(fullset):
        yield [item]
        if len(fullset) > 1:
            for subset in subsets(fullset[i+1:]):
                yield [item] + subset