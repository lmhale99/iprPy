#!/usr/bin/env python
# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
import sys
import uuid
import random
import datetime
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://atztogo.github.io/spglib/python-spglib.html
import spglib

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define calculation metadata
calculation_style = 'crystal_space_group'
record_style = f'calculation_{calculation_style}'
script = Path(__file__).stem
pkg_name = f'iprPy.calculation.{calculation_style}.{script}'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Run crystal_compare to compare two systems based on spacegroup info
    results_dict = crystal_space_group(input_dict['ucell'],
                                       symprec=input_dict['symmetryprecision'],
                                       to_primitive=input_dict['primitivecell'],
                                       no_idealize=not input_dict['idealcell'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def crystal_space_group(system, symprec=1e-5, to_primitive=False,
                        no_idealize=False):
    """
    Uses spglib to evaluate space group information for a given system.
    
    Parameters
    ----------
    system : atomman.System
        The system to analyze.
    symprec : float
        Absolute length tolerance to use in identifying symmetry of atomic
        sites and system boundaries.
    to_primitive : bool
        Indicates if the returned unit cell is conventional (False) or
        primitive (True). Default value is False.
    no_idealize : bool
        Indicates if the atom positions in the returned unit cell are averaged
        (True) or idealized based on the structure (False).  Default value is
        False.
    
    Returns
    -------
    dict
        Results dictionary containing space group information and an associated
        unit cell system.
    """
    # Identify the standardized unit cell representation
    sym_data = spglib.get_symmetry_dataset(system.dump('spglib_cell'), symprec=symprec)
    ucell = spglib.standardize_cell(system.dump('spglib_cell'),
                                    to_primitive=to_primitive,
                                    no_idealize=no_idealize, symprec=symprec)
    
    # Convert back to atomman systems and normalize
    ucell = am.load('spglib_cell', ucell, symbols=system.symbols)
    ucell.atoms.pos -= ucell.atoms.pos[0]
    ucell = ucell.normalize()
    
    # Throw error if natoms > 2000
    natoms = ucell.natoms
    if natoms > 2000:
        raise RuntimeError('too many positions')

    # Average extra per-atom properties by mappings to primitive
    for index in np.unique(sym_data['mapping_to_primitive']):
        for key in system.atoms.prop():
            if key in ['atype', 'pos']:
                continue
            value = system.atoms.view[key][sym_data['mapping_to_primitive'] == index].mean()
            if key not in ucell.atoms.prop():
                ucell.atoms.view[key] = np.zeros_like(value)
            ucell.atoms.view[key][sym_data['std_mapping_to_primitive'] == index] = value
    
    # Get space group metadata
    sym_data = spglib.get_symmetry_dataset(ucell.dump('spglib_cell'))
    spg_type = spglib.get_spacegroup_type(sym_data['hall_number'])
    
    # Generate Pearson symbol
    if spg_type['number'] <= 2:
        crystalclass = 'a'
    elif spg_type['number'] <= 15:
        crystalclass = 'm'
    elif spg_type['number'] <= 74:
        crystalclass = 'o'
    elif spg_type['number'] <= 142:
        crystalclass = 't'
    elif spg_type['number'] <= 194:
        crystalclass = 'h'
    else:
        crystalclass = 'c'
    
    latticetype = spg_type['international'][0]
    if latticetype in ['A', 'B']:
        latticetype = 'C'
    
    pearson = crystalclass + latticetype + str(natoms)
    
    # Generate Wyckoff fingerprint
    fingerprint_dict = {} 
    usites, uindices = np.unique(sym_data['equivalent_atoms'], return_index=True)
    for usite, uindex in zip(usites, uindices):
        atype = ucell.atoms.atype[uindex]
        wykoff = sym_data['wyckoffs'][uindex]
        if atype not in fingerprint_dict:
            fingerprint_dict[atype] = [wykoff]
        else:
            fingerprint_dict[atype].append(wykoff)
    fingerprint = []
    for atype in sorted(fingerprint_dict.keys()):
        fingerprint.append(''.join(sorted(fingerprint_dict[atype])))
    fingerprint = ' '.join(fingerprint)

    # Return results
    results_dict = spg_type
    results_dict['ucell'] = ucell
    results_dict['hall_number'] = sym_data['hall_number']
    results_dict['wyckoffs'] = sym_data['wyckoffs']
    results_dict['equivalent_atoms'] = sym_data['equivalent_atoms']
    results_dict['pearson'] = pearson
    results_dict['wyckoff_fingerprint'] = fingerprint
    
    return results_dict
    
def process_input(input_dict, UUID=None, build=True):
    """
    Processes str input parameters, assigns default values if needed, and
    generates new, more complex terms as used by the calculation.
    
    Parameters
    ----------
    input_dict :  dict
        Dictionary containing the calculation input parameters with string
        values.  The allowed keys depends on the calculation style.
    UUID : str, optional
        Unique identifier to use for the calculation instance.  If not 
        given and a 'UUID' key is not in input_dict, then a random UUID4 
        hash tag will be assigned.
    build : bool, optional
        Indicates if all complex terms are to be built.  A value of False
        allows for default values to be assigned even if some inputs 
        required by the calculation are incomplete.  (Default is True.)
    """
    # Set script's name
    input_dict['script'] = script

    # Set calculation UUID
    if UUID is not None: 
        input_dict['calc_key'] = UUID
    else: 
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.subset('units').interpret(input_dict)
    
    # These are calculation-specific default strings
    # None for this calculation
    
    # These are calculation-specific default booleans
    input_dict['primitivecell'] = iprPy.input.boolean(input_dict.get('primitivecell', False))
    input_dict['idealcell'] = iprPy.input.boolean(input_dict.get('idealcell', True))
    
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    input_dict['symmetryprecision'] = iprPy.input.value(input_dict, 'symmetryprecision',
                                            default_unit=input_dict['length_unit'],
                                            default_term='0.01 angstrom')
    
    # Load system
    iprPy.input.subset('atomman_systemload').interpret(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])