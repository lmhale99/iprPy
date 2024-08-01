# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from copy import deepcopy
from typing import Optional, Union

import numpy as np

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .diffusion_liquid import diffusion_liquid
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value

class DiffusionLiquid(Calculation):
    """
    Class for measuring the diffusion coefficient for a liquid using both mean
    squared displacement and velocity autocorrelation methods.
    """

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, Path, IOBase, DM, None]=None,
                 name: Optional[str]=None,
                 database = None,
                 params: Union[str, Path, IOBase, dict] = None,
                 **kwargs: any):
        """
        Initializes a Calculation object for a given style.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Record content in data model format to read in.  Cannot be given
            with params.
        name : str, optional
            The name to use for saving the record.  By default, this should be
            the calculation's key.
        database : yabadaba.Database, optional
            A default Database to associate with the Record, typically the
            Database that the Record was obtained from.  Can allow for Record
            methods to perform Database operations without needing to specify
            which Database to use.
        params : str, file-like object or dict, optional
            Calculation input parameters or input parameter file.  Cannot be
            given with model.
        **kwargs : any
            Any other core Calculation record attributes to set.  Cannot be
            given with model.
        """
        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        self.__system_mods = AtommanSystemManipulate(self)
        subsets = (self.commands, self.potential, self.system,
                   self.system_mods, self.units)

        # Initialize unique calculation attributes
        self.temperature = None
        self.runsteps = 50000
        self.timestep = None
        self.simruns = 10
        self.equilsteps = 0

        self.__measured_temperature = None
        self.__measured_temperature_stderr = None
        self.__diffusion_msd_long = None
        self.__diffusion_msd_long_stderr = None
        self.__diffusion_msd_short = None
        self.__diffusion_msd_short_stderr = None
        self.__diffusion_vacf = None
        self.__diffusion_vacf_stderr = None
        self.__lammps_output = None

        # Define calc shortcut
        self.calc = diffusion_liquid

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'diffusion_vacf.py',
            'in.diffusion_vacf.template'
        ]

############################## Class attributes ################################

    @property
    def commands(self) -> LammpsCommands:
        """LammpsCommands subset"""
        return self.__commands

    @property
    def potential(self) -> LammpsPotential:
        """LammpsPotential subset"""
        return self.__potential

    @property
    def units(self) -> Units:
        """Units subset"""
        return self.__units

    @property
    def system(self) -> AtommanSystemLoad:
        """AtommanSystemLoad subset"""
        return self.__system

    @property
    def system_mods(self) -> AtommanSystemManipulate:
        """AtommanSystemManipulate subset"""
        return self.__system_mods

    @property
    def timestep(self) -> Optional[float]:
        """float: time step for simulation"""
        if self.__timestep is None:
            timestep = am.lammps.style.timestep(self.potential.potential.units)
            lammps_units = am.lammps.style.unit(self.potential.potential.units)
            self.__timestep = uc.set_in_units(timestep, lammps_units['time'])
        
        return self.__timestep
    
    @timestep.setter
    def timestep(self, val: Optional[float]):
        if val is None:
            self.__timestep = None
        else:
            self.__timestep = float(val)
    
    @property
    def temperature(self) -> float:
        """float: Target relaxation temperature"""
        if self.__temperature is None:
            raise ValueError('temperature not set!')
        return self.__temperature

    @temperature.setter
    def temperature(self, val: Optional[float]):
        if val is None:
            self.__temperature = None
        else:
            val = float(val)
            assert val >= 0.0
            self.__temperature = val

    @property
    def runsteps(self) -> int:
        """int: Number of MD steps during the nve analysis stage"""
        return self.__runsteps

    @runsteps.setter
    def runsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__runsteps = val

    @property
    def equilsteps(self) -> int:
        """int: Number of MD steps during the volume equilibration stage"""
        return self.__equilsteps

    @equilsteps.setter
    def equilsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilsteps = val

    @property
    def simruns(self) -> int:
        """How many of the simulations to run for good noise reduction"""
        return self.__simruns 
    
    @simruns.setter
    def simruns(self, val: int):
        val = int(val)
        assert val >= 1
        self.__simruns = val

