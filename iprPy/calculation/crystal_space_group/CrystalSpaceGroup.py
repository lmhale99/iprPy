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
from .crystal_space_group import crystal_space_group
from ...calculation_subset import Units, AtommanSystemLoad
from ...input import value, boolean

class CrystalSpaceGroup(Calculation):
    """Class for managing space group analysis of crystals"""

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, Path, IOBase, DM, None]=None,
                 name: Optional[str]=None,
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
        params : str, file-like object or dict, optional
            Calculation input parameters or input parameter file.  Cannot be
            given with model.
        **kwargs : any
            Any other core Calculation record attributes to set.  Cannot be
            given with model.
        """
        # Initialize subsets used by the calculation
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        subsets = (self.system, self.units)

        # Initialize unique calculation attributes
        self.primitivecell = False
        self.idealcell = True
        self.symmetryprecision = uc.set_in_units(0.01, 'angstrom')
        self.__pearson = None
        self.__number = None
        self.__international = None
        self.__schoenflies = None
        self.__wyckoffs = None
        self.__wyckoff_fingerprint = None
        self.__spg_ucell = None

        # Define calc shortcut
        self.calc = crystal_space_group

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'crystal_space_group.py'
        ]

############################## Class attributes ###############################

    @property
    def units(self) -> Units:
        """Units subset"""
        return self.__units

    @property
    def system(self) -> AtommanSystemLoad:
        """AtommanSystemLoad subset"""
        return self.__system

    @property
    def primitivecell(self) -> bool:
        """bool : Indicates if spg_ucell is conventional (False) or primitive (True)."""
        return self.__primitivecell

    @primitivecell.setter
    def primitivecell(self, val: bool):
        self.__primitivecell = boolean(val)

    @property
    def idealcell(self) -> bool:
        """bool : Indicates if spg_ucell atoms are averaged (False) or idealized (True)."""
        return self.__idealcell

    @idealcell.setter
    def idealcell(self, val: bool):
        self.__idealcell = boolean(val)

    @property
    def symmetryprecision(self) -> float:
        """
        float : Length tolerance used in identifying symmetry of atomic sites
        and system dimensions
        """
        return self.__symmetryprecision

    @symmetryprecision.setter
    def symmetryprecision(self, val: float):
        self.__symmetryprecision = float(val)

    @property
    def pearson(self) -> str:
        """str: Pearson symbol."""
        if self.__pearson is None:
            raise ValueError('No results yet!')
        return self.__pearson

    @property
    def number(self) -> int:
        """int: Space group number."""
        if self.__number is None:
            raise ValueError('No results yet!')
        return self.__number

    @property
    def international(self) -> str:
        """str: Space group International symbol."""
        if self.__international is None:
            raise ValueError('No results yet!')
        return self.__international

    @property
    def schoenflies(self) -> str:
        """str: Space group Schoenflies symbol."""
        if self.__schoenflies is None:
            raise ValueError('No results yet!')
        return self.__schoenflies

    @property
    def wyckoffs(self) -> list:
        """list: Wykoff site letter for each atom."""
        if self.__wyckoffs is None:
            raise ValueError('No results yet!')
        return self.__wyckoffs

    @property
    def wyckoff_fingerprint(self) -> str:
        """str: Combines all Wyckoff letters."""
        if self.__wyckoff_fingerprint is None:
            raise ValueError('No results yet!')
        return self.__wyckoff_fingerprint

    @property
    def spg_ucell(self) -> am.System:
        """atomman.System: The unit cell identified following the space-group analysis"""
        if self.__spg_ucell is None:
            raise ValueError('No results yet!')
        if not isinstance(self.__spg_ucell, am.System):
            self.__spg_ucell = am.load('system_model', self.__spg_ucell)
        return self.__spg_ucell

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
        primitivecell : bool, optional
            Indicates if spg_ucell is conventional (False) or primitive (True).
        idealcell : bool, optional
            Indicates if spg_ucell atoms are averaged (False) or idealized
            (True).
        symmetryprecision : float, optional
            Length tolerance used in identifying symmetry of atomic sites and
            system dimensions.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'primitivecell' in kwargs:
            self.primitivecell = kwargs['primitivecell']
        if 'idealcell' in kwargs:
            self.idealcell = kwargs['idealcell']
        if 'symmetryprecision' in kwargs:
            self.symmetryprecision = kwargs['symmetryprecision']

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
        self.primitivecell = boolean(input_dict.get('primitivecell', False))
        self.idealcell = boolean(input_dict.get('idealcell', True))

        # Load calculation-specific integers

        # Load calculation-specific unitless floats

        # Load calculation-specific floats with units
        self.symmetryprecision = value(input_dict, 'symmetryprecision',
                                       default_unit=self.units.length_unit,
                                       default_term='0.01 angstrom')

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

        # main branch
        if branch == 'main':
            raise ValueError('No main branch: use relax, prototype or reference')

        elif branch == 'relax':

            # Check for required kwargs

            # Set default workflow settings
            params['buildcombos'] = [
                'atomicarchive load_file archive1',
                'atomicarchive load_file archive2'
            ]
            params['archive1_record'] = 'calculation_relax_static'
            params['archive1_load_key'] = 'final-system'
            params['archive1_status'] = 'finished'
            params['archive2_record'] = 'calculation_relax_box'
            params['archive2_load_key'] = 'final-system'
            params['archive2_status'] = 'finished'

            # Copy kwargs to params
            for key in kwargs:

                # Rename potential-related terms for buildcombos
                if key == 'potential_id':
                    params['archive1_potential_LAMMPS_id'] = kwargs[key]
                    params['archive2_potential_LAMMPS_id'] = kwargs[key]
                elif key == 'potential_key':
                    params['archive1_potential_LAMMPS_key'] = kwargs[key]
                    params['archive2_potential_LAMMPS_key'] = kwargs[key]
                elif key == 'potential_pot_id':
                    params['archive1_potential_id'] = kwargs[key]
                    params['archive2_potential_id'] = kwargs[key]
                elif key == 'potential_pot_key':
                    params['archive1_potential_key'] = kwargs[key]
                    params['archive2_potential_key'] = kwargs[key]


                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        elif branch == 'prototype':

            # Check for required kwargs

            # Set default workflow settings
            params['buildcombos'] = 'crystalprototype load_file proto'

            # Copy kwargs to params
            for key in kwargs:
                params[key] = kwargs[key]

        elif branch == 'reference':

            # Check for required kwargs

            # Set default workflow settings
            params['buildcombos'] = 'atomicreference load_file ref'

            # Copy kwargs to params
            for key in kwargs:
                params[key] = kwargs[key]

        else:
            raise ValueError(f'Unknown branch {branch}')

        return params

    @property
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'symmetryprecision': ' '.join([
                "The precision tolerance used for the atomic positions and box",
                "dimensions for determining symmetry elements.  Default value is",
                "'0.01 angstrom'."]),
            'primitivecell': ' '.join([
                "A boolean flag indicating if the returned unit cell is to be",
                "primitive (True) or conventional (False).  Default value is False."]),
            'idealcell': ' '.join([
                "A boolean flag indicating if the box dimensions and atomic positions",
                "are to be idealized based on the space group (True) or averaged based",
                "on their actual values (False).  Default value is True."]),
        }

    @property
    def singularkeys(self) -> list:
        """list: Calculation keys that can have single values during prepare."""

        keys = (
            # Universal keys
            super().singularkeys

            # Subset keys
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

            # System keys
            [
                self.system.keyset
            ] +

            # Run parameter keys
            [
                [
                    'symmetryprecision',
                    'primitivecell',
                    'idealcell',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-crystal-space-group'

    def build_model(self) -> DM:
        """
        Generates and returns model content based on the values set to object.
        """
        # Build universal content
        model = super().build_model()
        calc = model[self.modelroot]

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']
        run_params['symmetryprecision'] = self.symmetryprecision
        run_params['primitivecell'] = self.primitivecell
        run_params['idealcell'] = self.idealcell

        # Build subset content
        self.system.build_model(calc, after='calculation')

        # Build results
        if self.status == 'finished':
            calc['Pearson-symbol'] = self.pearson
            calc['space-group'] = DM()
            calc['space-group']['number'] = self.number
            calc['space-group']['Hermann-Maguin'] = self.international
            calc['space-group']['Schoenflies'] = self.schoenflies

            wykoffletters, wykoffmults = np.unique(self.wyckoffs, return_counts=True)
            for letter, mult in zip(wykoffletters, wykoffmults):
                wykoff = DM()
                wykoff['letter'] = letter
                wykoff['multiplicity'] = int(mult)
                calc['space-group'].append('Wykoff', wykoff)
            calc['space-group']['Wyckoff-fingerprint'] = self.wyckoff_fingerprint

            system_model = self.spg_ucell.dump('system_model', box_unit=self.units.length_unit)
            calc['unit-cell-atomic-system'] = system_model['atomic-system']

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
        self.symmetryprecision = run_params['symmetryprecision']
        self.primitivecell = run_params['primitivecell']
        self.idealcell = run_params['idealcell']

        # Load results
        if self.status == 'finished':
            self.__pearson = calc['Pearson-symbol']
            self.__number = calc['space-group']['number']
            self.__international = calc['space-group']['Hermann-Maguin']
            self.__schoenflies = calc['space-group']['Schoenflies']
            self.__wyckoffs = []
            for wyckoff in calc['space-group'].aslist('Wykoff'):
                self.__wyckoffs.extend([wyckoff['letter']] * wyckoff['multiplicity'])
            self.__wyckoff_fingerprint = calc['space-group']['Wyckoff-fingerprint']

            self.__spg_ucell = DM([('atomic-system', calc['unit-cell-atomic-system'])])

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        queries = deepcopy(super().queries)
        queries.update({
            'symmetryprecision': load_query(
                style='float_match',
                name='symmetryprecision',
                path=f'{self.modelroot}.calculation.run-parameter.symmetryprecision',
                description='search by the symmetry precision tolerance used'),
            'idealcell': load_query(
                style='str_match',
                name='idealcell',
                path=f'{self.modelroot}.calculation.run-parameter.idealcell',
                description='search by the ideal cell setting'),
            'primitivecell': load_query(
                style='str_match',
                name='primitivecell',
                path=f'{self.modelroot}.calculation.run-parameter.primitivecell',
                description='search by the primitive cell setting'),
            'pearson': load_query(
                style='str_match',
                name='pearson',
                path=f'{self.modelroot}.Pearson-symbol',
                description='search by the Pearson symbol'),
            'number': load_query(
                style='int_match',
                name='number',
                path=f'{self.modelroot}.space-group.number',
                description='search by the space group number'),
            'international': load_query(
                style='str_match',
                name='international',
                path=f'{self.modelroot}.space-group.Hermann-Maguin',
                description='search by the space group international Hermann-Maguin symbol'),
            'schoenflies': load_query(
                style='str_contains',
                name='schoenflies',
                path=f'{self.modelroot}.space-group.Schoenflies',
                description='search by the space group Schoenflies symbol'),
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
        meta['symmetryprecision'] = self.symmetryprecision
        meta['idealcell'] = self.idealcell
        meta['primitivecell'] = self.primitivecell

        # Extract results
        if self.status == 'finished':
            meta['pearson_symbol'] = self.pearson
            meta['spacegroup_number'] = self.number
            meta['spacegroup_international'] = self.international
            meta['spacegroup_Schoenflies'] = self.schoenflies
            meta['wykoff_fingerprint'] = self.wyckoff_fingerprint
            meta['composition'] = self.spg_ucell.composition
            meta['a'] = self.spg_ucell.box.a
            meta['b'] = self.spg_ucell.box.b
            meta['c'] = self.spg_ucell.box.c
            meta['alpha'] = self.spg_ucell.box.alpha
            meta['beta'] = self.spg_ucell.box.beta
            meta['gamma'] = self.spg_ucell.box.gamma
            meta['natoms'] = self.spg_ucell.natoms

        return meta

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',

            'parent_key',
            'load_options',

            'primitivecell',
            'idealcell',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'symmetryprecision':1e-5,
        }

########################### Calculation interactions ##########################

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""

        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Modify subset inputs
        input_dict['system'] = input_dict.pop('ucell')

        # Add calculation-specific inputs
        input_dict['symprec'] = self.symmetryprecision
        input_dict['to_primitive'] = self.primitivecell
        input_dict['no_idealize'] = not self.idealcell

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
        self.__pearson = results_dict['pearson']
        self.__number = results_dict['number']
        self.__international = results_dict['international']
        self.__schoenflies = results_dict['schoenflies']
        self.__wyckoffs = results_dict['wyckoffs']
        self.__wyckoff_fingerprint = results_dict['wyckoff_fingerprint']
        self.__spg_ucell = results_dict['ucell']
