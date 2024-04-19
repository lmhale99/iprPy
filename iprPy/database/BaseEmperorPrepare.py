from typing import Union
from ..input import parse
from . import load_database
from . import IprPyDatabase

class BaseEmperorPrepare():
    """
    Base class for the top level Emperor prepare managers.  Subclasses are
    expected to define the machine-specific master_prepare parameters.
    """
    
    def __init__(self,
                 database: Union[str, IprPyDatabase, None] = None):
        """
        Initializes the class
        
        Parameters
        ----------
        database : str, iprPy.database.IprPyDatabase or None, optional
            The database or database name to use.  If None, then it will
            default to the database given by the class' database_name setting.
        """
        self.__prepare_pool = {}
        self.build_prepare_pool()
        self.database = database

    @property
    def prepare_pool(self) -> dict:
        """dict: Links prepare pool methods to pool numbers"""
        return self.__prepare_pool

    @property
    def database(self):
        """iprPy.Database: The database used to prepare the calculations"""
        return self.__database
    
    @database.setter
    def database(self, value: Union[str, IprPyDatabase, None]):
        if value is None:
            self.__database = load_database(self.database_name)
        elif isinstance(value, str):
            self.__database = load_database(value)
        elif isinstance(value, IprPyDatabase):
            self.__database = value
        else:
            raise TypeError('invalid database type: should be None, str, or IprPyDatabase')
        
    
    @property
    def database_name(self) -> str:
        """str: The name of the default database to use"""
        return 'DEFAULT DATABASE NAME'

    @property
    def commands(self) -> dict:
        """
        Defines the LAMMPS and mpi commands to use with the calculations.
        """
        terms = {
            
            ### Required commands ###
            # Primary LAMMPS executable (machine-specific location)
            'lammps_command': 'PATH TO THE PRIMARY LAMMPS EXECUTABLE',

            # MPI command to use with the LAMMPS executable(s)
            # Blank string will always run in serial
            'mpi_command': '',

            
            ### Optional alternate LAMMPS commands ###
            # SNAP version 1 needs LAMMPS between 8 Oct 2014 and 30 May 2017.
            #'lammps_command_snap_1': 'PATH TO THE SNAP V1 LAMMPS EXECUTABLE',

            # SNAP version 2 needs LAMMPS between 3 Dec 2018 and 12 June 2019.
            #'lammps_command_snap_2': 'PATH TO THE SNAP V2 LAMMPS EXECUTABLE',

            # Some older implementations of potentials need LAMMPS before 30 Oct 2019.
            #'lammps_command_old': 'PATH TO THE OLD LAMMPS EXECUTABLE',

            # LAMMPS built with an external module to run aenet potentials
            #'lammps_command_aenet': 'PATH TO THE AENET LAMMPS EXECUTABLE',

            # LAMMPS built with an external module to run pinn potentials
            #'lammps_command_pinn': 'PATH TO THE PINN LAMMPS EXECUTABLE',

        }
        return terms

    def compile_prepare_params(self, pool_params, **kwargs):
        """
        Builds the full set of master_prepare parameters by combining the
        parameters defined for commands, a given pool, and any user-specified
        modifications.

        Parameters
        ----------
        pool_params : dict
            The master_prepare parameters as defined for a prepare pool.
        **kwargs : any
            Any extra/alternate master_prepare parameters to modify the default
            settings.
        """
        
        prepare_params = self.commands
        prepare_params.update(pool_params)
        prepare_params.update(kwargs)

        return prepare_params

    def prepare(self, 
                pool_number, 
                input_script=None, 
                debug=False, 
                **kwargs):
        """
        Prepare calculations for a given pool
        
        Parameters
        ----------
        pool_number : int
            The pool to prepare calculations for.
        input_script : str or file-like object, optional
            A file containing additional prepare term settings to use.
            Examples are potential limiters or replacement run/prepare settings.
        debug : bool
            If set to True, will throw errors associated with failed/invalid
            calculation builds.  Default is False.
        **kwargs : str or list
            Allows for direct specification of any additional prepare term
            settings to use.  These are treated the same as the values in
            input_script (if it was given).
        """
        # Parse input_script and join with kwargs
        if input_script is not None:
            temp = kwargs
            kwargs = parse(input_script)
            kwargs.update(temp)

        self.prepare_pool[pool_number](debug=debug, **kwargs)


    def build_prepare_pool(self):
        """Method to map prepare pool methods to pool numbers"""
        self.prepare_pool[1] = self.prepare_pool_1
        self.prepare_pool[2] = self.prepare_pool_2



    def prepare_pool_1(self, debug: bool = False, **kwargs):
        """
        Prepare pool example #1: A simple call to master_prepare for
        multiple calculations.
        
        Parameters
        ----------
        debug : bool, optional
            If set to True, will throw errors associated with failed/invalid
            calculation builds.  Default is False.
        **kwargs : any
            Any user-specified master_prepare parameter additions or
            modifications.
        """
        raise NotImplementedError('this is only example code')
    
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'isolated_atom diatom_scan E_vs_r_scan:bop E_vs_r_scan',
            'run_directory': 'RUN DIRECTORY NAME',
            'np_per_runner': '1',
            'num_pots': '100',
        }

        # Compile prepare_params 
        prepare_params = self.compile_prepare_params(pool_params, **kwargs)

        # Call master prepare
        self.database.master_prepare(debug=debug, **prepare_params)

    def prepare_pool_2(self, debug: bool = False, **kwargs):
        """
        Prepare pool example #2: Use multiple master_prepare calls to
        prepare one temperature at a time across a range.
        
        Parameters
        ----------
        debug : bool, optional
            If set to True, will throw errors associated with failed/invalid
            calculation builds.  Default is False.
        **kwargs : any
            Any user-specified master_prepare parameter additions or
            modifications.
        """
        raise NotImplementedError('this is only example code')

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_liquid:change_temp',
            'run_directory': 'RUN DIRECTORY NAME',
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

        