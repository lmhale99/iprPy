# coding: utf-8
# Standard Python libraries

from datamodelbase import query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .elastic_constants_static import elastic_constants_static
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

class ElasticConstantsStatic(Calculation):
    """Class for managing static elastic constants calculations from small strains"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""
        
        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        self.__system_mods = AtommanSystemManipulate(self)
        self.__minimize = LammpsMinimize(self)
        subsets = (self.commands, self.potential, self.system,
                   self.system_mods, self.minimize, self.units)

        # Initialize unique calculation attributes
        self.strainrange = 1e-6
        self.__C = None
        self.__raw_Cij_positive = None
        self.__raw_Cij_negative = None
        
        # Define calc shortcut
        self.calc = elastic_constants_static

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self):
        """list: the names of each file used by the calculation."""
        return [
            'elastic_constants_static.py',
            'cij.template'
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
    def minimize(self):
        """LammpsMinimize subset"""
        return self.__minimize

    @property
    def strainrange(self):
        """float: Strain step size used in estimating elastic constants"""
        return self.__strainrange

    @strainrange.setter
    def strainrange(self, value):
        self.__strainrange = float(value)
        
    @property
    def C(self):
        """atomman.ElasticConstants: Averaged elastic constants"""
        if self.__C is None:
            raise ValueError('No results yet!')
        return self.__C

    @property
    def raw_Cij_positive(self):
        """numpy.NDArray: Cij 6x6 array measured using positive strain steps"""
        if self.__raw_Cij_positive is None:
            raise ValueError('No results yet!')
        return self.__raw_Cij_positive

    @property
    def raw_Cij_negative(self):
        """numpy.NDArray: Cij 6x6 array measured using negative strain steps"""
        if self.__raw_Cij_negative is None:
            raise ValueError('No results yet!')
        return self.__raw_Cij_negative

    def set_values(self, name=None, **kwargs):
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameter
        ---------
        name : str, optional
            The name to assign to the calculation.  By default, this is set as
            the calculation's key.
        strainrange : float, optional
            The magnitude of strain to use.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=None, **kwargs)

        # Set calculation-specific values
        if 'strainrange' in kwargs:
            self.strainrange = kwargs['strainrange']

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
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

        # Load calculation-specific unitless floats
        self.strainrange = float(input_dict.get('strainrange', 1e-6))

        # Load calculation-specific floats with units
        
        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)
        
        # Load minimization parameters
        self.minimize.load_parameters(input_dict)

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
            params['buildcombos'] = 'atomicparent load_file parent'
            params['parent_record'] = 'relaxed_crystal'
            params['parent_standing'] = 'good'
            params['sizemults'] = '10 10 10'
            params['maxiterations'] = '5000'
            params['maxevaluations'] = '10000'
            params['strainrange'] = ['1e-6', '1e-7', '1e-8']


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
    def templatekeys(self):
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'strainrange': ' '.join([
                "The strain range to apply to the system to evaluate the",
                "elastic constants.  Default value is '1e-6'"]),
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
            
            # Strainrange
            [
                [
                    'strainrange',
                ]
            ] +
            
            [
                self.minimize.keyset
            ]
        )    
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'calculation-relax-static'

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
        self.minimize.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']
        run_params['strain-range'] = self.strainrange

        # Build results
        if self.status == 'finished':
            cij = DM()
            cij['Cij'] = uc.model(self.raw_Cij_negative,
                                  self.units.pressure_unit)
            calc.append('raw-elastic-constants', cij)
            cij = DM()
            cij['Cij'] = uc.model(self.raw_Cij_positive,
                                  self.units.pressure_unit)
            calc.append('raw-elastic-constants', cij)
            
            calc['elastic-constants'] = DM()
            calc['elastic-constants']['Cij'] = uc.model(self.C.Cij,
                                                        self.units.pressure_unit)

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
        self.strainrange = run_params['strain-range']

        # Load results
        if self.status == 'finished':
            self.__raw_Cij_negative = uc.value_unit(calc['raw-elastic-constants'][0]['Cij'])
            self.__raw_Cij_positive = uc.value_unit(calc['raw-elastic-constants'][1]['Cij'])
            Cij = uc.value_unit(calc['elastic-constants']['Cij'])
            self.__C = am.ElasticConstants(Cij=Cij)

    def mongoquery(self, strainrange=None, **kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.

        Parameters
        ----------
        strainrange : float or list, optional
            strainrange values to parse by.
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
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.strain-range', strainrange)

        return mquery

    def cdcsquery(self, strainrange=None, **kwargs):
        """
        Builds a CDCS-style query based on kwargs values for the record style.

        Parameters
        ----------
        strainrange : float or list, optional
            strainrange values to parse by.
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
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.strain-range', strainrange)
        
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
        meta['strainrange'] = self.strainrange
        
        # Extract results
        if self.status == 'finished':
            meta['C'] = self.C
            meta['raw_Cij_negative'] = self.raw_Cij_negative
            meta['raw_Cij_positive'] = self.raw_Cij_positive

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
        return {
            'strainrange':1e-10,
        }

    def pandasfilter(self, dataframe, strainrange=None, **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
        strainrange : float or list, optional
            strainrange values to parse by.
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
            &query.str_match.pandas(dataframe, 'strainrange', strainrange)
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
        del input_dict['ucell']

        # Add calculation-specific inputs
        input_dict['strainrange'] = self.strainrange

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
        self.__C = results_dict['C']
        self.__raw_Cij_negative = results_dict['raw_Cij_negative']
        self.__raw_Cij_positive = results_dict['raw_Cij_positive']
