# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from copy import deepcopy
from typing import Optional, Union
import random

import numpy as np

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .diffusion_vacf import diffusion_vacf
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value

class DiffusionVACF(Calculation):
    """Class for managing dynamic relaxations"""

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
        subsets = (self.commands, self.potential, self.system, self.units)

        # Initialize unique calculation attributes

        self.temperature = 300
        self.randomseed = None

        self.runsteps = 50000
        self.timestep = .001 


        self.simruns = 5
        self.eq_thermosteps = 0
        self.eq_runsteps = 0
        self.eq_equilibrium = False

        self.__measured_temperature = None
        self.__measured_temperature_stderr = None
        self.__diffusion_value = None
        self.__diffusion_value_stderr = None
        self.__vacf_x_values = None
        self.__vacf_y_values = None
        self.__vacf_z_values = None
        self.__vacf_values = None
        self.__lammps_output = None

        # Define calc shortcut
        self.calc = diffusion_vacf

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

    ########################## Input Paramteres #################################

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
    def timestep(self) -> Optional[float]:
        """float: time step for simulation"""
        if self.__timestep is None:
            return am.lammps.style.timestep(self.potential.potential.units)
        else:
            return self.__timestep
    
    @timestep.setter
    def timestep(self, val: Optional[float]):
        if val is None:
            self.__timestep = None
        else:
            self.__timestep = val
    
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
    def randomseed(self) -> int:
        """int: Random number seed."""
        return self.__randomseed

    @randomseed.setter
    def randomseed(self, val: int):
        if val is None:
            val = random.randint(1, 900000000)
        else:
            val = int(val)
            assert val > 0 and val <= 900000000
        self.__randomseed = val


    @property
    def eq_thermosteps(self) -> int:
        """int: Number of MD steps during the energy equilibration stage"""
        if self.__eq_thermosteps is None:
            return 0
        else:
            return self.__eq_thermosteps
    
    @eq_thermosteps.setter
    def eq_thermosteps(self, val: int):
        if val is None:
            self.__eq_thermosteps = 0
        else:
            assert val >= 0
            self.__eq_thermosteps = val

    @property
    def eq_runsteps(self) -> int:
        """int: Number of MD steps during the volume equilibration stage"""
        if self.__eq_runsteps is None:
            return 0 
        else:
            return self.__eq_runsteps

    @eq_runsteps.setter
    def eq_runsteps(self, val: int):
        if val is None:
            self.__eq_runsteps = 0
        else:
            assert val >= 0
            self.__eq_runsteps = val

    @property 
    def eq_equilibrium(self) -> bool:
        """bool: Does the system need equilibration"""
        if self.__eq_equilibrium is None:
            return False
        else:
            return self.__eq_equilibrium
    
    @eq_equilibrium.setter
    def eq_equilibrium(self, val:bool):
        if val is None:
            self.__eq_equilibrium = False 
        else: 
            self.__eq_equilibrium = val

    @property
    def simruns(self) -> int:
        """How many of the simulations to run for good noise reduction"""
        return self.__simruns 
    
    @simruns.setter
    def simruns(self, val: int):
        if val is None:
            self.__simruns = 5
        else:
            self.__simruns = int(val)

