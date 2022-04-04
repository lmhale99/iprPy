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
from .stacking_fault_static import stackingfault
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

class StackingFaultStatic(Calculation):
    """Class for managing stacking fault energy calculations"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""
        
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
        self.a1 = 0.0
        self.a2 = 0.0
        self.__dumpfile_base = None
        self.__dumpfile_defect = None
        self.__potential_energy_base = None
        self.__potential_energy_defect = None
        self.__gsf_energy = None
        self.__gsf_displacement = None
        
        # Define calc shortcut
        self.calc = stackingfault

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self):
        """list: the names of each file used by the calculation."""
        return [
            'stacking_fault_static.py',
            'sfmin.template'
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
    def minimize(self):
        """LammpsMinimize subset"""
        return self.__minimize

    @property
    def defect(self):
        """StackingFault subset"""
        return self.__defect

    @property
    def a1(self):
        """float: Fractional shift along the a1vect direction to apply"""
        return self.__a1

    @a1.setter
    def a1(self, value):
        self.__a1 = float(value)

    @property
    def a2(self):
        """float: Fractional shift along the a2vect direction to apply"""
        return self.__a2

    @a2.setter
    def a2(self, value):
        self.__a2 = float(value)

    @property
    def dumpfile_base(self):
        """str: Name of the LAMMPS dump file of the 0 shift reference system"""
        if self.__dumpfile_base is None:
            raise ValueError('No results yet!')
        return self.__dumpfile_base
    
    @property
    def dumpfile_defect(self):
        """str: Name of the LAMMPS dump file of the defect system"""
        if self.__dumpfile_defect is None:
            raise ValueError('No results yet!')
        return self.__dumpfile_defect

    @property
    def potential_energy_base(self):
        """float: Potential energy of the 0 shift reference system"""
        if self.__potential_energy_base is None:
            raise ValueError('No results yet!')
        return self.__potential_energy_base

    @property
    def potential_energy_defect(self):
        """float: Potential energy of the defect system"""
        if self.__potential_energy_defect is None:
            raise ValueError('No results yet!')
        return self.__potential_energy_defect

    @property
    def gsf_displacement(self):
        """float: Difference in planar displacement between reference and defect systems"""
        if self.__gsf_displacement is None:
            raise ValueError('No results yet!')
        return self.__gsf_displacement

    @property
    def gsf_energy(self):
        """float: Generalized stacking fault energy associated with the defect system"""
        if self.__gsf_energy is None:
            raise ValueError('No results yet!')
        return self.__gsf_energy

    def set_values(self, name=None, **kwargs):
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameters
        ----------
        name : str, optional
            The name to assign to the calculation.  By default, this is set as
            the calculation's key.
        a1 : float, optional
            The fractional shift to make along the a1 shift vector.
        a2 : float, optional
            The fractional shift to make along the a2 shift vector.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'a1' in kwargs:
            self.a1 = kwargs['a1']
        if 'a2' in kwargs:
            self.a2 = kwargs['a2']

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
        self.a1 = float(input_dict.get('stackingfault_a1', 0.0))
        self.a2 = float(input_dict.get('stackingfault_a2', 0.0))
        
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
        raise NotImplementedError('Not implemented for this calculation style')
    
    @property
    def templatekeys(self):
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'stackingfault_a1': ' '.join([
                "The fractional shift to apply along the a1 direction."]),
            'stackingfault_a2': ' '.join([
                "The fractional shift to apply along the a2 direction."]),
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

            # Defect multikeys
            self.defect.multikeys + 
                
            # Run parameter keys
            [    
                [
                    'stackingfault_a1',
                    'stackingfault_a2',
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
    def modelroot(self):
        """str: The root element of the content"""
        return 'calculation-stacking-fault-static'

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
        self.defect.build_model(calc, after='system-info')
        self.minimize.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']
        
        run_params['stackingfault_a1'] = self.a1
        run_params['stackingfault_a2'] = self.a2
        
        # Build results
        if self.status == 'finished':
            calc['defect-free-system'] = DM()
            calc['defect-free-system']['artifact'] = DM()
            calc['defect-free-system']['artifact']['file'] = self.dumpfile_base
            calc['defect-free-system']['artifact']['format'] = 'atom_dump'
            calc['defect-free-system']['symbols'] = self.system.ucell.symbols
            calc['defect-free-system']['potential-energy'] = uc.model(self.potential_energy_base, 
                                                                      self.units.energy_unit)
            
            calc['defect-system'] = DM()
            calc['defect-system']['artifact'] = DM()
            calc['defect-system']['artifact']['file'] = self.dumpfile_defect
            calc['defect-system']['artifact']['format'] = 'atom_dump'
            calc['defect-system']['symbols'] = self.system.ucell.symbols
            calc['defect-system']['potential-energy'] = uc.model(self.potential_energy_defect,
                                                                 self.units.energy_unit)
            
            # Save the stacking fault energy
            energy_per_area_unit = f'{self.units.energy_unit}/{self.units.length_unit}^2'
            calc['stacking-fault-energy'] = uc.model(self.gsf_energy,
                                                     energy_per_area_unit)
            
            # Save the plane separation
            calc['plane-separation'] = uc.model(self.gsf_displacement,
                                                self.units.length_unit)

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
        self.a1 = run_params['stackingfault_a1']
        self.a2 = run_params['stackingfault_a2']

        # Load results
        if self.status == 'finished':
            self.__dumpfile_base = calc['defect-free-system']['artifact']['file']
            self.__potential_energy_base = uc.value_unit(calc['defect-free-system']['potential-energy'])
            
            self.__dumpfile_defect= calc['defect-system']['artifact']['file']
            self.__potential_energy_defect = uc.value_unit(calc['defect-system']['potential-energy'])

            self.__gsf_energy = uc.value_unit(calc['stacking-fault-energy'])
            self.__gsf_displacement = uc.value_unit(calc['plane-separation'])
            
    def mongoquery(self, **kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.

        Parameters
        ----------
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
       
        return mquery

    def cdcsquery(self, **kwargs):
        
        """
        Builds a CDCS-style query based on kwargs values for the record style.

        Parameters
        ----------
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
        
        # Extract results
        if self.status == 'finished':            
            meta['dumpfile_base'] = self.dumpfile_base
            meta['dumpfile_defect'] = self.dumpfile_defect
            meta['E_pot_base'] = self.potential_energy_base
            meta['E_pot_defect'] = self.potential_energy_defect
            meta['E_gsf'] = self.gsf_energy
            meta['delta_gsf'] = self.gsf_displacement

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
            
            'stackingfault_key',
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'a1':1e-5,
            'a2':1e-5,
        }

    def isvalid(self):
        return self.system.family == self.defect.family
    
    def pandasfilter(self, dataframe, **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
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
        
        return matches

########################### Calculation interactions ##########################

    def calc_inputs(self):
        """Builds calculation inputs from the class's attributes"""
        
        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Add calculation-specific inputs
        input_dict['a1'] = self.a1
        input_dict['a2'] = self.a2

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
        self.__dumpfile_base = results_dict['dumpfile_0']
        self.__dumpfile_defect = results_dict['dumpfile_sf']
        self.__potential_energy_base = results_dict['E_total_0']
        self.__potential_energy_defect = results_dict['E_total_sf']
        self.__gsf_energy = results_dict['E_gsf']
        self.__gsf_displacement = results_dict['delta_disp']
