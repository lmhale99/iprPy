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
from .elastic_constants_dynamic import elastic_constants_dynamic
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value

class ElasticConstantsDynamic(Calculation):
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
        subsets = (self.commands, self.potential, self.system,
                   self.system_mods, self.units)

        # Initialize unique calculation attributes
        self.strainrange = 1e-6
        self.temperature = None
        self.randomseed = None
        self.equilsteps = 20000
        self.runsteps = 200000
        self.thermosteps = 100
        self.normalized_as = 'triclinic'
        self.__measured_pressure = None
        self.__C = None
        self.__Cij_born = None
        self.__Cij_fluc = None
        self.__Cij_kin = None
        
        # Define calc shortcut
        self.calc = elastic_constants_dynamic

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'elastic_constants_dynamic.py',
            'born_matrix.template'
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
    def strainrange(self) -> float:
        """float: The strain range to use for generating finite difference
           approximations for the virial stress."""
        return self.__strainrange

    @strainrange.setter
    def strainrange(self, val: Optional[float]):
        self.__strainrange = float(val)

    @property
    def equilsteps(self) -> int:
        """int: Number of MD steps during the equilibration stage"""
        return self.__equilsteps

    @equilsteps.setter
    def equilsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilsteps = val

    @property
    def runsteps(self) -> int:
        """int: Number of MD steps during the born matrix calculation stage"""
        return self.__runsteps

    @runsteps.setter
    def runsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__runsteps = val

    @property
    def thermosteps(self) -> int:
        """int: How often to sample thermo data"""
        return self.__thermosteps

    @thermosteps.setter
    def thermosteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__thermosteps = val

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
    def normalized_as(self) -> str:
        """str: Crystal family to use to normalize elastic constants"""
        return self.__normalized_as

    @normalized_as.setter
    def normalized_as(self, val: str):
        allowed = ['isotropic', 'cubic', 'hexagonal', 'tetragonal',
                   'rhombohedral', 'orthorhombic', 'monoclinic', 'triclinic']
        val = str(val).lower()
        if val not in allowed:
            raise ValueError('Invalid elastic constants normalization option')
        self.__normalized_as = val

    @property
    def measured_pressure(self) -> float:
        """float: Mean measured pressure during the nve run"""
        if self.__measured_pressure is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure

    @property
    def C(self) -> am.ElasticConstants:
        """atomman.ElasticConstants: Elastic constants"""
        if self.__C is None:
            raise ValueError('No results yet!')
        return self.__C

    @property
    def Cij_born(self) -> np.ndarray:
        """numpy.NDArray: The Born component of the Cij 6x6 array"""
        if self.__Cij_born is None:
            raise ValueError('No results yet!')
        return self.__Cij_born
    
    @property
    def Cij_fluc(self) -> np.ndarray:
        """numpy.NDArray: The fluctuation component of the Cij 6x6 array"""
        if self.__Cij_fluc is None:
            raise ValueError('No results yet!')
        return self.__Cij_fluc
    
    @property
    def Cij_kin(self) -> np.ndarray:
        """numpy.NDArray: The kinetic component of the Cij 6x6 array"""
        if self.__Cij_kin is None:
            raise ValueError('No results yet!')
        return self.__Cij_kin

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
            The temperature to run the calculation at.
        strainrange : float, optional
            The magnitude of strains to use to generate finite difference
            approximations for the exact virial stress.  Picking a good value may
            be dependent on the crystal structure and it is recommended to try
            multiple different values.  Default value is 1e-6.
        normalized_as : str, optional
            Crystal family to use to normalize elastic constants.
        equilsteps : int, optional
            Number of integration steps to perform prior to performing the
            born/matrix calculation to equilibrate the system.  Default value is
            20000.
        runsteps : int, optional
            Number of integration steps to perform during the born/matrix
            calculation.  Default value is 200000.
        thermosteps : int, optional
            How often to output thermo values to sample the computed stress and
            born/matrix values.
        randomseed : int or None, optional
            Random number seed used by LAMMPS in creating velocities and with
            the Langevin thermostat.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
        if 'strainrange' in kwargs:
            self.strainrange = kwargs['strainrange']
        if 'normalized_as' in kwargs:
            self.normalized_as = kwargs['normalized_as']
        if 'equilsteps' in kwargs:
            self.equilsteps = kwargs['equilsteps']
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'thermosteps' in kwargs:
            self.thermosteps = kwargs['thermosteps']
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

        # Load calculation-specific strings

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.equilsteps = int(input_dict.get('equilsteps', 20000))
        self.runsteps = int(input_dict.get('runsteps', 200000))
        self.thermosteps = input_dict.get('thermosteps', 100)
        self.randomseed = input_dict.get('randomseed', None)

        # Load calculation-specific unitless floats
        self.temperature = float(input_dict['temperature'])
        self.strainrange = float(input_dict.get('strainrange', 1e-6))

        # Load calculation-specific floats with units

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Set normalized_as from input_dict or ucell's crystal family
        if 'normalized_as' in input_dict:
            self.normalized_as = input_dict['normalized_as']
        else:     
            self.normalized_as = 'triclinic'

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
            assert 'temperature' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'atomicarchive load_file archive'

            params['archive_record'] = 'calculation_relax_dynamic'
            params['archive_temperature'] = kwargs['temperature']
            params['archive_load_key'] = 'final-system'
            params['archive_status'] = 'finished'
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
                "The temperature to run the calculation at.  Required."]),
            'strainrange': ' '.join([
                "The magnitude of strains to use to generate finite difference",
                "approximations for the exact virial stress.  Picking a good value may",
                "be dependent on the crystal structure and it is recommended to try",
                "multiple different values.  Default value is 1e-6."]),
            'normalized_as': ' '.join([
                "Crystal family to use to normalize elastic constants.  If not given",
                "will try to identify the crystal family of the unit cell."]),
            'equilsteps': ' '.join([
                "Number of integration steps to perform prior to performing the",
                "born/matrix calculation to equilibrate the system.  Default value is",
                "20000."]),
            'runsteps': ' '.join([
                "Number of integration steps to perform during the born/matrix",
                "calculation.  Default value is 200000."]),
            'thermosteps': ' '.join([
                "How often to output thermo values to sample the computed stress and",
                "born/matrix values."]),
            'randomseed': ' '.join([
                "Random number seed used by LAMMPS in creating velocities and with",
                "the Langevin thermostat.  Default is None which will select a",
                "random int between 1 and 900000000."]),
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
                self.system.keyset +
                [
                    'normalized_as'
                ]
            ] +

            # System mods keys
            [
                self.system_mods.keyset
            ] +

            # Temperature
            [
                [
                    'temperature',
                ]
            ] +

            # Strain range
            [
                [
                    'strainrange',
                ]
            ] +

            # Run parameters
            [
                [
                    'equilsteps',
                    'runsteps',
                    'thermosteps',
                    'randomseed',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-elastic-constants-dynamic'

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

        run_params['strainrange'] = self.strainrange
        run_params['normalized_as'] = self.normalized_as
        run_params['equilsteps'] = self.equilsteps
        run_params['runsteps'] = self.runsteps
        run_params['thermosteps'] = self.thermosteps
        run_params['randomseed'] = self.randomseed
        
        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(self.temperature, 'K')

        # Build results
        if self.status == 'finished':

            # Save measured phase-state info
            calc['measured-phase-state'] = mps = DM()
            mps['pressure'] = uc.model(self.measured_pressure,
                                          self.units.pressure_unit)

            raw = calc['raw-Cij-components'] = DM()
            raw['born'] = uc.model(self.Cij_born, self.units.pressure_unit)
            raw['fluctuation'] = uc.model(self.Cij_fluc, self.units.pressure_unit)
            raw['kinetic'] = uc.model(self.Cij_kin, self.units.pressure_unit)

            calc['elastic-constants'] = DM()
            calc['elastic-constants']['Cij'] = uc.model(self.C.Cij,
                                                        self.units.pressure_unit)

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
        self.strainrange = run_params['strainrange']
        self.normalized_as = run_params['normalized_as']
        self.equilsteps = run_params['equilsteps']
        self.runsteps = run_params['runsteps']
        self.thermosteps = run_params['thermosteps']
        self.randomseed = run_params['randomseed']

        # Load phase-state info
        self.temperature = uc.value_unit(calc['phase-state']['temperature'])

        # Load results
        if self.status == 'finished':


            mps = calc['measured-phase-state']
            self.__measured_pressure = uc.value_unit(mps['pressure'])
            
            raw = calc['raw-Cij-components']
            self.__Cij_born = uc.value_unit(raw['born'])
            self.__Cij_fluc = uc.value_unit(raw['fluctuation'])
            self.__Cij_kin = uc.value_unit(raw['kinetic'])

            Cij = uc.value_unit(calc['elastic-constants']['Cij'])
            self.__C = am.ElasticConstants(Cij=Cij)

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'temperature': load_query(
                style='float_match',
                name='temperature',
                path=f'{self.modelroot}.phase-state.temperature.value',
                description='search by temperature in Kelvin'),
            'strainrange': load_query(
                style='float_match',
                name='strainrange',
                path=f'{self.modelroot}.calculation.run-parameter.strainrange',
                description='search by strain range used'),
            'equilsteps': load_query(
                style='int_match',
                name='equilsteps',
                path=f'{self.modelroot}.calculation.run-parameter.equilsteps',
                description='search by number of equilibration integration steps'),
            'runsteps': load_query(
                style='int_match',
                name='runsteps',
                path=f'{self.modelroot}.calculation.run-parameter.runsteps',
                description='search by number of computation integration steps'),
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
        meta['strainrange'] = self.strainrange
        meta['normalized_as'] = self.normalized_as
        meta['equilsteps'] = self.equilsteps
        meta['runsteps'] = self.runsteps

        # Extract results
        if self.status == 'finished':
            meta['measured_pressure'] = self.measured_pressure

            meta['C'] = self.C
            meta['Cij_born'] = self.Cij_born
            meta['Cij_fluc'] = self.Cij_fluc
            meta['Cij_kin'] = self.Cij_kin

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
            'strainrange':1e-10,
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
        input_dict['temperature'] = self.temperature
        input_dict['strainrange'] = self.strainrange
        input_dict['normalized_as'] = self.normalized_as
        input_dict['equilsteps'] = self.equilsteps
        input_dict['runsteps'] = self.runsteps
        input_dict['thermosteps'] = self.thermosteps
        input_dict['randomseed'] = self.randomseed

        # Return input_dict
        return input_dict

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'init.dat',
            'log.lammps',
            'born_matrix.in',
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

        self.__measured_pressure = results_dict['measured_pressure']
        self.__C = results_dict['C']
        self.__Cij_born = results_dict['Cij_born']
        self.__Cij_fluc = results_dict['Cij_fluc']
        self.__Cij_kin = results_dict['Cij_kin']
