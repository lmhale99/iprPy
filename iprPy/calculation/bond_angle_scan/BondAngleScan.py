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
from .bond_angle_scan import bond_angle_scan
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

class BondAngleScan(Calculation):
    """Class for managing 3-body (bond angle) energy scan calculations"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""
        
        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        subsets = (self.commands, self.potential, self.units)

        # Initialize unique calculation attributes
        self.symbols = []
        self.number_of_steps_r = 100
        self.minimum_r = uc.set_in_units(0.5, 'angstrom')
        self.maximum_r = uc.set_in_units(6.0, 'angstrom')
        self.number_of_steps_theta = 100
        self.minimum_theta = 1.0
        self.maximum_theta = 180.0
        
        self.cluster = None
        self.results_file = None
        self.results_length_unit = None
        self.results_energy_unit = None

        # Define calc shortcut
        self.calc = bond_angle_scan

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self):
        """list: the names of each file used by the calculation."""
        return [
            'bond_angle_scan.py',
            'bond_scan.template'
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
    def symbols(self):
        """The potential symbols to use"""
        return self.__symbols

    @symbols.setter
    def symbols(self, value):
        if value is None:
            self.__symbols = []
        else:
            value = aslist(value)
            # Replicate single symbol
            if len(value) == 1:
                value += value
            
            # Check that at most 2 symbols given for calc
            elif len(value) > 2:
                raise ValueError('Invalid number of symbols')
            
            self.__symbols = value

    @property
    def number_of_steps_r(self):
        """int : The number of r evaluation steps"""
        return self.__number_of_steps_r

    @number_of_steps_r.setter
    def number_of_steps_r(self, value):
        value = int(value)
        assert value > 0
        self.__number_of_steps_r = value

    @property
    def minimum_r(self):
        """float : The minimum value of r"""
        return self.__minimum_r

    @minimum_r.setter
    def minimum_r(self, value):
        value = float(value)
        assert value > 0
        self.__minimum_r = value

    @property
    def maximum_r(self):
        """float : The maximum value of r"""
        return self.__maximum_r

    @maximum_r.setter
    def maximum_r(self, value):
        value = float(value)
        assert value > 0
        self.__maximum_r = value

    @property
    def number_of_steps_theta(self):
        """int : The number of theta evaluation steps"""
        return self.__number_of_steps_theta

    @number_of_steps_theta.setter
    def number_of_steps_theta(self, value):
        value = int(value)
        assert value > 0
        self.__number_of_steps_theta = value

    @property
    def minimum_theta(self):
        """float : The minimum value of theta"""
        return self.__minimum_theta

    @minimum_theta.setter
    def minimum_theta(self, value):
        value = float(value)
        assert value > 0
        assert value <= 180.0
        self.__minimum_theta = value

    @property
    def maximum_theta(self):
        """float : The maximum value of theta"""
        return self.__maximum_theta

    @maximum_theta.setter
    def maximum_theta(self, value):
        value = float(value)
        assert value > 0
        assert value <= 180.0
        self.__maximum_theta = value

    @property
    def cluster(self):
        """atomman.cluster.BondAngleMap : Measured energies and coordinates"""
        if self.__cluster is None:
            raise ValueError('No results yet!')
        return self.__cluster

    @cluster.setter
    def cluster(self, value):
        if value is None:
            self.__cluster = value
        elif isinstance(value, am.cluster.BondAngleMap):
            self.__cluster = value
        else:
            raise TypeError('Must be a cluster object')
        
    @property
    def results_file(self):
        """str : File name where the raw results are saved."""
        if self.__results_file is None:
            raise ValueError('No results yet!')

    @results_file.setter
    def results_file(self, value):
        self.__results_file = value

    @property
    def results_length_unit(self):
        """str : Unit of length for the results_file."""
        if self.__results_length_unit is None:
            raise ValueError('No results yet!')

    @results_length_unit.setter
    def results_length_unit(self, value):
        self.__results_length_unit = value

    @property
    def results_energy_unit(self):
        """str : Unit of energy for the results_file."""
        if self.__results_energy_unit is None:
            raise ValueError('No results yet!')

    @results_energy_unit.setter
    def results_energy_unit(self, value):
        self.__results_energy_unit = value

    def set_values(self, name=None, **kwargs):
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
        number_of_steps_theta : int, optional
            The number of evaluation steps to use for the theta angles.
        minimum_theta : float, optional
            The minimum theta angle value to evaluate.
        maximum_theta : float, optional
            The maximum theta angle value to evaluate.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=None, **kwargs)

        # Set calculation-specific values
        if 'symbols' in kwargs:
            self.symbols = kwargs['symbols']
        if 'number_of_steps_r' in kwargs:
            self.number_of_steps_r = kwargs['number_of_steps_r']
        if 'minimum_r' in kwargs:
            self.minimum_r = kwargs['minimum_r']
        if 'maximum_r' in kwargs:
            self.maximum_r = kwargs['maximum_r']
        if 'number_of_steps_theta' in kwargs:
            self.number_of_steps_theta = kwargs['number_of_steps_theta']
        if 'minimum_theta' in kwargs:
            self.minimum_theta = kwargs['minimum_theta']
        if 'maximum_theta' in kwargs:
            self.maximum_theta = kwargs['maximum_theta']

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
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
        self.number_of_steps_r = int(input_dict.get('number_of_steps_r', 100))
        self.number_of_steps_theta = int(input_dict.get('number_of_steps_theta', 100))

        # Load calculation-specific unitless floats
        self.minimum_theta = float(input_dict['minimum_theta'])
        self.maximum_theta = float(input_dict['maximum_theta'])

        # Load calculation-specific floats with units
        self.minimum_r = value(input_dict, 'minimum_r',
                               default_unit=self.units.length_unit,
                               default_term='0.5 angstrom')
        self.maximum_r = value(input_dict, 'maximum_r',
                               default_unit=self.units.length_unit,
                               default_term='6.0 angstrom')
        
        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)
        
        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

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
            params['buildcombos'] = 'bondangle potential_file intpot'
            params['minimum_r'] = '0.5 angstrom'
            params['maximum_r'] = '6.0 angstrom'
            params['number_of_steps_r'] = '100'
            params['minimum_theta'] = '1.0'
            params['maximum_theta'] = '180.0'
            params['number_of_steps_theta'] = '100'

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
    def templatekeys(self):
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'symbols': ' '.join([
                "The one or two model symbols to perform the scan for."]),
            'minimum_r': ' '.join([
                "The minimum interatomic spacing, r, for the scan.  Default",
                "value is '0.5 angstrom'."]),
            'maximum_r': ' '.join([
                "The maximum interatomic spacing, r, for the scan.  Default"
                "value is '6.0 angstrom'."]),
            'number_of_steps_r': ' '.join([
                "The number of interatomic spacing values, r, to use.  Default"
                "value is 100."]),
            'minimum_theta': ' '.join([
                "The minimum bond angle, theta, for the scan in degrees.  Default",
                "value is 1.0."]),
            'maximum_theta': ' '.join([
                "The maximum bond angle, theta, for the scan in degrees.  Default"
                "value is 180.0."]),
            'number_of_steps_theta': ' '.join([
                "The number of bond angle, theta, to use.  Default"
                "value is 100."]),
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
                ],
                [
                    'minimum_theta', 
                    'maximum_theta', 
                    'number_of_steps_theta',
                ]
            ]  
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'calculation-bond-angle-scan'

    def build_model(self):
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
        run_params['minimum_theta'] = self.minimum_theta
        run_params['maximum_theta'] = self.maximum_theta
        run_params['number_of_steps_theta'] = self.number_of_steps_theta

        dict_insert(calc, 'system-info', DM(), after='potential-LAMMPS')
        calc['system-info']['symbol'] = self.symbols
        
        # Build results
        if self.status == 'finished':
            calc['results'] = results = DM()
            results['file'] = self.results_file
            results['length_unit'] = self.results_length_unit
            results['energy_unit'] = self.results_energy_unit
        
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
        self.minimum_theta = run_params['minimum_theta']
        self.maximum_theta = run_params['maximum_theta']
        self.number_of_steps_theta = run_params['number_of_steps_theta']

        self.symbols = calc['system-info']['symbol']

        # Load results
        if self.status == 'finished':
           self.cluster = am.cluster.BondAngleMap(rmin=self.minimum_r,
                                                  rmax=self.maximum_r,
                                                  rnum=self.number_of_steps_r,
                                                  thetamin=self.minimum_theta,
                                                  thetamax=self.maximum_theta,
                                                  thetanum=self.number_of_steps_theta,
                                                  symbols=self.symbols)
           self.results_file = calc['calculation']['results']['file']
           self.results_length_unit = calc['calculation']['results']['length_unit']
           self.results_energy_unit = calc['calculation']['results']['energy_unit']

    def mongoquery(self, minimum_r=None, maximum_r=None,
                   number_of_steps_r=None, minimum_theta=None,
                   maximum_theta=None, number_of_steps_theta=None, symbol=None,
                   **kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.

        Parameters
        ----------
        minimum_r : float
            The minimum interatomic spacing to use for the scan.
        maximum_r : float
            The maximum interatomic spacing to use for the scan.
        number_of_steps_r : int
            The number of interatomic spacings to use for the scan.
        minimum_theta : float
            The minimum bond angle to use for the scan.
        maximum_theta : float
            The maximum bond angle to use for the scan.
        number_of_steps_theta : int
            The number of bond angles to use for the scan.
        symbol : str
            Element model symbol(s) assigned to the two atoms.
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
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.minimum_theta', minimum_theta)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maximum_theta', maximum_theta)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_theta', number_of_steps_theta)
        query.in_list.mongo(mquery, f'{root}.system-info.symbols', symbol)

        return mquery

    def cdcsquery(self, minimum_r=None, maximum_r=None, number_of_steps_r=None,
                  minimum_theta=None, maximum_theta=None,
                  number_of_steps_theta=None, symbol=None, **kwargs):
        """
        Builds a CDCS-style query based on kwargs values for the record style.

        Parameters
        ----------
        minimum_r : float
            The minimum interatomic spacing to use for the scan.
        maximum_r : float
            The maximum interatomic spacing to use for the scan.
        number_of_steps_r : int
            The number of evaluation points to use for the scan.
        minimum_theta : float
            The minimum bond angle to use for the scan.
        maximum_theta : float
            The maximum bond angle to use for the scan.
        number_of_steps_theta : int
            The number of bond angles to use for the scan.
        symbol : str
            Element model symbol(s) assigned to the two atoms.
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
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maxnimum_r', maximum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_r', number_of_steps_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.minimum_theta', minimum_theta)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maximum_theta', maximum_theta)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_theta', number_of_steps_theta)
        query.in_list.mongo(mquery, f'{root}.system-info.symbols', symbol)

        return mquery

