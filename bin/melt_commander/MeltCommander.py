from typing import Union, Optional
import argparse

import numpy as np

import iprPy
from iprPy.input import parse


class MeltCommander():
    """
    Class for managing melting temperature search workflows.
    """
    def __init__(self,
                 database: Union[str, iprPy.database.IprPyDatabase],
                 lammps_command: str,
                 potential_LAMMPS_id: str,
                 composition: str,
                 family: str,
                 mpi_command: str = '',
                 min_temperature: float = 50,
                 max_temperature: float = 3000,
                 calc_style: str = 'melting_temperature'):
        """
        Initializes a MeltCommander object, which is designed to iteratively
        run the iprPy melting_temperature calculation at different guess
        temperatures.

        Parameters
        ----------
        database : iprPy.database.IprPyDatabase
            The database to save results into and to check for existing
            results.
        lammps_command : str
            The LAMMPS executable to use with the simulation.
        potential_LAMMPS_id : str
            The id for the LAMMPS potential to use.
        composition : str
            The composition of the system to use.
        family : str
            The crystal prototype to use for the solid phase.  Note that the
            size of the system that will be used is currently hard-coded to
            the prototype.
        mpi_commmand : str, optional
            The MPI executable and options to use if running LAMMPS in
            parallel.
        min_temperature : float, optional
            The lower bound to use for the guess temperature when iterating.
            Default value is 50.
        max_temperature : float, optional
            The upper bound to use for the guess temperature when iterating.
            Default value is 3000.
        calc_style : str, optional
            The iprPy calculation style to use.  Default value is
            'melting_temperature'.
        """
        self.database = database
        self.lammps_command = lammps_command
        self.mpi_command = mpi_command
        self.potential_LAMMPS_id = potential_LAMMPS_id
        self.composition = composition
        self.family = family
        self.min_temperature = min_temperature
        self.max_temperature = max_temperature
        self.calc_style = calc_style

        self.load_existing_records()
        print(len(self.temperature_melts), 'existing records')

    @property
    def database(self) -> iprPy.database.IprPyDatabase:
        """iprPy.Database: The database used to prepare the calculations"""
        return self.__database
    
    @database.setter
    def database(self, value: Union[str, iprPy.database.IprPyDatabase]):
        if isinstance(value, str):
            self.__database = iprPy.load_database(value)
        elif isinstance(value, iprPy.database.IprPyDatabase):
            self.__database = value
        else:
            raise TypeError('invalid database type: should be str or IprPyDatabase')

    @property
    def lammps_command(self) -> str:
        """str: The path to the LAMMPS executable to use"""
        return self.__lammps_command
    
    @lammps_command.setter
    def lammps_command(self, val: str):
        self.__lammps_command =  str(val)

    @property
    def mpi_command(self) -> str:
        """str: The mpi command to use with LAMMPS"""
        return self.__mpi_command
    
    @mpi_command.setter
    def mpi_command(self, val: str):
        self.__mpi_command =  str(val)
    
    @property
    def potential_LAMMPS_id(self) -> str:
        """str: The path to the LAMMPS executable to use"""
        return self.__potential_LAMMPS_id
    
    @potential_LAMMPS_id.setter
    def potential_LAMMPS_id(self, val: str):
        self.__potential_LAMMPS_id =  str(val)

    @property
    def composition(self) -> str:
        """str: The element model symbol to use"""
        return self.__composition
    
    @composition.setter
    def composition(self, val: str):
        self.__composition =  str(val)
    
    @property
    def family(self) -> str:
        """str: The crystal structure family to use for the solid and solid identification"""
        return self.__family
        
    @family.setter
    def family(self, val: str):
        val = str(val)

        if val not in ['A1--Cu--fcc', 'A2--W--bcc', 'A3--Mg--hcp']:
            raise ValueError('Unsupported family type')
        
        self.__family =  val

    @property
    def min_temperature(self) -> float:
        """float: The minimum search temperature to use"""
        return self.__min_temperature
    
    @min_temperature.setter
    def min_temperature(self, val: float):
        self.__min_temperature =  float(val)

    @property
    def max_temperature(self) -> float:
        """float: The maximum search temperature to use"""
        return self.__max_temperature
    
    @max_temperature.setter
    def max_temperature(self, val: float):
        self.__max_temperature =  float(val)


    @property
    def calc_style(self) -> str:
        """str: The iprPy calculation style to use"""
        return self.__calc_style
    
    @calc_style.setter
    def calc_style(self, val: str):
        self.__calc_style=  str(val)

    @property
    def temperature_melts(self) -> list:
        """list: The computed melt temperatures for systems that had both phases"""
        return self.__temperature_melts


    @classmethod
    def from_input(cls, input_script):
        """
        Initializes a new MeltCommander object from a text input file.
        Recognizes input keywords that correspond to the parameters
        of the class' __init__ function.
        """

        kwargs = parse(input_script)

        database = kwargs.pop('database')
        lammps_command = kwargs.pop('lammps_command')
        composition = kwargs.pop('composition')
        family = kwargs.pop('family')
        mpi_command = kwargs.pop('mpi_command', '')
        min_temperature = float(kwargs.pop('min_temperature'))
        max_temperature = float(kwargs.pop('max_temperature'))
        calc_style = kwargs.pop('calc_style', 'melting_temperature')

        if 'potential_id' in kwargs:
            assert 'potential_LAMMPS_id' not in kwargs
            potential_LAMMPS_id = kwargs.pop('potential_id')
        else:
            potential_LAMMPS_id = kwargs.pop('potential_LAMMPS_id')

        obj = cls(database, lammps_command, potential_LAMMPS_id, composition, family,
                  mpi_command = mpi_command,
                  min_temperature = min_temperature,
                  max_temperature = max_temperature,
                  calc_style = calc_style)
        
        return obj, kwargs

    def load_existing_records(self):
        """
        Loads all corresponding records currently in the database and updates
        input/output values accordingly
        """
        # Initialize/reset temperature_melts results list
        self.__temperature_melts = []

        # Fetch any currently existing records
        self.records_df = self.database.get_records_df(f'calculation_{self.calc_style}',
                                                       potential_LAMMPS_id = self.potential_LAMMPS_id,
                                                       composition = self.composition,
                                                       family = self.family)
        for index in self.records_df.index:
            record = self.records_df.loc[index]
            
            # Extract melt and guess temperatures, and the fraction solid
            fraction_solid = np.mean(record.fraction_solids)
            temperature_melt = record.melting_temperature
            temperature_guess = record.temperature_guess

            # Update min_temperature and max_temperature as needed
            if fraction_solid > 0.75:
                if temperature_guess > self.min_temperature:
                    self.min_temperature = temperature_guess
            elif fraction_solid < 0.25:
                if temperature_guess < self.max_temperature:
                    self.max_temperature = temperature_guess
            
            # Add good results to the temperature_melts list
            else:
                self.temperature_melts.append(temperature_melt)


    def prepare_kwargs(self,
                       alat: float,
                       t_guess: float,
                       **kwargs):
        """
        Generates the input script terms for preparing a new melting
        temperature calculation run.  NOTE: lots of terms and settings are
        currently hard-coded within this function!
        """
        prepare_kwargs = {
            'lammps_command':                  self.lammps_command,

            'potential_file':                  f'{self.potential_LAMMPS_id}.json',
            'potential_content':               f'record {self.potential_LAMMPS_id}',
            'potential_dir':                   self.potential_LAMMPS_id,
            'potential_dir_content':           f'tar {self.potential_LAMMPS_id}',
            
            # Initial System Configuration
            'symbols':                         self.composition,
            
            # Run Parameters
            'temperature_guess':               f'{t_guess}',
            
            'meltsteps':                       '10000',
            'scalesteps':                      '10000',
            'runsteps':                        '200000',
            'dumpsteps':                       '10000',
            'randomseed':                      f'{len(self.temperature_melts) + 1}',
        }

        if self.mpi_command is not None:
            prepare_kwargs['mpi_command'] = self.mpi_command

        if self.family == 'A1--Cu--fcc':
            prepare_kwargs.update(self.default_fcc_prepare_kwargs(alat))
        elif self.family == 'A2--W--bcc':
            prepare_kwargs.update(self.default_bcc_prepare_kwargs(alat))
        elif self.family == 'A3--Mg--hcp':
            prepare_kwargs.update(self.default_hcp_prepare_kwargs(alat))

        # Overwrite with input kwargs
        prepare_kwargs.update(kwargs)

        return prepare_kwargs
    
    def default_fcc_prepare_kwargs(self,
                                   alat: float):
        """The default prepare input kwargs to use for fcc crystals"""
        return {
            'load_file':                       'A1--Cu--fcc.json',
            'load_content':                    'record A1--Cu--fcc',
            'load_style':                      'system_model',
            'box_parameters':                  f'{alat:.3} {alat:.3} {alat:.3}',
            'sizemults':                       '10 10 20',
            'ptm_structures':                  'fcc',
        }
    
    def default_bcc_prepare_kwargs(self,
                                   alat: float):
        """The default prepare input kwargs to use for bcc crystals"""
        return {
            'load_file':                       'A2--W--bcc.json',
            'load_content':                    'record A2--W--bcc',
            'load_style':                      'system_model',
            'box_parameters':                  f'{alat:.3} {alat:.3} {alat:.3}',
            'sizemults':                       '13 13 26',
            'ptm_structures':                  'bcc',
        }
    
    def default_hcp_prepare_kwargs(self,
                                   alat: float):
        """The default prepare input kwargs to use for hcp crystals"""
        return {
            'load_file':                       'A3--Mg--hcp.json',
            'load_content':                    'record A3--Mg--hcp',
            'load_style':                      'system_model',
            'box_parameters':                  f'{alat:.3} {alat:.3} {1.633*alat:.3} 90 90 120',
            'sizemults':                       '13 13 26',
            'ptm_structures':                  'hcp',
        }



    def run(self, 
            run_directory,
            alat: float,
            max_melts: int = 10,
            temperature_guess: Optional[float] = None,
            **kwargs):
        """
        Prepares and runs multiple melting temperature calculations, iterating
        the guess temperature until max_melts runs have finished with the
        target solid fraction.

        Parameters
        ----------
        run_directory : str
            The iprPy run_directory to use for preparing and running the
            calculations.
        alat : float
            The guess lattice constant to use for the solid phase.  Only
            needs to be a rough approximate value due to the barostat
            relaxation.
        max_melts : int, optional
            The target number of melt simulations to obtain that are within
            the target solid fraction range.  When this is achieved, the
            calculations will stop.  Default value is 10.
        temperature_guess : float, optional
            The initial guess temperature to start with.  If not given, will
            select the temperature halfway between the min_temperature and
            max_temperature values previously set.
        """
        
        # Set default initial temperature guess
        if temperature_guess is None:
            temperature_guess = (self.min_temperature + self.max_temperature) / 2

        # Init run manager and tar_dict for preparing and running
        runner = iprPy.database.RunManager(self.database, run_directory)
        tar = self.database.get_tar(style='potential_LAMMPS', name=self.potential_LAMMPS_id)
        tar_dict = {self.potential_LAMMPS_id: tar}

        # Loop until max_melts performed
        while len(self.temperature_melts) < max_melts:

            # Build prepare keys and prepare the calculation
            prepare_kwargs = self.prepare_kwargs(alat, temperature_guess, **kwargs)
            keys = self.database.prepare(run_directory, self.calc_style, tar_dict=tar_dict,
                                         calc_df=self.records_df, **prepare_kwargs)
            assert len(keys) == 1
            key = keys[0]
            
            # Run prepared calculation and fetch record
            runner.run(key)
            record = self.database.get_record(f'calculation_{self.calc_style}', key=key)
            fraction_solid = np.mean(record.fraction_solids)
            temperature_melt = record.melting_temperature

            print(f'{temperature_guess:.3f} {fraction_solid:.4} {temperature_melt:.3f}')

            if fraction_solid > 0.75:
                # Increase T and adjust min boundary if too much solid
                self.min_temperature = temperature_guess
                temperature_guess = (temperature_guess + self.max_temperature) / 2

            elif fraction_solid < 0.25:
                # Decrease T and adjust max boundary if too much liquid
                self.max_temperature = temperature_guess
                temperature_guess = (temperature_guess + self.min_temperature) / 2
            
            else:
                self.temperature_melts.append(temperature_melt)
                if fraction_solid > 0.6:
                    temperature_guess = (temperature_guess + self.max_temperature) / 2
                elif fraction_solid < 0.4:
                    temperature_guess = (temperature_guess + self.min_temperature) / 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command line options for running a melt commander')
    parser.add_argument('input_script', 
                        help='The input script specifying run parameters')
    args = parser.parse_args()

    # Parse input script and init a MeltCommander
    commander, kwargs = MeltCommander.from_input(args.input_script)

    # Pop required run parameters
    run_directory = kwargs.pop('run_directory')
    alat = float(kwargs.pop('alat'))
    max_melts = int(kwargs.pop('max_melts', 10))

    commander.run(run_directory, alat, max_melts, **kwargs)