#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard library imports
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
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

# Define record_style
record_style = 'calculation_crystal_space_group'

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
    
    # Save data model of results
    script = os.path.splitext(os.path.basename(__file__))[0]
    
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
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
    ucell = spglib.standardize_cell(system.dump('spglib_cell'),
                                    to_primitive=to_primitive,
                                    no_idealize=no_idealize, symprec=symprec)
    
    # Convert back to atomman systems and normalize
    ucell = am.load('spglib_cell', ucell, symbols=system.symbols)
    ucell.atoms.pos -= ucell.atoms.pos[0]
    ucell = ucell.normalize()
    
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
    
    natoms = str(ucell.natoms)
    pearson = crystalclass + latticetype + natoms
    
    # Return results
    results_dict = spg_type
    results_dict['ucell'] = ucell
    results_dict['hall_number'] = sym_data['hall_number']
    results_dict['wyckoffs'] = sym_data['wyckoffs']
    results_dict['pearson'] = pearson
    
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
    
    # Set calculation UUID
    if UUID is not None: 
        input_dict['calc_key'] = UUID
    else: 
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.interpret('units', input_dict)
    
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
    iprPy.input.interpret('atomman_systemload', input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])