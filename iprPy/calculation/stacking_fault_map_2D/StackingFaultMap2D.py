# coding: utf-8

# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union
from copy import deepcopy

import numpy as np

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .stacking_fault_map_2D import stackingfaultmap
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, LammpsMinimize,
                                   StackingFault)

class StackingFaultPath():
    """Class for managing a path along a stacking fault map"""

    def __init__(self, sp: DM):
        self.__direction = sp['direction']
        self.__error = sp.get('error', None)

        if self.__error is None:
            self.__coord = uc.value_unit(sp['minimum-energy-path'])
            self.__usf_mep = uc.value_unit(sp['unstable-fault-energy-mep'])
            self.__usf_urp = uc.value_unit(sp['unstable-fault-energy-unrelaxed-path'])
            self.__shear_mep = uc.value_unit(sp['ideal-shear-stress-mep'])
            self.__shear_urp = uc.value_unit(sp['ideal-shear-stress-unrelaxed-path'])

        else:
            self.__coord = None

            self.__usf_mep = None
            self.__usf_urp = None
            self.__shear_mep = None
            self.__shear_urp = None

    @property
    def direction(self) -> str:
        """str: The direction of slip"""
        return self.__direction

    @property
    def coord(self) -> np.ndarray:
        """numpy.ndarray: Coordinates along the path"""
        return self.__coord

    @property
    def usf_mep(self) -> float:
        """float: The USF energy found along the minimum energy path"""
        return self.__usf_mep

    @property
    def usf_urp(self) -> float:
        """float: The USF energy found along the unrelaxed (ideal) path"""
        return self.__usf_urp

    @property
    def shear_mep(self) -> float:
        """float: The ideal shear stress found along the minimum energy path"""
        return self.__shear_mep

    @property
    def shear_urp(self) -> float:
        """float: The ideal shear stress found along the unrelaxed (ideal) path"""
        return self.__shear_urp

    @property
    def error(self) -> Optional[str]:
        """str or None: Any error that may have been issued during the MEP calculation"""
        return self.__error

    def build_model(self,
                    length_unit: str = 'angstrom',
                    energyperarea_unit: str = 'mJ/m^2',
                    stress_unit: str = 'GPa') -> DM:
        """
        Constructs the model contents associated with the path.

        Parameters
        ----------
        length_unit : str, optional
            The unit of length to use when outputting the path coordinates.
        energyperarea_unit : str, optional
            The unit of energy per area to use when outputting the unstable fault
            energies.
        stress_unit : str, optional
            The unit of stress to use when outputting the ideal shear stresses.
        """
        sp = DM()
        sp['direction'] = self.direction

        if self.error is None:
            sp['minimum-energy-path'] = uc.model(self.coord, length_unit)
            sp['unstable-fault-energy-mep'] = uc.model(self.usf_mep, energyperarea_unit)
            sp['unstable-fault-energy-unrelaxed-path'] = uc.model(self.usf_urp, energyperarea_unit)
            sp['ideal-shear-stress-mep'] = uc.model(self.shear_mep, stress_unit)
            sp['ideal-shear-stress-unrelaxed-path'] = uc.model(self.shear_urp, stress_unit)

        else:
            sp['error'] = self.error

        return sp

