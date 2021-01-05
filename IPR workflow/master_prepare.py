#!/usr/bin/env python
# coding: utf-8

# Standard Python libraries
from copy import deepcopy
import sys
from pathlib import Path
from datetime import date

import numpy as np

import atomman.lammps as lmp

import iprPy

from iprPy.workflow import prepare, process, fix_lammps_versions, test_lammps_versions
from iprPy.input import boolean
from iprPy.tools import aslist

def main(*args):
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f)

    # Get database_name
    database_name = input_dict.pop('database_name')

    # Get commands
    commands = {}
    commands['mpi_command'] = input_dict.pop('mpi_command')
    allkeys = list(input_dict.keys())
    for key in allkeys:
        if key[:14] == 'lammps_command':
            commands[key] = input_dict.pop(key)

    # Get pools
    all_styles = aslist(input_dict.pop('styles'))
    all_np_per_runner = aslist(input_dict.pop('np_per_runner'))
    all_run_directory_name = aslist(input_dict.pop('run_directory_name'))
    if len(all_styles) != len(all_np_per_runner) or len(all_styles) != len(all_run_directory_name):
        raise ValueError('Equal numbers of styles, np_per_runner and run_directory_name lines required')
    pools = []
    for styles, np_per_runner, run_directory_name in zip(all_styles, all_np_per_runner, all_run_directory_name):
        pool = {}
        pool['styles'] = styles.split()
        pool['np_per_runner'] = int(np_per_runner)
        pool['run_directory_name'] = run_directory_name
        pools.append(pool)

    # Get pot_kwargs:
    pot_kwargs = {}
    allkeys = list(input_dict.keys())
    for key in allkeys:
        if key[:10] == 'potential_':
            pot_kwargs[key[10:]] = input_dict.pop(key)

    # Get test_commands
    test_commands = boolean(input_dict.pop('test_commands', True))

    master_prepare(database_name, commands, pools, pot_kwargs=pot_kwargs,
                   test_commands=test_commands, **input_dict)

def master_prepare(database_name, commands, pools, pot_kwargs=None,
                   test_commands=True, **global_kwargs):
    """
    Primary workflow script for preparing calculations consistent with the
    NIST Interatomic Potentials Repository workflow.

    Parameters
    ----------
    database_name : str
        The name of the database that the calculations will be prepared for.
    commands : dict
        Lists mpi_command, the primary lammps_command and any alternate lammps
        commands
    pools : list
        Indicates the pools for preparing the calculations in.  Each pool
        is a dict containing styles (list of str), np_per_runner (int), and
        run_directory_name (str).
    pot_kwargs : dict, optional
        Any potential limiting parameters.
    test_commands : bool, optional
        If True, the lammps_commands listed in run_command_filename will be
        tested before calculations are prepared.  Default value is True.
    global_kwargs : any
        Any other kwargs will be taken as global parameters to apply to all
        calculations.  
    """
    
    global_kwargs = {}
    global_kwargs['lammps_command'] = commands['lammps_command']

    # Load pot kwargs
    if pot_kwargs is None:
        pot_kwargs = {}

    # Loop over calculation pools
    for pool in pools:
        run_directory_name = pool['run_directory_name']
        np_per_runner = pool['np_per_runner']
        if np_per_runner > 1:
            mpi_command = commands['mpi_command'].format(np_per_runner=np_per_runner)
        else:
            mpi_command = ''

        # Loop over styles to prepare in that pool
        for style in pool['styles']:
            prepare_switch(style, database_name, run_directory_name,
                           pot_kwargs=pot_kwargs,
                           mpi_command=mpi_command, **global_kwargs)

        # Fix lammps versions in the pool
        fix_lammps_versions(run_directory_name, commands)


def prepare_switch(style, database_name, run_directory_name, pot_kwargs=None,
                   **kwargs):
    """
    Wrapper function that calls the corresponding prepare function for a given
    style.

    Parameters
    ----------
    style : str
        The calculation (sub)style to prepare.
    database_name : str
        The name of the pre-set database to use.
    run_directory_name : str
        The name of the pre-set run_directory to use.
    pot_kwargs : dict, optional
        Values for potential-specific limiters.
    **kwargs : str or list, optional
        Values for any additional or replacement prepare parameters.
    """
    # Define dict mapping style to prepare function
    switch = {}
    switch['isolated_atom'] = prepare.isolated_atom.main
    switch['diatom_scan'] = prepare.diatom_scan.main
    switch['E_vs_r_scan'] = prepare_E_vs_r_scan
    switch['relax_box'] = prepare.relax_box.main
    switch['relax_dynamic'] = prepare.relax_dynamic.main
    switch['relax_static'] = prepare.relax_static.main
    switch['relax_static_from_dynamic'] = prepare.relax_static.from_dynamic
    switch['crystal_space_group'] = prepare_crystal_space_group
    switch['elastic_constants_static'] = prepare.elastic_constants_static.main
    switch['phonon'] = prepare.phonon.main
    switch['point_defect_static'] = prepare_point_defect_static
    switch['surface_energy_static'] = prepare_surface_energy_static
    switch['stacking_fault_map_2D'] = prepare_stacking_fault_map_2D
    switch['dislocation_monopole'] = prepare_dislocation_monopole
    switch['dislocation_periodic_array'] = prepare_dislocation_periodic_array

    # Shorten calculation-specific kwargs
    for key in kwargs:
        if key[:len(style)] == style:
            kwargs[key[:len(style)].lstrip('_')] = kwargs.pop(key)

    # Call the corresponding function
    switch[style](database_name, run_directory_name, pot_kwargs=pot_kwargs,
                  **kwargs)