###################################################################################################################
    ################# Calculated results #########################


    @property
    def lammps_output(self) -> am.lammps.Log:
        """atomman.lammps.Log: The simulation output"""
        if self.__lammps_output is None:
            raise ValueError('No results! Does not get loaded from records!')
        return self.__lammps_output
    
    @property
    def measured_temperature(self) -> float:
        """Measured temperature values throughout simulation"""
        if self.__measured_temperature is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__measured_temperature
    
    @property
    def measured_temperature_stderr(self) -> float:
        """Standard error of temperature over run"""
        if self.__measured_temperature_stderr is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__measured_temperature_stderr

    @property
    def diffusion_msd_long(self) -> float:
        """Calculated diffusion coeffecient averaged over the run 
            starting at the data offset value"""
        if self.__diffusion_msd_long is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__diffusion_msd_long
    
    @property
    def diffusion_msd_long_stderr(self) -> float:
        """Error in the diffusion measurements"""
        if self.__diffusion_msd_long_stderr is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__diffusion_msd_long_stderr
    
    @property
    def diffusion_msd_short(self) -> float:
        """Calculated diffusion coeffecient averaged over the run 
            starting at the data offset value"""
        if self.__diffusion_msd_short is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__diffusion_msd_short
    
    @property
    def diffusion_msd_short_stderr(self) -> float:
        """Error in the diffusion measurements"""
        if self.__diffusion_msd_short_stderr is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__diffusion_msd_short_stderr
    
    @property
    def diffusion_vacf(self) -> float:
        """Calculated diffusion coeffecient averaged over the run 
            starting at the data offset value"""
        if self.__diffusion_vacf is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__diffusion_vacf
    
    @property
    def diffusion_vacf_stderr(self) -> float:
        """Error in the diffusion measurements"""
        if self.__diffusion_vacf_stderr is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__diffusion_vacf_stderr
  
    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs: any):
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameters
        ----------
        name : str, optional
            The name to assign to the calculation.  By default, this is set as
            the calculation's key.
        temperature : float
            The target temperature to perform calculation on
        runsteps : int or None, optional
            The number of nve integration steps to perform on the system to
            obtain measurements of diffusion
        timestep: float or None
            the difference in time between each step of the calculation
        simruns: int or None
            The number of simulations to run - more simulations equates to
            less noise. Default value of 5
        equilsteps: int or None
            If doing an equilibrium run this is the number of simulation
            timesteps 
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
        if 'timestep' in kwargs:
            self.timestep = kwargs['timestep']
        if 'simruns' in kwargs:
            self.simruns = kwargs['simruns']
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'equilsteps' in kwargs:
            self.equilsteps = kwargs['equilsteps']

