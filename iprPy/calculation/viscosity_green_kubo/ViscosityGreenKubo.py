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
from .viscosity_green_kubo import viscosity_green_kubo
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value

class ViscosityGreenKubo(Calculation):
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
        self.__system_mods = AtommanSystemManipulate(self)
        subsets = (self.commands, self.potential, self.system, self.system_mods, self.units)

        # Initialize unique calculation attributes
        self.temperature = None
        self.timestep = None
        self.runsteps = 1000000
        self.outputsteps = 2000
        self.sampleinterval = 5
        self.correlationlength = 200
        self.dragcoeff = 0.2
        self.equilsteps = 0

########################################################

        self.__pxy_values = None
        self.__pxz_values = None
        self.__pyz_values = None

        self.__vx_value = None
        self.__vy_value = None
        self.__vz_value = None

        self.__measured_temperature = None
        self.__measured_temperature_stderr = None
        self.__viscosity = None
        self.__viscosity_stderr = None
        self.__lammps_output = None

        # Define calc shortcut
        self.calc = viscosity_green_kubo

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'viscosity_green_kubo.py',
            'in.viscosity_green_kubo.template'
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
    def outputsteps(self) -> int:
        """Frequency of the thermo outputs"""
        return self.__outputsteps
    
    @outputsteps.setter
    def outputsteps(self, val: Optional[int]):
        val = int(val)
        assert val >= 0
        self.__outputsteps = val

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
    def correlationlength(self) -> int:
        """the SMALL number of steps to average over for one 'point' """
        return self.__correlationlength
    
    @correlationlength.setter
    def correlationlength(self, val: int):
        val = int(val)
        assert val >= 0
        self.__correlationlength = val 
    
    @property 
    def sampleinterval(self) -> int:
        return self.__sampleinterval 
    
    @sampleinterval.setter
    def sampleinterval(self, val: int):
        val = int(val)
        assert val >= 0
        self.__sampleinterval = val
    
    @property
    def dragcoeff(self) -> float:
        return self.__dragcoeff
    
    @dragcoeff.setter
    def dragcoeff(self, val: float):
        self.__dragcoeff = float(val)