def prepare_E_vs_r_scan(database_name, run_directory_name, pot_kwargs=None,
                        **kwargs):
    """
    Calls main and bop versions of prepare E_vs_r_scan
    """
    # Deep copy pot_kwargs to allow manipulation
    pot_kwargs = deepcopy(pot_kwargs)

    # Extract pair_style from pot_kwargs
    pair_style = pot_kwargs.pop('pair_style', None)

    # Prepare bop calculations
    if pair_style is None or pair_style=='bop' or 'bop' in pair_style:
        prepare.E_vs_r_scan.bop(database_name, run_directory_name,
                                pot_kwargs=pot_kwargs, **kwargs)

    # Prepare everything else
    if pair_style is not None:
        pot_kwargs['pair_style'] = pair_style
    prepare.E_vs_r_scan.main(database_name, run_directory_name, 
                             pot_kwargs=pot_kwargs, **kwargs)

def prepare_crystal_space_group(database_name, run_directory_name,
                                pot_kwargs=None, **kwargs):
    """
    Calls prototype, reference and relax versions of prepare crystal_space_group
    """
    # Prepare using prototype, reference and relax references
    #prepare.crystal_space_group.prototype(database_name, run_directory_name,
    #                             pot_kwargs=pot_kwargs, **kwargs)
    #prepare.crystal_space_group.reference(database_name, run_directory_name,
    #                             pot_kwargs=pot_kwargs, **kwargs)
    prepare.crystal_space_group.relax(database_name, run_directory_name,
                                 pot_kwargs=pot_kwargs, **kwargs)

def prepare_point_defect_static(database_name, run_directory_name,
                                pot_kwargs=None, **kwargs):
    """
    Calls prepare point_defect_static for each unique family
    """
    # Load database
    database = iprPy.load_database(database_name)
    
    # Build kwargs for each family
    families = np.unique(database.get_records_df(style='point_defect').family)
    for family in families:
        print(family, flush=True)        
        kwargs['parent_family'] = kwargs['defect_family'] = family 
        
        # Prepare
        prepare.point_defect_static.main(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)

def prepare_surface_energy_static(database_name, run_directory_name,
                                pot_kwargs=None, **kwargs):
    """
    Calls prepare surface_energy_static for each unique family
    """
    # Load database
    database = iprPy.load_database(database_name)
    
    # Build kwargs for each family
    families = np.unique(database.get_records_df(style='free_surface').family)
    for family in families:
        print(family, flush=True)        
        kwargs['parent_family'] = kwargs['defect_family'] = family 
        
        # Prepare
        prepare.surface_energy_static.main(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)

def prepare_stacking_fault_map_2D(database_name, run_directory_name,
                                pot_kwargs=None, **kwargs):
    """
    Calls prepare stacking_fault_map_2D for each unique family
    """
    # Load database
    database = iprPy.load_database(database_name)
    
    # Build kwargs for each family
    families = np.unique(database.get_records_df(style='stacking_fault').family)
    for family in families:
        print(family, flush=True)        
        kwargs['parent_family'] = kwargs['defect_family'] = family 
        
        # Prepare
        prepare.stacking_fault_map_2D.main(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)

def prepare_dislocation_monopole(database_name, run_directory_name,
                                pot_kwargs=None, **kwargs):
    """
    Calls prepare dislocation_monopole for each dislocation type
    """
    # Prepare
    prepare.dislocation_monopole.bcc_screw(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)
    prepare.dislocation_monopole.bcc_edge(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)
    prepare.dislocation_monopole.bcc_edge_112(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)
    prepare.dislocation_monopole.fcc_edge_100(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)

def prepare_dislocation_periodic_array(database_name, run_directory_name,
                                pot_kwargs=None, **kwargs):
    """
    Calls prepare dislocation_periodic_array for each dislocation type
    """
    
    # Prepare
    prepare.dislocation_periodic_array.fcc_edge_mix(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)
    prepare.dislocation_periodic_array.fcc_screw(database_name, run_directory_name,
                                           pot_kwargs=pot_kwargs, **kwargs)

if __name__ == '__main__':
    main(*sys.argv[1:])