###################################################################################################################
    ################# Calculated results #########################


    @property
    def vacf_x_values(self) -> np.ndarray:
        """numpy.array: Mean squared displacements along the x direction"""
        if self.__vacf_x_values is None:
            raise ValueError('No results yet!')
        return self.__vacf_x_values

    @property
    def vacf_y_values(self) -> np.ndarray:
        """numpy.array: Mean squared displacements along the y direction"""
        if self.__vacf_y_values is None:
            raise ValueError('No results yet!')
        return self.__vacf_y_values

    @property
    def vacf_z_values(self) -> np.ndarray:
        """numpy.array: Mean squared displacements along the z direction"""
        if self.__vacf_z_values is None:
            raise ValueError('No results yet!')
        return self.__vacf_z_values

    @property
    def vacf_values(self) -> np.ndarray:
        """numpy.array: Total mean squared displacements"""
        if self.__vacf_values is None:
            raise ValueError('No results yet!')
        return self.__vacf_values

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
    def diffusion_value(self) -> float:
        """Calculated diffusion coeffecient averaged over the run 
            starting at the data offset value"""
        if self.__diffusion_value is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__diffusion_value
    
    @property
    def diffusion_value_stderror(self) -> float:
        """Error in the diffusion measurements"""
        if self.__diffusion_value_stderr is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__diffusion_value_stderr
    
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
        eq_thermosteps: int or None
            If doing an equilibrium run this is the number of steps inbetween
            the thermo calculations
        eq_runsteps: int or None
            If doing an equilibrium run this is the number of simulation
            timesteps 
        eq_equilibrium: bool or None
            Set to true if you need to relax the system first. False if the 
            system is already relaxed. 
        randomseed : int or None, optional
            Random number seed used by LAMMPS in creating velocities and with
            the Langevin thermostat.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)
        if 'randomseed' in kwargs:
            self.randomseed = kwargs['randomseed']
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
        if 'timestep' in kwargs:
            self.timestep = kwargs['timestep']
        if 'simruns' in kwargs:
            self.simruns = kwargs['simruns']
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'eq_thermosteps' in kwargs:
            self.eq_thermosteps = kwargs['eq_thermosteps']
        if 'eq_runsteps' in kwargs:
            self.eq_runsteps = kwargs['eq_runsteps']
        if 'eq_equilbirium' in kwargs:
            self.eq_equilibrium = kwargs['eq_equilibrium']

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


        # Load calculation-specific strings

        # Load calculation-specific booleans
        self.eq_equilibrium = bool(input_dict.get('eq_equilibrium',False))

        # Load calculation-specific its
        self.runsteps = int(input_dict.get('runsteps', 50000))
        self.randomseed = input_dict.get('randomseed', None)
        self.simruns = int(input_dict.get('simruns',5))
        self.eq_thermosteps = int(input_dict.get('eq_termosteps',0))
        self.eq_runsteps = int(input_dict.get('eq_runsteps',0))

        # Load calculation-specific unitless floats

        # Load calculation-specific floats with units
        self.timestep = value(input_dict,'timestep',
                              default_unit='ps',
                              default_term='0.001 ps')
        self.temperature = value(input_dict,'temperature',
                                 default_unit='K',
                                 default_term='300 K')

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Manipulate system


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

            params['archive_record'] = 'calculation_diffusion_vacf'
            params['archive_load_key'] = 'final-system'
            params['archive_status'] = 'finished'
            params['archive_temperature'] = kwargs['temperature']
            params['temperature'] = kwargs['temperature']

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
            'temperature': ' '.join(["Target temperature for the simulation - Default value of 300 K"]),
            'timestep': ' '.join(["How much to increase the time at each step - Default value of None will use the LAMMPS default"]),
            'runsteps':' '.join(["How many time steps to run simulation - Default value is 100000"]),
            'simruns':' '.join(["The number of simulations to run - a higher number helps damp out simulation noise"]),
            'eq_thermosteps':' '.join(["How often to write calculated value to log file/ouput for",
                                         "equilibriation run- Default value is 1000"]),
            'eq_runsteps':' '.join(["How many time steps to run simulation for equilibration",
                                     "run - Default value is 0"]),
            'eq_equilibrium':' '.join(["Specifies whether or not to do an equilibration default is false",
                                       "Set to yet if the input is not a relaxed liquid already"]),
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
            # [
            #     self.system_mods.keyset
            # ] +

            # Run parameters
            [
                [
                    'temperature',
                    'timestep',
                    'runsteps',
                    'simruns',
                    'eq_thermosteps',
                    'eq_runsteps',
                    'eq_equilibrium',
                    'randomseed',
                ]
            ]
        )
        return keys


########################### Data model interactions ###########################