class StackingFaultMap2D(Calculation):
    """Class for managing 2D maps of stacking fault energy calculations"""

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
        self.__defect = StackingFault(self)
        subsets = (self.commands, self.potential, self.system,
                   self.minimize, self.defect, self.units)

        # Initialize unique calculation attributes
        self.num_a1 = 10
        self.num_a2 = 10
        self.__gamma = None
        self.__paths = None
        self.__E_isf = None

        # Define calc shortcut
        self.calc = stackingfaultmap

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'stacking_fault_map_2D.py',
            'sfmin.template'
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
    def defect(self) -> StackingFault:
        """StackingFault subset"""
        return self.__defect

    @property
    def num_a1(self) -> int:
        """int: Number of fractional shifts along the a1vect direction to evaluate"""
        return self.__num_a1

    @num_a1.setter
    def num_a1(self, val: int):
        self.__num_a1 = int(val)

    @property
    def num_a2(self) -> int:
        """int: Number of fractional shifts along the a2vect direction to evaluate"""
        return self.__num_a2

    @num_a2.setter
    def num_a2(self, val: int):
        self.__num_a2 = int(val)

    @property
    def gamma(self) -> am.defect.GammaSurface:
        """atomman.defect.GammaSurface: GSF results"""
        if self.__gamma is None:
            raise ValueError('No results yet!')
        if not isinstance(self.__gamma, am.defect.GammaSurface):
            self.__gamma = am.defect.GammaSurface(model=self.__gamma)
        return self.__gamma

    @property
    def paths(self) -> list:
        """list: Any StackingFaultPath results"""
        if self.__paths is None:
            raise ValueError('No path results!')
        return self.__paths

    @property
    def E_isf(self) -> Optional[float]:
        """float or None: Intrinsic stacking fault energy for the plane, if exists and found."""
        return self.__E_isf

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
        num_a1 : int, optional
            The number of shifts to evaluate along the a1 shift vector.
        num_a2 : int, optional
            The number of shifts to evaluate along the a2 shift vector.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'num_a1' in kwargs:
            self.num_a1 = kwargs['num_a1']
        if 'num_a2' in kwargs:
            self.num_a2 = kwargs['num_a2']

    def add_path(self, sp):
        """
        Adds a new path object to the paths list.

        Parameters
        ----------
        sp : DataModelDict
            Dictionary of stacking fault mep results terms
        """
        newpath = StackingFaultPath(sp)
        if self.__paths is None:
            self.__paths = []
        self.paths.append(newpath)

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
        input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
        input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')

        # Load calculation-specific strings

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.num_a1 = int(input_dict.get('stackingfault_num_a1', 10))
        self.num_a2 = int(input_dict.get('stackingfault_num_a2', 10))

        # Load calculation-specific unitless floats

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

            # Set default workflow settings
            params['buildcombos'] = [
                'atomicparent load_file parent',
                'defect stackingfault_file'
            ]
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['defect_record'] = 'stacking_fault'
            params['sizemults'] = '5 5 10'
            params['stackingfault_num_a1'] = '30'
            params['stackingfault_num_a2'] = '30'

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
            'stackingfault_num_a1': ' '.join([
                "The number of fractional shift steps to measure along the a1",
                "shift vector. Default value is 10."]),
            'stackingfault_num_a2': ' '.join([
                "The number of fractional shift steps to measure along the a2",
                "shift vector. Default value is 10."]),
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

            # Defect multikeys
            self.defect.multikeys +

            # Run parameter keys
            [
                [
                    'stackingfault_num_a1',
                    'stackingfault_num_a2',
                ]
            ] +

            # Minimize keys
            [
                self.minimize.keyset
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-stacking-fault-map-2D'

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

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']
        run_params['stackingfault_num_a1'] = self.num_a1
        run_params['stackingfault_num_a2'] = self.num_a2

        # Build results
        if self.status == 'finished':
            energy_per_area_unit = f'{self.units.energy_unit}/{self.units.length_unit}^2'
            gamma_model = self.gamma.model(length_unit=self.units.length_unit,
                                           energyperarea_unit=energy_per_area_unit)
            calc['stacking-fault-map'] = gamma_model['stacking-fault-map']

            if self.E_isf is not None:
                calc['intrinsic-fault-energy'] = uc.model(self.E_isf, 'mJ/m^2')

            try:
                paths = self.paths
            except:
                pass
            else:
                for path in paths:
                    calc.append('slip-path', path.build_model())

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
        self.num_a1 = run_params['stackingfault_num_a1']
        self.nun_a2 = run_params['stackingfault_num_a2']

        # Load results
        if self.status == 'finished':
            self.__gamma = calc

            if 'intrinsic-fault-energy' in calc:
                self.__E_isf = uc.value_unit(calc['intrinsic-fault-energy'])
            if 'slip-path' in calc:
                self.__paths = []
                for sp in calc.iteraslist('slip-path'):
                    self.paths.append(StackingFaultPath(sp))

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'num_a1': load_query(
                style='int_match',
                name='num_a1',
                path=f'{self.modelroot}.calculation.run-parameter.stackingfault_num_a1',
                description='search by number of a1 steps used'),
            'num_a2': load_query(
                style='int_match',
                name='num_a2',
                path=f'{self.modelroot}.calculation.run-parameter.stackingfault_num_a2',
                description='search by number of a2 steps used'),
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
        meta['num_a1'] = self.num_a1
        meta['num_a2'] = self.num_a2

        # Extract results
        if self.status == 'finished':
            if self.E_isf is not None:
                meta['E_isf'] = self.E_isf

            try:
                paths = self.paths
            except:
                pass
            else:
                for path in paths:
                    direction = path.direction

                    if path.error is None:
                        meta[f'E_usf_mep {direction}'] = path.usf_mep
                        meta[f'E_usf_urp {direction}'] = path.usf_urp
                        meta[f'τ_ideal_mep {direction}'] = path.shear_mep
                        meta[f'τ_ideal_urp {direction}'] = path.shear_urp
                    else:
                        meta[f'error {direction}'] = path.error

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

            'stackingfault_key',

            'num_a1',
            'num_a2'
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

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

        # Add calculation-specific inputs
        input_dict['num_a1'] = self.num_a1
        input_dict['num_a2'] = self.num_a2

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
        self.__gamma = results_dict['gamma']