####################### Parameter file interactions ###########################

    def load_parameters(self,
                        params: Union[dict, str, IOBase],
                        key: Optional[str] = None):
        """
        Reads in and sets calculation parameters.

        Parameters
        ----------
        params : dict, str or file-like object
            The parameters or parameter file to read in.
        key : str, optional
            A new key value to assign to the object.  If not given, will use
            calc_key field in params if it exists, or leave the key value
            unchanged.
        """
        # Load universal content
        input_dict = super().load_parameters(params, key=key)

        # Load input/output units
        self.units.load_parameters(input_dict)

        # Change default values for subset terms
        input_dict['sizemults'] = input_dict.get('sizemults', '1 1 1')

        # Load calculation-specific strings

        # Load calculation-specific booleans

        # Load calculation-specific its
        self.runsteps = int(input_dict.get('runsteps', 50000))
        self.simruns = int(input_dict.get('simruns', 10))
        self.equilsteps = int(input_dict.get('equilsteps', 0))

        # Load calculation-specific unitless floats
        self.temperature = float(input_dict['temperature'])

        # Load calculation-specific floats with units
        if 'timestep' in input_dict:
            self.timestep = value(input_dict, 'timestep',
                                  default_unit='ps')
        else:
            self.timestep = None

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Manipulate system
        self.system_mods.load_parameters(input_dict)

    def master_prepare_inputs(self,
                              branch: str = 'main',
                              **kwargs: any) -> dict:
        """
        Utility method that build input parameters for prepare according to the
        workflows used by the NIST Interatomic Potentials Repository.  In other
        words, transforms inputs from master_prepare into inputs for prepare.

        Parameters
        ----------
        branch : str, optional
            Indicates the workflow branch to prepare calculations for.  Default
            value is 'main'.
        **kwargs : any
            Any parameter modifications to make to the standard workflow
            prepare scripts.

        Returns
        -------
        params : dict
            The full set of prepare parameters based on the workflow branch
        """
        
        # Initialize params and copy over branch
        params = {}
        params['branch'] = branch

        # main branch
        if branch == 'main':

            # Check for required kwargs
            assert 'lammps_command' in kwargs
            assert 'temperature' in kwargs, 'temperature must be specified for this branch'

            # Set default workflow settings
            params['buildcombos'] =  'atomicarchive load_file archive'

            params['archive_record'] = 'calculation_relax_liquid_redo'
            params['archive_load_key'] = 'final-system'
            params['archive_status'] = 'finished'
            params['archive_temperature'] = kwargs['temperature']
            params['temperature'] = kwargs['temperature']
            params['runsteps'] = '2000'
            params['simruns'] = '100'
            params['sizemults'] = '1 1 1'

            # Copy kwargs to params
            for key in kwargs:

                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'archive_{key}'] = kwargs[key]

                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        else:
            raise ValueError(f'Unknown branch {branch}')

        return params

    @property
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'temperature': ' '.join([
                "Target temperature for the simulation. Required."]),
            'timestep': ' '.join([
                "How much to increase the time at each step.  If not given, will",
                "use the default LAMMPS timestep value associated with the",
                "potential's unit style."]),
            'runsteps':' '.join([
                "How many time steps to run during each simulation.  The total steps",
                 "will be runsteps * simruns"]),
            'simruns':' '.join([
                "The number of separate VACF simulations to run.  A higher number",
                 "helps damp out the simulation noise.  Default value is 10."]),
            'equilsteps':' '.join([
                "The number of equilibrium timesteps to run prior to evaluating the",
                "diffusion.  Useful if your initial configuration and velocities are",
                "not already in an equilibrium state.  Default value is 0."]),
        }

    @property
    def singularkeys(self) -> list:
        """list: Calculation keys that can have single values during prepare."""

        keys = (
            # Universal keys
            super().singularkeys

            # Subset keys
            + self.commands.keyset
            + self.units.keyset

            # Calculation-specific keys
        )
        return keys

    @property
    def multikeys(self) -> list:
        """list: Calculation key sets that can have multiple values during prepare."""

        keys = (
            # Universal multikeys
            super().multikeys +

            # Combination of potential and system keys
            [
                self.potential.keyset +
                self.system.keyset
            ] +

            # System mods keys
            [
                self.system_mods.keyset
            ] +

            # Run parameters
            [
                [
                    'temperature',
                    'timestep',
                    'runsteps',
                    'simruns',
                    'equilsteps',
                ]
            ]
        )
        return keys


