#!/usr/bin/env python
# coding: utf-8
import argparse

from iprPy.database import BaseEmperorPrepare
from iprPy.input import boolean

class CTCMSEmperorPrepare(BaseEmperorPrepare):
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
            'lammps_command': '/toolbox/lmh1/LAMMPS/2022_06_23/build/lmp',

            # MPI command to use with the LAMMPS executable(s)
            # Blank string will always run in serial
            'mpi_command': 'mpirun -n {np_per_runner}',


            ### Optional alternate LAMMPS commands ###
            # SNAP version 1 needs LAMMPS between 8 Oct 2014 and 30 May 2017.
            'lammps_command_snap_1': '/toolbox/lmh1/LAMMPS/2017_03_31/src/lmp_mpi',

            # SNAP version 2 needs LAMMPS between 3 Dec 2018 and 12 June 2019.
            'lammps_command_snap_2': '/toolbox/lmh1/LAMMPS/2019_06_05/src/lmp_mpi',

            # Some older implementations of potentials need LAMMPS before 30 Oct 2019.
            'lammps_command_old': '/toolbox/lmh1/LAMMPS/2019_06_05/src/lmp_mpi',

            # LAMMPS built with an external module to run aenet potentials
            'lammps_command_aenet': '/toolbox/lmh1/LAMMPS/2022_06_23_aenet/src/lmp_mpi',

            # LAMMPS built with an external module to run pinn potentials
            'lammps_command_pinn': '/toolbox/lmh1/LAMMPS/2020_10_29_pinn/src/lmp_mpi',

        }
        return terms


    def build_prepare_pool(self):
        """Method to map prepare pool methods to pool numbers"""
        self.prepare_pool[1] = self.prepare_pool_1
        self.prepare_pool[2] = self.prepare_pool_2
        self.prepare_pool[3] = self.prepare_pool_3
        self.prepare_pool[4] = self.prepare_pool_4
        self.prepare_pool[5] = self.prepare_pool_5
        self.prepare_pool[6] = self.prepare_pool_6
        self.prepare_pool[7] = self.prepare_pool_7
        self.prepare_pool[8] = self.prepare_pool_8
        self.prepare_pool[9] = self.prepare_pool_9
        self.prepare_pool[10] = self.prepare_pool_10
        self.prepare_pool[11] = self.prepare_pool_11
        self.prepare_pool[12] = self.prepare_pool_12
        self.prepare_pool[13] = self.prepare_pool_13
        self.prepare_pool[14] = self.prepare_pool_14
        self.prepare_pool[15] = self.prepare_pool_15
        self.prepare_pool[16] = self.prepare_pool_16

    def prepare_pool_1(self, debug=False, **kwargs):
        """Pool #1: Basic potential evaluations and scans"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'isolated_atom diatom_scan E_vs_r_scan:bop E_vs_r_scan',
            'run_directory': 'iprhub_1',
            'np_per_runner': '1',
            'num_pots': '100',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_2(self, debug=False, **kwargs):
        """Pool #2: Relax round 1"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_box relax_static relax_dynamic',
            'run_directory': 'iprhub_2',
            'np_per_runner': '1',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_3(self, debug=False, **kwargs):
        """Pool #3: Relax round 2 (static from dynamic)"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_static:from_dynamic',
            'run_directory': 'iprhub_3',
            'np_per_runner': '1',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_4(self, debug=False, **kwargs):
        """
        Pool #4: Space group

        Pool-specific kwargs
        ------------------------
        include_references : bool, optional
            If True then prototype and reference structures will be included in the prepare.
            If False (default) then only relaxation results will be prepared.
        """

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'crystal_space_group:relax',
            'run_directory': 'iprhub_4',
            'np_per_runner': '1',
            'num_pots': '50',
        }

        # Add prototype and reference branches if wanted
        include_references = boolean(kwargs.pop('include_references', False))
        if include_references:
            pool_params['styles'] = 'crystal_space_group:relax crystal_space_group:prototype crystal_space_group:reference'

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_5(self, debug=False, **kwargs):
        """Pool #5: Static elastic constants"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'elastic_constants_static',
            'run_directory': 'iprhub_5',
            'np_per_runner': '1',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_6(self, debug=False, **kwargs):
        """Pool #6: Phonons"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'phonon',
            'run_directory': 'iprhub_6',
            'np_per_runner': '1',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_7(self, debug=False, **kwargs):
        """Pool #7: Point defects and surfaces"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'point_defect_static surface_energy_static',
            'run_directory': 'iprhub_7',
            'np_per_runner': '1',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_8(self, debug=False, **kwargs):
        """Pool #8: Stacking faults"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'stacking_fault_map_2D',
            'run_directory': 'iprhub_8',
            'np_per_runner': '1',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_9(self, debug=False, **kwargs):
        """Pool #9: Dislocation monopoles"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'dislocation_monopole:fcc_edge_100 dislocation_monopole:bcc_screw dislocation_monopole:bcc_edge dislocation_monopole:bcc_edge_112',
            'run_directory': 'iprhub_9',
            'np_per_runner': '16',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_10(self, debug=False, **kwargs):
        """Pool #10: Dislocation arrays"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'dislocation_periodic_array:fcc_edge_mix dislocation_periodic_array:fcc_screw',
            'run_directory': 'iprhub_10',
            'np_per_runner': '16',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_11(self, debug=False, **kwargs):
        """Pool #11: Dynamic relax at 50K"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_dynamic:at_temp_50K',
            'run_directory': 'iprhub_11',
            'np_per_runner': '16',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)

        # If sizemults is manually specified, use it
        if 'sizemults' in kwargs:

            self.database.master_prepare(**prepare_params)

        # Otherwise dynamically change sizemults based on natoms
        else:
            sdict = {}
            sdict[16] = [1, 1]
            sdict[13] = [2, 2]
            sdict[12] = [3, 3]
            sdict[10] = [4, 5]
            sdict[9] = [6, 7]
            sdict[8] = [8, 11]
            sdict[7] = [12, 18]
            sdict[6] = [19, 31]
            sdict[5] = [32, 62]
            sdict[4] = [63, 148]
            sdict[3] = [149, 499]
            sdict[2] = [500, 1000]

            # Loop over dynamic sizemult sets
            for s in sdict:
                nmin, nmax = sdict[s]
                print(f'Preparing for natoms between {nmin} and {nmax}')

                prepare_params['sizemults'] = f'{s} {s} {s}'
                natoms = list(range(nmin, nmax+1))

                # Find all parents within the sizemults range
                parent_natoms_df = self.database.get_records_df('relaxed_crystal', method='dynamic',
                                                                standing='good', natoms=natoms)
                prepare_params['parent_key'] = parent_natoms_df.key.tolist()

                self.database.master_prepare(debug=debug, **prepare_params)

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
            'np_per_runner': '16',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 3000))

        # Compile prepare_params
        prepare_params = self.compile_prepare_params(pool_params, **kwargs)

        # Loop from max temperature down to 50
        for temperature in range(100, max_temperature+50, 50):
            
            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_13(self, debug: bool = False, **kwargs):
        """
        Pool #13: Free energy solid

        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'free_energy',
            'run_directory': 'iprhub_13',
            'np_per_runner': '16',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 3000))

        # Compile prepare_params
        prepare_params = self.compile_prepare_params(pool_params, **kwargs)

        # Loop from max temperature down to 50
        for temperature in range(100, max_temperature+50, 50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_14(self, debug=False, **kwargs):
        """Pool #14: Relax liquid at melt"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_liquid:melt',
            'run_directory': 'iprhub_14',
            'np_per_runner': '16',
            'num_pots': '50',
        }

        prepare_params = self.compile_prepare_params(pool_params, **kwargs)
        self.database.master_prepare(**prepare_params)

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
            'styles': 'relax_liquid:change_temp',
            'run_directory': 'iprhub_15',
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
            prepare_params['temperature'] = str(temperature - 50)
            prepare_params['temperature_melt'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_16(self, debug: bool = False, **kwargs):
        """
        Pool #16: Free energy liquid

        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'free_energy_liquid',
            'run_directory': 'iprhub_16',
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

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            self.database.master_prepare(debug=debug, **prepare_params)



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

    emperor = CTCMSEmperorPrepare(args.database)
    emperor.prepare(args.pool_number, input_script=args.input_script, debug=args.debug)