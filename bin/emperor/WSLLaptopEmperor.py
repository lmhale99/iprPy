#!/usr/bin/env python
# coding: utf-8
import argparse

from iprPy.database import BaseEmperorPrepare
from iprPy.input import boolean

class WSLEmperorPrepare(BaseEmperorPrepare):
    """
    Emperor prepare class for the CTCMS machines
    """

    @property
    def database_name(self):
        """str: The name of the default database to use"""
        return 'iprhub'

    @property
    def commands(self):
        """
        Specifies the LAMMPS command(s) and mpi command to use with the calculations.
        """
        terms = {

            ### Required commands ###
            # Primary LAMMPS executable (machine-specific location)
            'lammps_command': '/home/lmh1/LAMMPS/2022-06-23/src/lmp_mpi',

            # MPI command to use with the LAMMPS executable(s)
            # Blank string will always run in serial
            'mpi_command': 'mpiexec -n {np_per_runner}',


            ### Optional alternate LAMMPS commands ###
            # SNAP version 1 needs LAMMPS between 8 Oct 2014 and 30 May 2017.
            'lammps_command_snap_1': '/home/lmh1/LAMMPS/2017-03-31/src/lmp_mpi',

            # SNAP version 2 needs LAMMPS between 3 Dec 2018 and 12 June 2019.
            'lammps_command_snap_2': '/home/lmh1/LAMMPS/2019-06-05/src/lmp_mpi',

            # Some older implementations of potentials need LAMMPS before 30 Oct 2019.
            'lammps_command_old': '/home/lmh1/LAMMPS/2019-06-05/src/lmp_mpi',

            # LAMMPS built with an external module to run aenet potentials
            #'lammps_command_aenet': '/toolbox/lmh1/LAMMPS/2022_06_23_aenet/src/lmp_mpi',

            # LAMMPS built with an external module to run pinn potentials
            #'lammps_command_pinn': '/toolbox/lmh1/LAMMPS/2020_10_29_pinn/src/lmp_mpi',
        }
        return terms

    def build_prepare_pool(self):
        """Method to map prepare pool methods to pool numbers"""
        self.prepare_pool[12] = self.prepare_pool_12
        self.prepare_pool[15] = self.prepare_pool_15

    def prepare_pool_12(self, debug: bool = False, **kwargs):
        """
        Pool #12: Relax dynamic, increasing T

        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_dynamic:at_temp',
            'run_directory': 'iprhub_12',
            'np_per_runner': '8',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 3000))

        # Compile prepare_params
        prepare_params = self.compile_prepare_params(pool_params, **kwargs)

        # Loop from 100 up to max temperature
        for temperature in range(100, max_temperature+50, 50):
            
            # Set run temperature
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names = self.database.master_prepare(debug=debug, **prepare_params)

            # Run the prepared calculations
            for calc_name in calc_names:
                self.database.runner(pool_params['run_directory'], calc_name=calc_name)

    def prepare_pool_15(self, debug: bool = False, **kwargs):
        """
        Pool #15: Relax liquid, decreasing T

        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_liquid_redo:change_temp',
            'run_directory': 'iprhub_12',
            'np_per_runner': '8',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 6100))

        # Compile prepare_params
        prepare_params = self.compile_prepare_params(pool_params, **kwargs)

        # Loop from max temperature down to 50
        for temperature in range(max_temperature, 0, -50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)
            prepare_params['temperature_melt'] = str(temperature + 50)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names = self.database.master_prepare(debug=debug, **prepare_params)
            
            # Run the prepared calculations
            for calc_name in calc_names:
                self.database.runner(pool_params['run_directory'], calc_name=calc_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Command line options for Emperor prepare on CTCMS')
    parser.add_argument('pool_number', type=int,
                        help='The calculation pool to prepare')
    parser.add_argument('-d', '--database', default=None,
                        help='Name of the database to prepare with')
    parser.add_argument('-i', '--input_script', default=None,
                        help='File containing modification parameters to use')
    parser.add_argument('--debug', action='store_true',
                        help='raise errors for invalid calculations rather than skipping')
    args = parser.parse_args()

    emperor = WSLEmperorPrepare(args.database)
    emperor.prepare(args.pool_number, input_script=args.input_script, debug=args.debug)
