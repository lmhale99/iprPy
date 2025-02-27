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
from .melting_temperature import melting_temperature
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value, boolean

class MeltingTemperature(Calculation):
    """Class for managing two-phase coexistence melting temperature simulations"""
    
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
        self.temperature_guess = None
        self.temperature_solid = None
        self.temperature_liquid = None
        self.pressure = 0.0
        self.ptm_structures = None
        self.meltsteps = 10000
        self.scalesteps = 10000
        self.runsteps = 200000
        self.thermosteps = 100
        self.dumpsteps = None
        self.randomseed = None

        self.__melting_temperature = None
        self.__fraction_solids = None

########################################################

        # Define calc shortcut
        self.calc = melting_temperature

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'melting_temperature.py',
            'two_phase_melting_temperature.template'
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
    def temperature_guess(self) -> float:
        """float: Initial guess melting temperature"""
        if self.__temperature_guess is None:
            raise ValueError('temperature_guess not set!')
        return self.__temperature_guess

    @temperature_guess.setter
    def temperature_guess(self, val: float):
        if val is not None:
            val = float(val)
            assert val >= 0.0
        self.__temperature_guess = val

    @property
    def temperature_solid(self) -> float:
        """float: Temperature to initially use in the solid region"""
        if self.__temperature_solid is None:
            return 0.5 * self.temperature_guess
        else:
            return self.__temperature_solid

    @temperature_solid.setter
    def temperature_solid(self, val: Optional[float]):
        if val is not None:
            val = float(val)
            assert val >= 0.0
        self.__temperature_solid = val

    @property
    def temperature_liquid(self) -> float:
        """float: Temperature to initially use in the liquid region"""
        if self.__temperature_liquid is None:
            return 1.25 * self.temperature_guess
        else:
            return self.__temperature_liquid

    @temperature_liquid.setter
    def temperature_liquid(self, val: Optional[float]):
        if val is not None:
            val = float(val)
            assert val >= 0.0
        self.__temperature_liquid = val

    @property
    def pressure(self) -> float:
        """float: Target relaxation pressure"""
        return self.__pressure

    @pressure.setter
    def pressure(self, val: float):
        self.__pressure = float(val)

    @property
    def ptm_structures(self) -> Optional[str]:
        """str or None: The structures to use with polyhedral template matching"""
        return self.__ptm_structures

    @ptm_structures.setter
    def ptm_structures(self, val: Optional[str]):
        if val is not None:
            val = str(val)
        self.__ptm_structures = val

    @property
    def meltsteps(self) -> int:
        """int : The number of MD steps to use when creating the two-phase system"""
        return self.__meltsteps

    @meltsteps.setter
    def meltsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__meltsteps = val

    @property
    def scalesteps(self) -> int:
        """int : The number of MD steps to scale temps to the guess"""
        return self.__scalesteps

    @scalesteps.setter
    def scalesteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__scalesteps = val

    @property
    def runsteps(self) -> int:
        """int : The number of MD steps to perform for two-phase coexistence"""
        return self.__runsteps

    @runsteps.setter
    def runsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__runsteps = val

    @property
    def thermosteps(self) -> int:
        """int : How often termo data is recorded"""
        return self.__thermosteps

    @thermosteps.setter
    def thermosteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__thermosteps = val

    @property
    def dumpsteps(self) -> int:
        """int : How often atomic configurations are dumped"""
        if self.__dumpsteps is None:
            return self.meltsteps + self.scalesteps + self.runsteps
        else:
            return self.__dumpsteps

    @dumpsteps.setter
    def dumpsteps(self, val: int):
        if val is None:
            self.__dumpsteps = None
        else:
            val = int(val)
            assert val >= 0
            self.__dumpsteps = val

    @property
    def randomseed(self) -> int:
        """int: Random number generator seed"""
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
    def melting_temperature(self) -> float:
        """float: The measured melting temperature"""
        if self.__melting_temperature is None:
            raise ValueError('No results yet!')
        return self.__melting_temperature
    
    @property
    def fraction_solids(self) -> list:
        """list: Estimates of the fraction of the system that is solid at different dump steps"""
        if self.__fraction_solids is None:
            raise ValueError('No results yet!')
        return self.__fraction_solids

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
        temperature_guess : float, optional
            The initial guess for the melting temperature to start the two
            phase coexistence simulation at.
        temperature_solid : float, optional
            The temperature to use for the solid half during the melt stage
            of the calculation.
        temperature_liquid : float, optional
            The temperature to use for the liquid half during the melt stage
            of the calculation.
        pressure : float, optional
            The hydrostatic pressure to use with the barostat.
        meltsteps : int, optional
            The number of integration steps to perform for the melt stage.
        scalesteps : int, optional
            The number of integration steps to use for scaling the temperatures
            of the two phases to the guess temperature.
        runsteps : int, optional
            The number of NPH integration steps to perform to estimate the
            melting temperature.
        thermosteps : int, optional
            Indicates how often the thermo data is output.
        dumpsteps : int, optional
            Indicates how often the atomic configuration is output to a LAMMPS
            dump file.
        randomseed : int, optional
            A random number generator seed to use for constructing the initial
            atomic velocities.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values

        if 'temperature_guess' in kwargs:
            self.temperature_guess = kwargs['temperature_guess']
        if 'temperature_solid' in kwargs:
            self.temperature_solid = kwargs['temperature_solid']
        if 'temperature_liquid' in kwargs:
            self.temperature_liquid = kwargs['temperature_liquid']
        if 'pressure' in kwargs:
            self.pressure = kwargs['pressure']
        if 'ptm_structures' in kwargs:
            self.ptm_structures = kwargs['ptm_structures']
        if 'meltsteps' in kwargs:
            self.meltsteps = kwargs['meltsteps']
        if 'scalesteps' in kwargs:
            self.scalesteps = kwargs['scalesteps']
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'thermosteps' in kwargs:
            self.thermosteps = kwargs['thermosteps']
        if 'dumpsteps' in kwargs:
            self.dumpsteps = kwargs['dumpsteps']
        if 'randomseed' in kwargs:
            self.randomseed = kwargs['randomseed']

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
        input_dict['sizemults'] = input_dict.get('sizemults', '10 10 20')

        # Load calculation-specific strings
        self.ptm_structures = input_dict.get('ptm_structures', None)

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.meltsteps = int(input_dict.get('meltsteps', 10000))
        self.scalesteps = int(input_dict.get('scalesteps', 10000))
        self.runsteps = int(input_dict.get('runsteps', 200000))
        self.thermosteps = int(input_dict.get('thermosteps', 100))
        self.dumpsteps = input_dict.get('dumpsteps', None)
        self.randomseed = input_dict.get('randomseed', 1)

        # Load calculation-specific unitless floats
        self.temperature_guess = input_dict['temperature_guess']
        self.temperature_liquid = input_dict.get('temperature_liquid', None)
        self.temperature_solid = input_dict.get('temperature_solid', None)

        # Load calculation-specific floats with units
        self.pressure = value(input_dict, 'pressure',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')

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
            raise NotImplementedError('Not yet implemented')
        
        else:
            raise ValueError(f'Unknown branch {branch}')

        return params
    
    @property
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'temperature_guess': ' '.join([
                "The initial guess for the melting temperature.  Required."]),
            'temperature_liquid': ' '.join([
                "The temperature to use in the liquid region when creating the",
                "two-phase region.  Default value is 1.25 * temperature_guess."]),
            'temperature_solid': ' '.join([
                "The temperature to use in the solid region when creating the",
                "two-phase region.  Default value is 0.5 * temperature_guess."]),
            'pressure': ' '.join([
                "The pressure to relax the box to. Default value is 0.0 GPa."]),
            'ptm_structures': ' '.join([
                "The structure option to use with LAMMPS compute ptm/atom to",
                "indicate which solid structures to search for.  If not given,",
                "then no ptm calculation will be performed."]),
            'meltsteps': ' '.join([
                "The number of MD integration steps to run during the melt stage",
                "to generate the two-phase region.  Default value is 10000."]),
            'scalesteps': ' '.join([
                "The number of MD integration steps to run during the scale stage",
                "to scale temperatures to the guess temperature.  Default value is 10000."]),
            'runsteps': ' '.join([
                "The number of MD integration steps to run to obtain the two-phase",
                "coexistence and estimate the melting temperature.  Default value",
                "is 200000."]),
            'thermosteps': ' '.join([
                "How often LAMMPS will print thermo data.  Default value is",
                "100."]),
            'dumpsteps': ' '.join([
                "How often LAMMPS will save the atomic configuration to a",
                "LAMMPS dump file.  Default value is meltsteps+scalesteps+runsteps,",
                "meaning that only the initial and final states are saved."]),
            'randomseed': ' '.join([
                "An int random number seed to use for generating initial velocities.",
                "A random int will be selected if not given."]),
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
            + [
                'ptm_structures'
            ]
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

            # Pressure parameters
            [
                [
                    'pressure',
                ]
            ] +

            # Temperature
            [
                [
                    'temperature_guess',
                    'temperature_solid',
                    'temperature_liquid',
                ]
            ] +

            # Run parameters
            [
                [
                    'meltsteps',
                    'scalesteps',
                    'runsteps',
                    'thermosteps',
                    'dumpsteps',   
                ]
            ] + 
            
            [
                [
                    'randomseed',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-melting-temperature'

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

        run_params['temperature_guess'] = self.temperature_guess
        run_params['temperature_liquid'] = self.temperature_liquid
        run_params['temperature_solid'] = self.temperature_solid
        run_params['ptm_structures'] = self.ptm_structures
        run_params['meltsteps'] = self.meltsteps
        run_params['scalesteps'] = self.scalesteps
        run_params['runsteps'] = self.runsteps
        run_params['thermosteps'] = self.thermosteps
        run_params['randomseed'] = self.randomseed

        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['pressure'] = uc.model(self.pressure,
                                                   self.units.pressure_unit)

        # Build results
        if self.status == 'finished':
            # Save measured box parameter info
            calc['melting-temperature'] = uc.model(self.melting_temperature, 'K')
            calc['fraction-solids'] = self.fraction_solids

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
        self.temperature_guess = run_params['temperature_guess']
        self.temperature_liquid = run_params['temperature_liquid']
        self.temperature_solid = run_params['temperature_solid']
        self.ptm_structures = run_params['ptm_structures']
        self.meltsteps = run_params['meltsteps']
        self.scalesteps = run_params['scalesteps']
        self.runsteps = run_params['runsteps']
        self.thermosteps = run_params['thermosteps']
        self.randomseed = run_params['randomseed']

        # Load phase-state info
        self.pressure = uc.value_unit(calc['phase-state']['pressure'])

        # Load results
        if self.status == 'finished':
            self.__melting_temperature = uc.value_unit(calc['melting-temperature'])
            self.__fraction_solids = calc.aslist('fraction-solids')

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
        meta['temperature_guess'] = self.temperature_guess
        meta['pressure'] = self.pressure
        meta['randomseed'] = self.randomseed

        # Extract results
        if self.status == 'finished':
            meta['melting_temperature'] = self.melting_temperature
            meta['fraction_solids'] = self.fraction_solids

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

            'randomseed',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'temperature_guess':1e-2,
            'pressure':1e-2,
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
        input_dict['temperature_guess'] = self.temperature_guess
        input_dict['temperature_liquid'] = self.temperature_liquid
        input_dict['temperature_solid'] = self.temperature_solid
        input_dict['pressure'] = self.pressure
        input_dict['ptm_structures'] = self.ptm_structures

        input_dict['meltsteps'] = self.meltsteps
        input_dict['scalesteps'] = self.scalesteps
        input_dict['runsteps'] = self.runsteps
        input_dict['thermosteps'] = self.thermosteps
        input_dict['dumpsteps'] = self.dumpsteps
        input_dict['randomseed'] = self.randomseed

        # Return input_dict
        return input_dict

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'init.dat',
            'log.lammps',
            'two_phase_melting_temp.in',
            '*.dump',
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
        self.__melting_temperature = results_dict['melting_temperature']
        self.__fraction_solids = results_dict['fraction_solids']