########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation_diffusion_liquid'

    def build_model(self) -> DM:
        """
        Generates and returns model content based on the values set to object.
        """
        # Build universal content
        model = super().build_model()
        calc = model[self.modelroot]

        # Build subset content
        self.commands.build_model(calc, after='atomman-version')
        self.potential.build_model(calc, after='calculation')
        self.system.build_model(calc, after='potential-LAMMPS')
        self.system_mods.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']

        run_params['temperature'] = uc.model(self.temperature, 'K')
        run_params['timestep'] = uc.model(self.timestep, 'ps')
        run_params['runsteps'] = self.runsteps
        run_params['simruns'] = self.simruns
        run_params['equilsteps'] = self.equilsteps
        
        # Build results
        if self.status == 'finished':
            calc['measured_temperature'] = uc.model(self.measured_temperature, 'K',
                                                    self.measured_temperature_stderr)
            calc['diffusion_msd_short'] = uc.model(self.diffusion_msd_short, 'm^2/s',
                                                   self.diffusion_msd_short_stderr)
            calc['diffusion_msd_long'] = uc.model(self.diffusion_msd_long, 'm^2/s',
                                                  self.diffusion_msd_long_stderr)
            calc['diffusion_vacf'] = uc.model(self.diffusion_vacf, 'm^2/s',
                                              self.diffusion_vacf_stderr)

        self._set_model(model)
        return model

    def load_model(self,
                   model: Union[str, DM],
                   name: Optional[str] = None):
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
        # Load universal and subset content
        super().load_model(model, name=name)
        calc = self.model[self.modelroot]

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.runsteps = run_params['runsteps']
        self.timestep = uc.value_unit(run_params['timestep'])
        self.temperature = uc.value_unit(run_params['temperature'])
        self.simruns = run_params['simruns']
        self.equilsteps = run_params['equilsteps']

        # Load results
        if self.status == 'finished':

            self.__diffusion_msd_short = uc.value_unit(calc['diffusion_msd_short'])
            self.__diffusion_msd_short_stderr = uc.error_unit(calc['diffusion_msd_short'])

            self.__diffusion_msd_long = uc.value_unit(calc['diffusion_msd_long'])
            self.__diffusion_msd_long_stderr = uc.error_unit(calc['diffusion_msd_long'])

            self.__diffusion_vacf = uc.value_unit(calc['diffusion_vacf'])
            self.__diffusion_vacf_stderr = uc.error_unit(calc['diffusion_vacf'])

            self.__measured_temperature = uc.value_unit(calc['measured_temperature'])
            self.__measured_temperature_stderr = uc.error_unit(calc['measured_temperature'])

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'temperature': load_query(
                style='float_match',
                name='temperature',
                path=f'{self.modelroot}.temperature.value',
                description='search by temperature in Kelvin'),
        })
        return queries

########################## Metadata interactions ##############################

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        # Call super to extract universal and subset content
        meta = super().metadata()

        # Extract calculation-specific content
        meta['temperature'] = self.temperature

        # Extract results
        if self.status == 'finished':

            meta['measured_temperature'] = self.measured_temperature
            meta['measured_temperature_stderr'] = self.measured_temperature_stderr

            meta['diffusion_msd_short'] = self.diffusion_msd_short
            meta['diffusion_msd_short_stderr'] = self.diffusion_msd_short_stderr

            meta['diffusion_msd_long'] = self.diffusion_msd_long
            meta['diffusion_msd_long_stderr'] = self.diffusion_msd_long_stderr

            meta['diffusion_vacf'] = self.diffusion_vacf
            meta['diffusion_vacf_stderr'] = self.diffusion_vacf_stderr


        return meta

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',

            'parent_key',
            'load_options',
            'symbols',

            'potential_LAMMPS_key',
            'potential_key',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'temperature':1e-2,
        }

########################### Calculation interactions ##########################

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""

        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Remove unused subset inputs
        del input_dict['transform']
        del input_dict['ucell']

        # Add calculation-specific inputs
        input_dict['runsteps'] = self.runsteps
        input_dict['temperature'] = self.temperature
        input_dict['timestep'] = self.timestep
        input_dict['simruns'] = self.simruns
        input_dict['equilsteps'] = self.equilsteps

        # Return input_dict
        return input_dict

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'init.dat',
            'log.lammps',
            'diffusion_liquid.in'
        ]

    def process_results(self, results_dict: dict):
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
        self.__measured_temperature = results_dict['measured_temperature']
        self.__measured_temperature_stderr = results_dict['measured_temperature_stderr']

        self.__diffusion_msd_short = results_dict["diffusion_msd_short"]
        self.__diffusion_msd_short_stderr = results_dict["diffusion_msd_short_stderr"]

        self.__diffusion_msd_long = results_dict["diffusion_msd_long"]
        self.__diffusion_msd_long_stderr = results_dict["diffusion_msd_long_stderr"]

        self.__diffusion_vacf = results_dict["diffusion_vacf"]
        self.__diffusion_vacf_stderr = results_dict["diffusion_vacf_stderr"]

        self.__lammps_output = results_dict['lammps_output']