########################## Metadata interactions ##############################

    def metadata(self):
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
        meta['minimum_theta'] = self.minimum_theta
        meta['maximum_theta'] = self.maximum_theta
        meta['number_of_steps_theta'] = self.number_of_steps_theta
        meta['symbols'] = ' '.join(sorted(self.symbols))
        
        # Extract results
        if self.status == 'finished':
            meta['results_file'] = self.results_file
            meta['results_length_unit'] = self.results_length_unit
            meta['results_energy_unit'] = self.results_energy_unit
        return meta

    @property
    def compare_terms(self):
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',
            'symbols',
            'potential_LAMMPS_key',
            'potential_key',
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

    def pandasfilter(self, dataframe, minimum_r=None, maximum_r=None,
                     number_of_steps_r=None, minimum_theta=None,
                     maximum_theta=None, number_of_steps_theta=None,
                     symbol=None, **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
        minimum_r : float
            The minimum interatomic spacing to use for the scan.
        maximum_r : float
            The maximum interatomic spacing to use for the scan.
        number_of_steps_r : int
            The number of evaluation points to use for the scan.
        minimum_theta : float
            The minimum bond angle to use for the scan.
        maximum_theta : float
            The maximum bond angle to use for the scan.
        number_of_steps_theta : int
            The number of bond angles to use for the scan.
        symbol : str
            Element model symbol(s) assigned to the two atoms.
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
            &query.str_match.pandas(dataframe, 'minimum_theta', minimum_theta)
            &query.str_match.pandas(dataframe, 'maximum_theta', maximum_theta)
            &query.str_match.pandas(dataframe, 'number_of_steps_theta', number_of_steps_theta)
            &query.in_list.pandas(dataframe, 'symbols', symbol)
        )
        
        return matches

########################### Calculation interactions ##########################

    def calc_inputs(self):
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
        input_dict['thetamin'] = self.minimum_theta
        input_dict['thetamax'] = self.maximum_theta
        input_dict['thetanum'] = self.number_of_steps_theta

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
        self.cluster = results_dict['cluster']
        self.results_file = results_dict['results_file']
        self.results_length_unit = results_dict['length_unit']
        self.results_energy_unit = results_dict['energy_unit']