###################################################################################################################
    ################# Calculated results #########################

    @property
    def pxy_values(self) -> np.ndarray:
        """xy component of pressure tensor"""
        if self.__pxy_values is None:
            raise ValueError('No results! Does not get loaded from records!')
        return self.__pxy_values

    @property
    def pxz_values(self) -> np.ndarray:
        """xz component of pressure tensor"""
        if self.__pxz_values is None:
            raise ValueError('No results! Does not get loaded from records!')
        return self.__pxz_values

    @property
    def pyz_values(self) -> np.ndarray:
        """yz component of pressure tensor"""
        if self.__pyz_values is None:
            raise ValueError('No results! Does not get loaded from records!')
        return self.__pyz_values
    
    @property
    def vx_value(self) -> float:
        """x component of viscosity"""
        if self.__vx_value is None:
            raise ValueError('No results! Does not get loaded from records!')
        return self.__vx_value

    @property
    def vy_value(self) -> float:
        """y component of viscosity """
        if self.__vy_value is None:
            raise ValueError('No results! Does not get loaded from records!')
        return self.__vy_value

    @property
    def vz_value(self) -> float:
        """y component of viscosity """
        if self.__vz_value is None:
            raise ValueError('No results! Does not get loaded from records!')
        return self.__vz_value

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
    def viscosity(self) -> float:
        """Calculated viscosity coeffecient averaged over the run 
            starting at the data offset value"""
        if self.__viscosity is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__viscosity
    
    @property
    def viscosity_stderror(self) -> float:
        """Error in the viscosity measurements"""
        if self.__viscosity_stderr is None:
            raise ValueError("No results! Does not get loaded from records")
        return self.__viscosity_stderr
    
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
            obtain measurements of viscosity
        timestep: float or None
            the difference in time between each step of the calculation
        outputsteps: int or None
            The number of steps in between the thermo writes to the log file
        dragcoeff: float or None
            this term affects the drag force that the thermostat function uses
            to calculate the temperature of the system.  
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
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'outputsteps' in kwargs:
            self.outputsteps = kwargs['outputsteps']
        if 'equilsteps' in kwargs:
            self.equilsteps = kwargs['equilsteps']
        if 'dragcoeff' in kwargs:
            self.dragcoeff = kwargs['dragcoeff']
        if 'sampleinterval' in kwargs:
            self.sampleinterval = kwargs['sampleinterval']
        if 'correlationlength' in kwargs:
            self.correlationlength = kwargs['correlationlength']
    

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
    
        # Load calculation-specific its
        self.runsteps = int(input_dict.get('runsteps', 1000000))
        self.outputsteps = int(input_dict.get('outputsteps', 2000))
        self.eq_thermosteps = int(input_dict.get('eq_termosteps', 0))
        self.eq_runsteps = int(input_dict.get('eq_runsteps', 0))
        self.sampleinterval = int(input_dict.get('sampleinterval', 5))
        self.correlationlength = int(input_dict.get('correlationlength', 200))

        # Load calculation-specific unitless floats
        self.temperature = float(input_dict['temperature'])
        self.dragcoeff = float(input_dict.get('dragcoeff', .2))

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
                "How many time steps to run the simulation. Default value is 1000000"]),
            'outputsteps':' '.join([
                "How often to write calculated values to the log file. Default",
                "value is 2000"]),
            'equilsteps':' '.join([
                "The number of equilibrium timesteps to run prior to evaluating the",
                "viscosity.  Useful if your initial configuration and velocities are",
                "not already in an equilibrium state.  Default value is 0."]),
            'dragcoeff':' '.join([
                "The damping in the thermostat calculations.  Default value is 0.2"]),
            'sampleinterval':' '.join([
                "How many frames the calculation averages over. This times the",
                "correlation length must be a divisor of the outputsteps.",
                "Default value is 5."]),
            'correlationlength':' '.join([
                "The number of averaged intervals for one calculation window.",
                "This time the sample interval must be a divisor of outputsteps.",
                "Default value is 200."])
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
                    'dragcoeff',
                    'runsteps',
                    'outputsteps',
                    'equilsteps',
                    'sampleinterval',
                    'correlationlength'
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
        return 'calculation_viscosity_green_kubo'

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

        run_params['timestep'] = uc.model(self.timestep,'ps')
        run_params['runsteps'] = self.runsteps
        run_params['outputsteps'] = self.outputsteps
        run_params['dragcoeff'] = self.dragcoeff
        run_params['equilsteps'] = self.equilsteps
        run_params['sampleinterval'] = self.sampleinterval
        run_params['correlationlength'] = self.correlationlength

        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(self.temperature, 'K')

        # Build results
        if self.status == 'finished':
            
            calc['pxy_values'] = uc.model(self.pxy_values.tolist(), f'{self.units.pressure_unit}')
            calc['pxz_values'] = uc.model(self.pxz_values.tolist(), f'{self.units.pressure_unit}')
            calc['pyz_values'] = uc.model(self.pyz_values.tolist(), f'{self.units.pressure_unit}')
            calc['vx_value'] = uc.model(self.vx_value, f'{self.units.pressure_unit}*ps')
            calc['vy_value'] = uc.model(self.vy_value, f'{self.units.pressure_unit}*ps')
            calc['vz_value'] = uc.model(self.vz_value, f'{self.units.pressure_unit}*ps')
            calc['measured_temperature'] = uc.model(self.measured_temperature, 'K')
            calc['measured_temperature_stderr'] = uc.model(self.measured_temperature_stderr, 'K')
            calc['viscosity'] = uc.model(self.viscosity, f'{self.units.pressure_unit}*ps')
            calc['viscosity_stderr'] = uc.model(self.viscosity_stderror, f'{self.units.pressure_unit}*ps')

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
        self.outputsteps = run_params['outputsteps']
        self.equilsteps = run_params['equilsteps']
        self.dragcoeff = run_params['dragcoeff']
        self.sampleinterval = run_params['sampleinterval']
        self.correlationlength = run_params['correlationlength']

        # Load phase-state info
        self.temperature = uc.value_unit(calc['phase-state']['temperature'])

        # Load results
        if self.status == 'finished':
            self.__pxy_values = uc.value_unit(calc['pxy_values']) 
            self.__pxz_values  = uc.value_unit(calc['pxz_values'])
            self.__pyz_values  = uc.value_unit(calc['pyz_values']) 
            self.__vx_value  = uc.value_unit(calc['vx_value']) 
            self.__vy_value  = uc.value_unit(calc['vy_value']) 
            self.__vz_value  = uc.value_unit(calc['vz_value']) 

            self.__viscosity = uc.value_unit(calc['viscosity'])
            self.__viscosity_stderr = uc.value_unit(calc['viscosity_stderr'])
            self.__measured_temperature = uc.value_unit(calc['measured_temperature'])
            self.__measured_temperature_stderr = uc.value_unit(calc['measured_temperature_stderr'])

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'temperature': load_query(
                style='float_match',
                name='temperature',
                path=f'{self.modelroot}.phase-state.temperature.value',
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
            meta['measured_viscosity'] = self.viscosity
            meta['measured_viscosity_stderr'] = self.viscosity_stderror

            meta['pxy_values'] = self.pxy_values
            meta['pxz_values'] = self.pxz_values
            meta['pyz_values'] = self.pyz_values
            meta['vx_value'] = self.vx_value
            meta['vy_value'] = self.vy_value
            meta['vz_value'] = self.vz_value

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
            'temperature': 1e-2,
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
        input_dict['outputsteps'] = self.outputsteps
        input_dict['dragcoeff'] = self.dragcoeff
        input_dict['equilsteps'] = self.equilsteps
        input_dict['sampleinterval'] = self.sampleinterval
        input_dict['correlationlength'] = self.correlationlength

        # Return input_dict
        return input_dict

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'init.dat',
            'log.lammps',
            'viscosity_green_kubo.in',
            'S0St.dat'
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
        self.__viscosity = results_dict["viscosity"]
        self.__viscosity_stderr = results_dict["viscosity_stderr"] 
        
        self.__pxy_values = results_dict['pxy_values']
        self.__pxz_values = results_dict['pxz_values']
        self.__pyz_values = results_dict['pyz_values']

        self.__vx_value = results_dict['vx_value']
        self.__vy_value = results_dict['vy_value']
        self.__vz_value = results_dict['vz_value']
        
        self.__lammps_output = results_dict['lammps_output']
