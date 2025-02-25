# coding: utf-8

# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union
import random

import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .dislocation_dipole import dislocation_dipole
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, LammpsMinimize, Dislocation,
                                   AtommanElasticConstants)

class DislocationDipole(Calculation):
    """Class for managing dislocation dipole constructions and relaxation"""

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
        self.__minimize = LammpsMinimize(self)
        self.__defect = Dislocation(self)
        self.__elastic = AtommanElasticConstants(self)
        subsets = (self.commands, self.potential, self.system,
                   self.elastic, self.minimize, self.defect, self.units)

        # Initialize unique calculation attributes
        self.annealtemperature = 0.0
        self.annealsteps = None
        self.randomseed = None
        self.__dumpfile_base = None
        self.__dumpfile_defect = None
        self.__symbols_base = None
        self.__symbols_defect = None
        self.__potential_energy_defect = None
        self.__dislocation = None
        self.__preln = None
        self.__K_tensor = None

        # Define calc shortcut
        self.calc = dislocation_dipole

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'dislocation_dipole.py',
            'disl_relax.template'
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
    def minimize(self) -> LammpsMinimize:
        """LammpsMinimize subset"""
        return self.__minimize

    @property
    def defect(self) -> Dislocation:
        """Dislocation subset"""
        return self.__defect

    @property
    def elastic(self) -> AtommanElasticConstants:
        """AtommanElasticConstants subset"""
        return self.__elastic

    @property
    def annealtemperature(self) -> float:
        """float: Temperature to use for annealing the system"""
        return self.__annealtemperature

    @annealtemperature.setter
    def annealtemperature(self, val: float):
        val = float(val)
        assert val >= 0.0
        self.__annealtemperature = float(val)

    @property
    def annealsteps(self) -> int:
        """int: Number of time steps to use for annealing the system"""
        if self.__annealsteps is None:
            if self.annealtemperature == 0.0:
                return 0
            else:
                return 10000
        else:
            return self.__annealsteps

    @annealsteps.setter
    def annealsteps(self, val: int):
        if val is None:
            self.__annealsteps = None
        else:
            self.__annealsteps = int(val)

    @property
    def randomseed(self) -> int:
        """int: random number generator seed to use"""
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
    def dumpfile_base(self) -> str:
        """str: Name of the LAMMPS dump file of the 0 shift reference system"""
        if self.__dumpfile_base is None:
            raise ValueError('No results yet!')
        return self.__dumpfile_base

    @property
    def dumpfile_defect(self) -> str:
        """str: Name of the LAMMPS dump file of the defect system"""
        if self.__dumpfile_defect is None:
            raise ValueError('No results yet!')
        return self.__dumpfile_defect

    @property
    def symbols_base(self) -> list:
        """list: Model symbols for the base system"""
        if self.__symbols_base is None:
            raise ValueError('No results yet!')
        return self.__symbols_base

    @property
    def symbols_defect(self) -> list:
        """list: Model symbols for the defect system"""
        if self.__symbols_defect is None:
            raise ValueError('No results yet!')
        return self.__symbols_defect

    @property
    def potential_energy_defect(self) -> float:
        """float: Potential energy of the defect system"""
        if self.__potential_energy_defect is None:
            raise ValueError('No results yet!')
        return self.__potential_energy_defect

    @property
    def dislocation(self) -> am.defect.Dislocation:
        """atomman.defect.Dislocation: Volterra dislocation solution"""
        if self.__dislocation is None:
            raise ValueError('No results yet!')
        return self.__dislocation

    @property
    def preln(self) -> float:
        """float: The dislocation's elastic pre-ln energy factor"""
        if self.__preln is None:
            return self.dislocation.dislsol.preln
        else:
            return self.__preln

    @property
    def K_tensor(self) -> np.ndarray:
        """numpy.ndarray: The dislocation's elastic K tensor"""
        if self.__K_tensor is None:
            return self.dislocation.dislsol.K_tensor
        else:
            return self.__K_tensor

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
        annealtemperature : float, optional
            The temperature to use for MD annealing steps.
        annealsteps : int, optional
            The number of MD annealing steps to perform.
        randomseed : int, optional
            A random number seed to use for generating the initial velocities
            for the MD anneal.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'annealtemperature' in kwargs:
            self.annealtemperature = kwargs['annealtemperature']
        if 'annealsteps' in kwargs:
            self.annealsteps = kwargs['annealsteps']
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
        
        # Load calculation-specific booleans
        
        # Load calculation-specific integers
        self.randomseed = input_dict.get('randomseed', None)
        self.annealsteps = input_dict.get('annealsteps', None)

        # Load calculation-specific unitless floats
        self.annealtemperature = float(input_dict.get('annealtemperature', 0.0))

        # Load calculation-specific floats with units
        
        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load minimization parameters
        self.minimize.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Load defect parameters
        self.defect.load_parameters(input_dict)

        # Load elastic constants
        self.elastic.load_parameters(input_dict)

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

        # Check for required kwargs
        assert 'lammps_command' in kwargs

        # Set common workflow settings
        params['buildcombos'] = [
            'atomicarchive load_file parent',
            'defect dislocation_file'
        ]
        params['parent_record'] = 'calculation_elastic_constants_static'
        params['parent_load_key'] = 'system-info'
        params['parent_strainrange'] = 1e-7
        params['defect_record'] = 'dislocation'

        params['annealtemperature'] = '10'
        params['annealsteps'] = '10000000'
        params['ftol'] = '1e-6 eV/angstrom'
        params['maxiterations'] = '10000'
        params['maxevaluations'] = '100000'

        # Set branch-specific parameters
        if branch == 'dc_screw_a':
            params['parent_family'] = 'A4--C--dc'
            params['defect_id'] = 'A1--Cu--fcc--a-2-110--90-edge--{100}'
            params['sizemults'] = '1 8 5'

        elif branch == 'dc_screw_b':
            params['parent_family'] = 'A4--C--dcc'
            params['defect_id'] = 'A2--W--bcc--a-2-111--0-screw--{110}'
            params['sizemults'] = '1 8 5'

        elif branch == 'dc_screw_c':
            params['parent_family'] = 'A4--C--dc'
            params['defect_id'] = 'A2--W--bcc--a-2-111--90-edge--{110}'
            params['sizemults'] = '1 8 5'
            params['annealtemperature'] = '0'
            params['annealsteps'] = '0'

        elif branch == 'dc_screw_c2':
            params['parent_family'] = 'A4--C--dc'
            params['defect_id'] = 'A2--W--bcc--a-2-111--90-edge--{112}'
            params['sizemults'] = '1 8 5'

        else:
            raise ValueError(f'Unknown branch {branch}')

        # Copy kwargs to params
        for key in kwargs:

            # Rename potential-related terms for buildcombos
            if key[:10] == 'potential_':
                params[f'parent_{key}'] = kwargs[key]

            # Copy/overwrite other terms
            else:
                params[key] = kwargs[key]

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
            + []
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
        return 'calculation-dislocation-dipole'

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
        self.annealtemperature = run_params['annealtemperature']
        self.annealsteps = run_params['annealsteps']

        # Load results
        if self.status == 'finished':
            self.__dumpfile_base = calc['base-system']['artifact']['file']
            self.__symbols_base = calc['base-system']['symbols']

            self.__dumpfile_defect = calc['defect-system']['artifact']['file']
            self.__symbols_defect = calc['defect-system']['symbols']
            self.__potential_energy_defect = uc.value_unit(calc['defect-system']['potential-energy'])

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
        meta['annealtemperature'] = self.annealtemperature
        meta['annealsteps'] = self.annealsteps

        # Extract results
        if self.status == 'finished':            
            meta['dumpfile_base'] = self.dumpfile_base
            meta['dumpfile_defect'] = self.dumpfile_defect
            meta['symbols_base'] = self.symbols_base
            meta['symbols_defect'] = self.symbols_defect
            meta['potential_energy_defect'] = self.potential_energy_defect
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
        
        del input_dict['amin']
        del input_dict['bmin']
        del input_dict['cmin']

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
