# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from copy import deepcopy
from typing import Optional, Union

import numpy as np
import numpy.typing as npt

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .diatom_scan import diatom_scan
from ...calculation_subset import LammpsCommands, LammpsPotential, Units
from ...input import value
from ...tools import aslist, dict_insert

class DiatomScan(Calculation):
    """Class for managing diatom energy scan calculations"""

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
        subsets = (self.commands, self.potential, self.units)

        # Initialize unique calculation attributes
        self.symbols = []
        self.number_of_steps_r = 300
        self.minimum_r = uc.set_in_units(0.02, 'angstrom')
        self.maximum_r = uc.set_in_units(6.0, 'angstrom')
        self.r_values = None
        self.energy_values = None

        # Define calc shortcut
        self.calc = diatom_scan

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'diatom_scan.py',
            'run0.template'
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
    def symbols(self) -> list:
        """list : The potential symbols to use"""
        return self.__symbols

    @symbols.setter
    def symbols(self, val: Union[str, list, None]):
        if val is None:
            self.__symbols = []
        else:
            val = [str(v) for v in aslist(val)]
            # Replicate single symbol
            if len(val) == 1:
                val += val

            # Check that at most 2 symbols given for calc
            elif len(val) > 2:
                raise ValueError('Invalid number of symbols')

            self.__symbols = val

    @property
    def number_of_steps_r(self) -> int:
        """int : The number of r evaluation steps"""
        return self.__number_of_steps_r

    @number_of_steps_r.setter
    def number_of_steps_r(self, val: int):
        val = int(val)
        assert val > 0
        self.__number_of_steps_r = val

    @property
    def minimum_r(self) -> float:
        """float : The minimum value of r"""
        return self.__minimum_r

    @minimum_r.setter
    def minimum_r(self, val: float):
        val = float(val)
        assert val > 0
        self.__minimum_r = val

    @property
    def maximum_r(self) -> float:
        """float : The maximum value of r"""
        return self.__maximum_r

    @maximum_r.setter
    def maximum_r(self, val: float):
        val = float(val)
        assert val > 0
        self.__maximum_r = val

    @property
    def r_values(self) -> np.ndarray:
        """numpy.NDArray : Interatomic distances used for the scan."""
        if self.__r_values is None:
            raise ValueError('No results yet!')
        return self.__r_values

    @r_values.setter
    def r_values(self, val: Optional[npt.ArrayLike]):
        if val is None:
            self.__r_values = val
        else:
            val = np.asarray(val, dtype=float)
            self.__r_values = val
            self.number_of_steps_r = len(val)
            self.minimum_r = val[0]
            self.maximum_r = val[-1]

    @property
    def energy_values(self) -> np.ndarray:
        """numpy.NDArray : Measured potential energy for each r value."""
        if self.__energy_values is None:
            raise ValueError('No results yet!')
        return self.__energy_values

    @energy_values.setter
    def energy_values(self, val: Optional[npt.ArrayLike]):
        if val is None:
            self.__energy_values = val
        else:
            val = np.asarray(val, dtype=float)
            self.__energy_values = val

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
        symbols : str or list, optional
            One or two model symbols to assign to the atoms.
        number_of_steps_r : int, optional
            The number of evaluation steps to use for the r spacing.
        minimum_r : float, optional
            The minimum r spacing value to evaluate.
        maximum_r : float, optional
            The maximum r spacing value to evaluate.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'symbols' in kwargs:
            self.symbols = kwargs['symbols']
        if 'number_of_steps_r' in kwargs:
            self.number_of_steps_r = kwargs['number_of_steps_r']
        if 'minimum_r' in kwargs:
            self.minimum_r = kwargs['minimum_r']
        if 'maximum_r' in kwargs:
            self.maximum_r = kwargs['maximum_r']

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

        # Load calculation-specific strings
        self.symbols = input_dict['symbols'].split()

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.number_of_steps_r = int(input_dict.get('number_of_steps_r', 300))

        # Load calculation-specific unitless floats

        # Load calculation-specific floats with units
        self.minimum_r = value(input_dict, 'minimum_r',
                               default_unit=self.units.length_unit,
                               default_term='0.02 angstrom')
        self.maximum_r = value(input_dict, 'maximum_r',
                               default_unit=self.units.length_unit,
                               default_term='6.0 angstrom')

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

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
            params['buildcombos'] = 'diatom potential_file intpot'
            params['minimum_r'] = '0.02 angstrom'
            params['maximum_r'] = '10.0 angstrom'
            params['number_of_steps_r'] = '500'

            # Copy kwargs to params
            for key in kwargs:

                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'intpot_{key}'] = kwargs[key]

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
            'symbols': ' '.join([
                "The one or two model symbols to perform the scan for."]),
            'minimum_r': ' '.join([
                "The minimum interatomic spacing, r, for the scan.  Default",
                "value is '0.02 angstrom'."]),
            'maximum_r': ' '.join([
                "The maximum interatomic spacing, r, for the scan.  Default"
                "value is '6.0 angstrom'."]),
            'number_of_steps_r': ' '.join([
                "The number of interatomic spacing values, r, to use.  Default"
                "value is 300."]),
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

            # Potential keys plus symbols
            [
                self.potential.keyset + 
                [
                    'symbols'
                ]
            ] +

            # Run parameter keys
            [
                [
                    'minimum_r',
                    'maximum_r',
                    'number_of_steps_r',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-diatom-scan'

    def build_model(self) -> DM:
        """
        Generates and returns model content based on the values set to object.
        """
        if len(self.symbols) is None:
            raise ValueError('symbols not set')

        # Build universal content
        model = super().build_model()
        calc = model[self.modelroot]

        # Build subset content
        self.commands.build_model(calc, after='atomman-version')
        self.potential.build_model(calc, after='calculation')

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        calc['calculation']['run-parameter'] = run_params = DM()
        run_params['minimum_r'] = uc.model(self.minimum_r,
                                           self.units.length_unit)
        run_params['maximum_r'] = uc.model(self.maximum_r,
                                           self.units.length_unit)
        run_params['number_of_steps_r'] = self.number_of_steps_r

        dict_insert(calc, 'system-info', DM(), after='potential-LAMMPS')
        calc['system-info']['symbol'] = self.symbols

        # Build results
        if self.status == 'finished':
            calc['diatom-energy-relation'] = scan = DM()
            scan['r'] = uc.model(self.r_values, self.units.length_unit)
            scan['potential-energy'] = uc.model(self.energy_values,
                                                self.units.energy_unit)

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
        self.minimum_r = uc.value_unit(run_params['minimum_r'])
        self.maximum_r = uc.value_unit(run_params['maximum_r'])
        self.number_of_steps_r = run_params['number_of_steps_r']

        self.symbols = calc['system-info']['symbol']

        # Load results
        if self.status == 'finished':
            scan = calc['diatom-energy-relation']
            self.r_values = uc.value_unit(scan['r'])
            self.energy_values = uc.value_unit(scan['potential-energy'])

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'minimum_r': load_query(
                style='float_match',
                name='minimum_r',
                path=f'{self.modelroot}.calculation.run-parameter.minimum_r.value',
                description='search by the minimum r value used in angstroms',
                unit='angstrom'),
            'maximum_r': load_query(
                style='float_match',
                name='maximum_r',
                path=f'{self.modelroot}.calculation.run-parameter.maximum_r.value',
                description='search by the maximum r value used in Angstroms',
                unit='angstrom'),
            'number_of_steps_r': load_query(
                style='int_match',
                name='number_of_steps_r',
                path=f'{self.modelroot}.calculation.run-parameter.number_of_steps_r',
                description='search by the number of r steps used'),
            'symbol': load_query(
                style='list_contains',
                name='symbols',
                path=f'{self.modelroot}.system-info.symbols',
                description='search by element symbols used'),
        })
        return queries