#Don't know what to do with the data model interactions 
#This stuff makes the json file
    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation_diffusion_vacf'

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
        # self.system_mods.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']

        run_params['temperature'] = uc.model(self.temperature,'K')
        run_params['timestep'] = uc.model(self.timestep,'ps')
        run_params['runsteps'] = self.runsteps
        run_params['simruns'] = self.simruns
        run_params['randomseed'] = self.randomseed
        run_params['eq_thermosteps'] = self.eq_thermosteps
        run_params['eq_runsteps'] = self.eq_runsteps
        run_params['eq_equilibrium'] = self.eq_equilibrium
        # Build results
        if self.status == 'finished':

            calc['vacf_x'] = uc.model(self.vacf_x_values.tolist(),f'({self.units.length_unit}/ps)^2')
            calc['vacf_y'] = uc.model(self.vacf_y_values.tolist(),f'({self.units.length_unit}/ps)^2')
            calc['vacf_z'] = uc.model(self.vacf_z_values.tolist(),f'({self.units.length_unit}/ps)^2')
            calc['vacf'] = uc.model(self.vacf_values.tolist(),f'({self.units.length_unit}/ps)^2')
            calc['measured_temperature'] = uc.model(self.measured_temperature,'K')
            calc['measured_temperature_stderr'] = uc.model(self.measured_temperature_stderr,'K')
            calc['diffusion'] = uc.model(self.diffusion_value,f'({self.units.length_unit}/ps)^2*ps')
            calc['diffusion_stderr'] = uc.model(self.diffusion_value_stderror,
                                                f'({self.units.length_unit}/ps)^2*ps')

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
        self.randomseed = run_params['randomseed']
        self.temperature = uc.value_unit(run_params['temperature'])
        self.simruns = run_params['simruns']
        self.eq_thermosteps = run_params['eq_thermosteps']
        self.eq_runsteps = run_params['eq_runsteps']
        self.eq_equilibrium = run_params['eq_equilibrium']

        # Load results
        if self.status == 'finished':

            self.__vacf_x_values = uc.value_unit(calc['vacf_x'])
            self.__vacf_y_values = uc.value_unit(calc['vacf_y'])
            self.__vacf_z_values = uc.value_unit(calc['vacf_z'])
            self.__vacf_values = uc.value_unit(calc['vacf'] )
            self.__diffusion_value = uc.value_unit(calc['diffusion'])
            self.__diffusion_value_stderr = uc.value_unit(calc['diffusion_stderr'])
            self.__measured_temperature = uc.value_unit(calc['measured_temperature'])
            self.__measured_temperature_stderr = uc.value_unit(calc['measured_temperature_stderr'])

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'temperature': load_query(
                style='float_match',
                name='temperature',
                path=f'{self.modelroot}.temperature.value',
                description='search by temperature in Kelvin'),
            'diffusion': load_query(
                style='float_match',
                name='diffusion',
                path=f'{self.modelroot}.diffusion.value',
                description='search by diffusion in Pressure time potential units')
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
            meta['measured_diffusion'] = self.diffusion_value
            meta['measured_diffusion_stderr'] = self.diffusion_value_stderror

            meta['vacf_x_values'] = self.vacf_x_values
            meta['vacf_y_values'] = self.vacf_y_values
            meta['vacf_z_values'] = self.vacf_z_values
            meta['vacf_values'] = self.vacf_values

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
        # del input_dict['transform']
        input_dict['system'] = input_dict.pop('ucell')

        # Add calculation-specific inputs
        input_dict['runsteps'] = self.runsteps
        input_dict['randomseed'] = self.randomseed
        input_dict['temperature'] = self.temperature
        input_dict['timestep'] = self.timestep
        input_dict['simruns'] = self.simruns
        input_dict['eq_thermosteps'] = self.eq_thermosteps
        input_dict['eq_runsteps'] = self.eq_runsteps
        input_dict['eq_equilibrium'] = self.eq_equilibrium
        # Return input_dict
        return input_dict

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
        self.__diffusion_value = results_dict["diffusion"]
        self.__diffusion_value_stderr = results_dict["diffusion_stderr"]

        self.__vacf_x_values = results_dict['vacf_x_values']
        self.__vacf_y_values = results_dict['vacf_y_values']
        self.__vacf_z_values = results_dict['vacf_z_values']
        self.__vacf_values = results_dict['vacf_values']
        self.__lammps_output = results_dict['lammps_output']
