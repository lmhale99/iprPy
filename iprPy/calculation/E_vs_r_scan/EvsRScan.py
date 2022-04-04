# coding: utf-8
# Standard Python libraries
import uuid
from copy import deepcopy

import numpy as np

from yabadaba import query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .e_vs_r_scan import e_vs_r_scan
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

class EvsRScan(Calculation):
    """Class for managing energy versus r volumetric scans for crystals"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""

        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        self.__system_mods = AtommanSystemManipulate(self)
        subsets = (self.commands, self.potential, self.system,
                   self.system_mods, self.units)

        # Initialize unique calculation attributes
        self.number_of_steps_r = 201
        self.minimum_r = uc.set_in_units(2.0, 'angstrom')
        self.maximum_r = uc.set_in_units(6.0, 'angstrom')
        self.r_values = None
        self.a_values = None
        self.energy_values = None
        self.min_cells = None

        # Define calc shortcut
        self.calc = e_vs_r_scan

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self):
        """list: the names of each file used by the calculation."""
        return [
            'e_vs_r_scan.py',
            'run0.template'
        ]

############################## Class attributes ###############################

    @property
    def commands(self):
        """LammpsCommands subset"""
        return self.__commands

    @property
    def potential(self):
        """LammpsPotential subset"""
        return self.__potential

    @property
    def units(self):
        """Units subset"""
        return self.__units

    @property
    def system(self):
        """AtommanSystemLoad subset"""
        return self.__system

    @property
    def system_mods(self):
        """AtommanSystemManipulate subset"""
        return self.__system_mods

    @property
    def number_of_steps_r(self):
        return self.__number_of_steps_r

    @number_of_steps_r.setter
    def number_of_steps_r(self, value):
        value = int(value)
        assert value > 0
        self.__number_of_steps_r = value

    @property
    def minimum_r(self):
        return self.__minimum_r

    @minimum_r.setter
    def minimum_r(self, value):
        value = float(value)
        assert value > 0
        self.__minimum_r = value

    @property
    def maximum_r(self):
        return self.__maximum_r

    @maximum_r.setter
    def maximum_r(self, value):
        value = float(value)
        assert value > 0
        self.__maximum_r = value

    @property
    def r_values(self):
        """numpy.NDArray : Interatomic distances used for the scan."""
        if self.__r_values is None:
            raise ValueError('No results yet!')
        return self.__r_values

    @r_values.setter
    def r_values(self, value):
        if value is None:
            self.__r_values = value
        else:
            value = np.asarray(value, dtype=float)
            self.__r_values = value
            self.number_of_steps_r = len(value)
            self.minimum_r = value[0]
            self.maximum_r = value[-1]

    @property
    def a_values(self):
        """numpy.NDArray : Unit cell a lattice parameters associated with the scan."""
        if self.__a_values is None:
            raise ValueError('No results yet!')
        return self.__a_values

    @a_values.setter
    def a_values(self, value):
        if value is None:
            self.__a_values = value
        else:
            value = np.asarray(value, dtype=float)
            self.__a_values = value

    @property
    def energy_values(self):
        """numpy.NDArray : Measured potential energy for each r value."""
        if self.__energy_values is None:
            raise ValueError('No results yet!')
        return self.__energy_values

    @energy_values.setter
    def energy_values(self, value):
        if value is None:
            self.__energy_values = value
        else:
            value = np.asarray(value, dtype=float)
            self.__energy_values = value

    @property
    def min_cells(self):
        """list : atomman.Systems for the dimensions scanned with local energy minima."""
        if self.__min_cells is None:
            raise ValueError('No results yet!')
        for i in range(len(self.__min_cells)):
            if not isinstance(self.__min_cells[i], am.System):
                self.__min_cells[i] = am.load('system_model', self.__min_cells[i])
        return self.__min_cells

    @min_cells.setter
    def min_cells(self, value):
        if value is None:
            self.__min_cells = value
        else:
            self.__min_cells = aslist(value)

    def set_values(self, name=None, **kwargs):
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameters
        ----------
        name : str, optional
            The name to assign to the calculation.  By default, this is set as
            the calculation's key.
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
        if 'number_of_steps_r' in kwargs:
            self.number_of_steps_r = kwargs['number_of_steps_r']
        if 'minimum_r' in kwargs:
            self.minimum_r = kwargs['minimum_r']
        if 'maximum_r' in kwargs:
            self.maximum_r = kwargs['maximum_r']

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Load universal content
        input_dict = super().load_parameters(params, key=key)

        # Load input/output units
        self.units.load_parameters(input_dict)

        # Load calculation-specific booleans
        
        # Load calculation-specific integers
        self.number_of_steps_r = int(input_dict.get('number_of_steps_r', 201))

        # Load calculation-specific unitless floats
        
        # Load calculation-specific floats with units
        self.minimum_r = value(input_dict, 'minimum_r',
                               default_unit=self.units.length_unit,
                               default_term='2.0 angstrom')
        self.maximum_r = value(input_dict, 'maximum_r',
                               default_unit=self.units.length_unit,
                               default_term='6.0 angstrom')
        
        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)
        
        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Manipulate system
        self.system_mods.load_parameters(input_dict)

    def master_prepare_inputs(self, branch='main', **kwargs):
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
            params['buildcombos'] = 'crystalprototype load_file prototype'
            params['sizemults'] = '10 10 10'
            params['minimum_r'] = '0.5 angstrom'
            params['maximum_r'] = '6.0 angstrom'
            params['number_of_steps_r'] = '276'

            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'prototype_{key}'] = kwargs[key]
                
                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]
        
        elif branch == 'bop':
            
            # Check for required kwargs
            assert 'lammps_command' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'crystalprototype load_file prototype'
            params['prototype_potential_pair_style'] = 'bop'
            params['sizemults'] = '10 10 10'
            params['minimum_r'] = '2.0 angstrom'
            params['maximum_r'] = '6.0 angstrom'
            params['number_of_steps_r'] = '201'

            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    if key != 'potential_pair_style':
                        params[f'prototype_{key}'] = kwargs[key]
                
                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        else:
            raise ValueError(f'Unknown branch {branch}')

        return params

    @property
    def templatekeys(self):
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'minimum_r': ' '.join([
                "The minimum interatomic spacing, r, for the scan.  Default",
                "value is '2.0 angstrom'."]),
            'maximum_r': ' '.join([
                "The maximum interatomic spacing, r, for the scan.  Default"
                "value is '6.0 angstrom'."]),
            'number_of_steps_r': ' '.join([
                "The number of interatomic spacing values, r, to use.  Default"
                "value is 201."]),
        } 

    @property
    def singularkeys(self):
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
    def multikeys(self):
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
                    'minimum_r',
                    'maximum_r',
                    'number_of_steps_r',
                ]
            ]
        )   
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'calculation-E-vs-r-scan'

    def build_model(self):
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
        run_params['minimum_r'] = uc.model(self.minimum_r,
                                           self.units.length_unit)
        run_params['maximum_r'] = uc.model(self.maximum_r,
                                           self.units.length_unit)
        run_params['number_of_steps_r'] = self.number_of_steps_r

        # Build results
        if self.status == 'finished':
            calc['cohesive-energy-relation'] = scan = DM()
            scan['r'] = uc.model(self.r_values, self.units.length_unit)
            scan['a'] = uc.model(self.a_values, self.units.length_unit)
            scan['cohesive-energy'] = uc.model(self.energy_values,
                                                self.units.energy_unit)

            for cell in self.min_cells:
               system_model = cell.dump('system_model', box_unit=self.units.length_unit)
               calc.append('minimum-atomic-system', system_model['atomic-system'])

        self._set_model(model)
        return model

    def load_model(self, model, name=None):
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

        # Load results
        if self.status == 'finished':
            scan = calc['cohesive-energy-relation']
            self.r_values = uc.value_unit(scan['r'])
            self.a_values = uc.value_unit(scan['a'])
            self.energy_values = uc.value_unit(scan['cohesive-energy'])

            self.min_cells = []
            for cell in calc.aslist('minimum-atomic-system'):
               self.min_cells.append(DM([('atomic-system', cell)]))

    def mongoquery(self, minimum_r=None, maximum_r=None,
                   number_of_steps_r=None, **kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.

        Parameters
        ----------
        minimum_r : float or list, optional
            The minimum_r run parameter value(s) to parse by.
        maximum_r : float or list, optional
            The maximum_r run parameter value(s) to parse by.
        number_of_steps_r : int or list, optional
            The number_of_steps_r run parameter value(s) to parse by.
        **kwargs : any
            Any extra query terms that are universal for all calculations
            or associated with one of the calculation's subsets.        
        
        Returns
        -------
        dict
            The Mongo-style query.
        """
        # Call super to build universal and subset terms
        mquery = super().mongoquery(**kwargs)

        # Build calculation-specific terms
        root = f'content.{self.modelroot}'
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.minimum_r', minimum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maximum_r', maximum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_r', number_of_steps_r)

        return mquery

    @staticmethod
    def cdcsquery(self, minimum_r=None, maximum_r=None,
                  number_of_steps_r=None, **kwargs):
        """
        Builds a CDCS-style query based on kwargs values for the record style.

        Parameters
        ----------
        minimum_r : float or list, optional
            The minimum_r run parameter value(s) to parse by.
        maximum_r : float or list, optional
            The maximum_r run parameter value(s) to parse by.
        number_of_steps_r : int or list, optional
            The number_of_steps_r run parameter value(s) to parse by.
        **kwargs : any
            Any extra query terms that are universal for all calculations
            or associated with one of the calculation's subsets.        
        
        Returns
        -------
        dict
            The CDCS-style query.
        """
        # Call super to build universal and subset terms
        mquery = super().cdcsquery(**kwargs)

        # Build calculation-specific terms
        root = self.modelroot
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.minimum_r', minimum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maximum_r', maximum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_r', number_of_steps_r)

        return mquery