########################## Metadata interactions ##############################

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        # Check required parameters
        if len(self.symbols) is None:
            raise ValueError('symbols not set')

        # Call super to extract universal and subset content
        meta = super().metadata()

        # Extract calculation-specific content
        meta['minimum_r'] = self.minimum_r
        meta['maximum_r'] = self.maximum_r
        meta['number_of_steps_r'] = self.number_of_steps_r
        meta['symbols'] = ' '.join(sorted(self.symbols))

        # Extract results
        if self.status == 'finished':
            meta['r_values'] = self.r_values.tolist()
            meta['energy_values'] = self.energy_values.tolist()

        return meta

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',
            'symbols',
            'potential_LAMMPS_key',
            'potential_key',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

########################### Calculation interactions ##########################

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""

        # Check required parameters
        if len(self.symbols) is None:
            raise ValueError('symbols not set')

        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Add calculation-specific inputs
        input_dict['symbols'] = self.symbols
        input_dict['rmin'] = self.minimum_r
        input_dict['rmax'] = self.maximum_r
        input_dict['rsteps'] = self.number_of_steps_r

        # Return input_dict
        return input_dict

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'diatom.dat',
            'log.lammps',
            'run0.in'
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
        self.r_values = results_dict['r_values']
        self.energy_values = results_dict['energy_values']
