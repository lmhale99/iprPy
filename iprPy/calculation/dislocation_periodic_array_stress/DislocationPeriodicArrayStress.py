# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union

import numpy as np

import pandas as pd

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import unitfloat

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .dislocation_periodic_array_stress import dislocation_periodic_array_stress
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad)
from ...input import value, boolean

class DislocationPeriodicArrayStress(Calculation):
    """Class for managing periodic array of dislocations constructions and relaxations"""

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
        self.temperature = None
        self.linesizemult = 1
        self.sigma_screw = 0.0
        self.sigma_edge = 0.0
        self.thermosteps = 100
        self.dumpsteps = None
        self.runsteps = 1000000
        self.rigidbounds = True
        self.createvelocities = True
        self.randomseed = None

        self.__thermo = None
 
        # Define calc shortcut
        self.calc = dislocation_periodic_array_stress

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'dislocation_periodic_array_stress.py'
        ]

############################## Class attributes ###############################

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
    def temperature(self) -> float:
        """float: Temperature to run NVT at"""
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
            self.__temperature = float(val)

    @property
    def linesizemult(self) -> int:
        """int: Number of replicas to make along the line direction"""
        return self.__linesizemult

    @linesizemult.setter
    def linesizemult(self, val: int):
            val = int(val)
            assert val >= 1
            self.__linesizemult = val

    @property
    def sigma_screw(self) -> float:
        """float: Shear stress to apply for driving screw dislocation components"""
        return self.__sigma_screw

    @sigma_screw.setter
    def sigma_screw(self, val: unitfloat):
            self.__sigma_screw = uc.set_in_units(val)

    @property
    def sigma_edge(self) -> float:
        """float: Shear stress to apply for driving screw dislocation components"""
        return self.__sigma_edge

    @sigma_edge.setter
    def sigma_edge(self, val: unitfloat):
            self.__sigma_edge = uc.set_in_units(val)

    @property
    def thermosteps(self) -> int:
        """int: Number of time steps to output thermo data"""
        return self.__thermosteps

    @thermosteps.setter
    def thermosteps(self, val: int):
            val = int(val)
            assert val >= 0
            self.__thermosteps = val

    @property
    def dumpsteps(self) -> Optional[int]:
        """int or None: Number of time steps to create dump files"""
        return self.__dumpsteps

    @dumpsteps.setter
    def dumpsteps(self, val: Optional[int]):
            if val is None:
                self.__dumpsteps = None
            else:
                val = int(val)
                assert val >= 0
                self.__dumpsteps = val

    @property
    def runsteps(self) -> int:
        """int: Number of time steps to run NVT for"""
        return self.__runsteps

    @runsteps.setter
    def runsteps(self, val: int):
            val = int(val)
            assert val >= 0
            self.__runsteps = val

    @property
    def rigidbounds(self) -> bool:
        """bool: Flag indicating if the boundary regions are rigid"""
        return self.__rigidbounds

    @rigidbounds.setter
    def rigidbounds(self, val: bool):
        self.__rigidbounds = boolean(val)

    @property
    def createvelocities(self) -> bool:
        """bool: Flag indicating if new rando velocities will be created"""
        return self.__createvelocities

    @createvelocities.setter
    def createvelocities(self, val: bool):
        self.__createvelocities = boolean(val)

    @property
    def randomseed(self) -> int:
        """int: random number generator seed to use"""
        return self.__randomseed

    @randomseed.setter
    def randomseed(self, val: int):
        self.__randomseed = am.lammps.seed(val)

    @property
    def thermo(self) -> pd.DataFrame:
        """pandas.DataFrame: The thermo data from the simulation"""
        if self.__thermo is None:
            raise ValueError('No results yet!')
        return self.__thermo
   
    

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
        temperature : float, optional
            The temperature to run the simulation at.
        linesizemult : int, optional
            Indicates how many times to replicate the initial configuration along
            the dislocation line direction prior to running the simulation.  This
            allows for easy exploration of multiple dislocation line lengths.
        sigma_screw : unitfloat, optional
            The shear stress to apply to the system that acts on the screw component
            of dislocations.
        sigma_edge: unitfloat, optional
            The shear stress to apply to the system that acts on the edge component
            of dislocations.
        thermosteps : int, optional
            How often to output thermo data.  Default value is 100 (timesteps).
        dumpsteps : int or None, optional
            How often to output atomic configurations as dump files.
        runsteps : int, optional
            The total number of MD steps to run.
        rigidbounds : bool, optional
            If True the top and bottom boundary regions will be treated
            as rigid bodies.  If False, then the atoms in the boundaries will be
            allowed to relax but will still have the shear stress(es) applied to
            them.
        createvelocities : bool, optional
            If True new random velocities will be assigned to the
            non-rigid atoms based on 2*temperature. Setting this to False will
            use any pre-assigned velocities to the atoms.
        randomseed : int or None, optional
            Random number seed used by LAMMPS.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
        if 'linesizemult' in kwargs:
            self.linesizemult = kwargs['linesizemult']
        if 'sigma_screw' in kwargs:
            self.sigma_screw = kwargs['sigma_screw']
        if 'sigma_edge' in kwargs:
            self.sigma_edge = kwargs['sigma_edge']
        if 'thermosteps' in kwargs:
            self.thermosteps = kwargs['thermosteps']
        if 'dumpsteps' in kwargs:
            self.dumpsteps = kwargs['dumpsteps']
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'rigidbounds' in kwargs:
            self.rigidbounds = kwargs['rigidbounds']
        if 'createvelocities' in kwargs:
            self.createvelocities = kwargs['createvelocities']
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
        input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')

        # Load calculation-specific strings
        self.boundaryshape = input_dict.get('dislocation_boundaryshape',
                                            'cylinder')

        # Load calculation-specific booleans
        self.onlylinear = boolean(input_dict.get('dislocation_onlylinear', False))
        self.boundaryscale = boolean(input_dict.get('dislocation_boundaryscale',
                                                    False))

        # Load calculation-specific integers
        self.randomseed = input_dict.get('randomseed', None)
        self.annealsteps = input_dict.get('annealsteps', None)

        # Load calculation-specific unitless floats
        self.annealtemperature = float(input_dict.get('annealtemperature', 0.0))
        self.strohtol = float(input_dict.get('strohtol', 1e-8))

        # Load calculation-specific floats with units
        self.boundarywidth = value(input_dict, 'dislocation_boundarywidth',
                                   default_unit=self.units.length_unit,
                                   default_term='0 angstrom')
        self.duplicatecutoff = value(input_dict, 'dislocation_duplicatecutoff',
                                     default_unit=self.units.length_unit,
                                     default_term='0.5 angstrom')

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)


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

        if branch == 'main':
            
            # Check for required kwargs
            assert 'lammps_command' in kwargs
            assert 'temperature' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'atomicarchive load_file archive'
            
            params['archive_record'] = 'calculation_dislocation_periodic_array'
            params['archive_load_key'] = 'defect-system'
            params['archive_status'] = 'finished'
        
            # Copy kwargs to params
            for key in kwargs:
    
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'parent_{key}'] = kwargs[key]
    
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
            'annealtemperature': ' '.join([
                "The temperature at which to anneal the dislocation system",
                "If 0, then no MD anneal will be performed."]),
            'annealsteps': ' '.join([
                "The number of MD steps to perform at  the anneal temperature",
                "before running the energy/force minimization.  Default value",
                "is 0 if annealtemperature=0, and 10,000 if annealtemperature > 0."]),
            'strohtol':  ' '.join([
                "The tolerance to use for validating that the Stroh elasticity",
                "solution calculations are valid.  Default value is 1e-8, but",
                "may need to be increased..."]),
            'randomseed': ' '.join([
                "An int random number seed to use for generating initial velocities.",
                "A random int will be selected if not given."]),
            'dislocation_duplicatecutoff': ' '.join([
                "The cutoff distance to use for determining duplicate atoms to delete",
                "associated with the extra half-plane formed by a dislocation's edge",
                "component.  Default value is 0.5 Angstroms."]),
            'dislocation_boundarywidth': ' '.join([
                "The minimum thickness of the boundary region."]),
            'dislocation_boundaryscale': ' '.join([
                "Boolean indicating if boundarywidth is taken as Cartesian (False)",
                "or scaled by the loaded unit cell's a lattice parameter."]),
            'dislocation_onlylinear': ' '.join([
                "Boolean, which if True will only use linear gradient displacements",
                "to form the dislocation and not the Volterra solution displacements.",
                "Setting this to be True is useful for screw dislocations that",
                "dissociate as it ensures that the resulting structure will dissociate",
                "along the correct slip plane."]),
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
                'dislocation_duplicatecutoff',
                'dislocation_boundarywidth',
                'dislocation_boundaryscale',
                'dislocation_onlylinear',
                'strohtol',
            ]
        )
        return keys

    @property
    def multikeys(self) -> list:
        """list: Calculation key sets that can have multiple values during prepare."""
        keys = (
            # Universal multikeys
            super().multikeys +

            # Combination of potential, system and elastic keys
            [
                self.potential.keyset +
                self.system.keyset +
                self.elastic.keyset
            ] +

            # Defect multikeys
            self.defect.multikeys +

            # Combination of minimize and run parameter keys
            [
                self.minimize.keyset + [
                    'randomseed',
                    'annealtemperature',
                    'annealsteps',
                ]
            ]
        )

        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-dislocation-periodic-array'

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
        self.defect.build_model(calc, after='system-info')
        self.minimize.build_model(calc)
        self.elastic.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']

        run_params['dislocation_boundarywidth'] = self.boundarywidth
        run_params['dislocation_boundaryscale'] = self.boundaryscale
        run_params['dislocation_onlylinear'] = self.onlylinear
        run_params['annealtemperature'] = self.annealtemperature
        run_params['annealsteps'] = self.annealsteps

        # Build results
        if self.status == 'finished':
            calc['base-system'] = DM()
            calc['base-system']['artifact'] = DM()
            calc['base-system']['artifact']['file'] = self.dumpfile_base
            calc['base-system']['artifact']['format'] = 'atom_dump'
            calc['base-system']['symbols'] = self.symbols_base

            calc['defect-system'] = DM()
            calc['defect-system']['artifact'] = DM()
            calc['defect-system']['artifact']['file'] = self.dumpfile_defect
            calc['defect-system']['artifact']['format'] = 'atom_dump'
            calc['defect-system']['symbols'] = self.symbols_defect
            calc['defect-system']['potential-energy'] = uc.model(self.potential_energy_defect,
                                                                 self.units.energy_unit)

            calc['elastic-solution'] = elsol = DM()
            elsol['pre-ln-factor'] = uc.model(self.preln,
                                             f"{self.units.energy_unit}/{self.units.length_unit}")

            elsol['K-tensor'] = uc.model(self.K_tensor,
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
        self.boundarywidth = run_params['dislocation_boundarywidth']
        self.boundaryscale = run_params['dislocation_boundaryscale']
        self.onlylinear = run_params['dislocation_onlylinear']
        self.annealtemperature = run_params['annealtemperature']
        self.annealsteps = run_params['annealsteps']

        # Load results
        if self.status == 'finished':
            self.__dumpfile_base = calc['base-system']['artifact']['file']
            self.__symbols_base = calc['base-system']['symbols']

            self.__dumpfile_defect = calc['defect-system']['artifact']['file']
            self.__symbols_defect = calc['defect-system']['symbols']

            elsol = calc['elastic-solution']
            self.__preln = uc.value_unit(elsol['pre-ln-factor'])
            self.__K_tensor = uc.value_unit(elsol['K-tensor'])

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
        meta['boundarywidth'] = self.boundarywidth
        meta['boundaryscale'] = self.boundaryscale
        meta['onlylinear'] = self.onlylinear
        meta['annealtemperature'] = self.annealtemperature
        meta['annealsteps'] = self.annealsteps

        # Extract results
        if self.status == 'finished':            
            meta['dumpfile_base'] = self.dumpfile_base
            meta['dumpfile_defect'] = self.dumpfile_defect
            meta['symbols_base'] = self.symbols_base
            meta['symbols_defect'] = self.symbols_defect
            #meta['potential_energy_defect'] = self.potential_energy_defect
            meta['preln'] = self.preln
            meta['K_tensor'] = self.K_tensor

        return meta

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',

            'load_file',
            'load_options',
            'symbols',

            'potential_LAMMPS_key',
            'potential_key',

            'a_mult',
            'b_mult',
            'c_mult',

            'dislocation_key',

            'annealsteps',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'annealtemperature':1,
        }

    def isvalid(self) -> bool:
        return self.system.family == self.defect.family

########################### Calculation interactions ##########################

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""

        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Modify inputs for calculation
        input_dict['annealtemp'] = self.annealtemperature
        input_dict['annealsteps'] = self.annealsteps
        input_dict['randomseed'] = self.randomseed
        input_dict['linear'] = self.onlylinear
        input_dict['cutoff'] = self.duplicatecutoff
        input_dict['boundarywidth'] = self.boundarywidth
        input_dict['boundaryscale'] = self.boundaryscale
        input_dict['tol'] = self.strohtol

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
        self.__dumpfile_base = results_dict['dumpfile_base']
        self.__dumpfile_defect = results_dict['dumpfile_disl']
        self.__symbols_base = results_dict['symbols_base']
        self.__symbols_defect = results_dict['symbols_disl']
        self.__potential_energy_defect = results_dict['E_total_disl']
        self.__dislocation = results_dict['dislocation']