########################## Metadata interactions ##############################

    def metadata(self):
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        # Call super to extract universal and subset content
        meta = super().metadata()

        # Extract calculation-specific content
        meta['minimum_r'] = self.minimum_r
        meta['maximum_r'] = self.maximum_r
        meta['number_of_steps_r'] = self.number_of_steps_r
        
        # Extract results
        if self.status == 'finished':
            meta['r_values'] = self.r_values.tolist()
            meta['a_values'] = self.a_values.tolist()
            meta['energy_values'] = self.energy_values.tolist()

        return meta

    @property
    def compare_terms(self):
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
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

    def pandasfilter(self, dataframe, minimum_r=None, maximum_r=None,
                     number_of_steps_r=None, **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
        minimum_r : float or list, optional
            The minimum_r run parameter value(s) to parse by.
        maximum_r : float or list, optional
            The maximum_r run parameter value(s) to parse by.
        number_of_steps_r : int or list, optional
            The number_of_steps_r run parameter value(s) to parse by.
        kwargs : any
            Any extra query terms that are universal for all calculations
            or associated with one of the calculation's subsets. 

        Returns
        -------
        pandas.Series of bool
            True for each entry where all filter terms+values match, False for
            all other entries.
        """
        # Call super to filter by universal and subset terms
        matches = super().pandasfilter(dataframe, **kwargs)

        # Filter by calculation-specific terms
        matches = (matches
            &query.str_match.pandas(dataframe, 'minimum_r', minimum_r)
            &query.str_match.pandas(dataframe, 'maximum_r', maximum_r)
            &query.str_match.pandas(dataframe, 'number_of_steps_r', number_of_steps_r)
        )
        
        return matches

########################### Calculation interactions ##########################

    def calc_inputs(self):
        """Builds calculation inputs from the class's attributes"""
        
        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)
        
        # Remove unused subset inputs
        del input_dict['transform']

        # Add calculation-specific inputs
        input_dict['rmin'] = self.minimum_r
        input_dict['rmax'] = self.maximum_r
        input_dict['rsteps'] = self.number_of_steps_r

        # Return input_dict
        return input_dict
    
    def process_results(self, results_dict):
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
        self.r_values = results_dict['r_values']
        self.a_values = results_dict['a_values']
        self.energy_values = results_dict['Ecoh_values']
        self.min_cells = results_dict['min_cell']
        