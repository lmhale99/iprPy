# coding: utf-8

# Standard Python libraries
import uuid
from copy import deepcopy
import random

import numpy as np

from datamodelbase import query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .dislocation_periodic_array import dislocation_array
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

class DislocationPeriodicArray(Calculation):
    """Class for managing periodic array of dislocations constructions and relaxations"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""
        
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
        self.duplicatecutoff = uc.set_in_units(0.5, 'angstrom')
        self.boundarywidth = 0.0
        self.boundaryscale = False
        self.onlylinear = False
        self.__dumpfile_base = None
        self.__dumpfile_defect = None
        self.__symbols_base = None
        self.__symbols_defect = None
        self.__potential_energy_defect = None
        self.__dislocation = None
        self.__preln = None
        self.__K_tensor = None
        
        # Define calc shortcut
        self.calc = dislocation_array

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self):
        """list: the names of each file used by the calculation."""
        return [
            'dislocation_periodic_array.py',
            'disl_relax.template'
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
        """Dislocation subset"""
        return self.__defect

    @property
    def elastic(self):
        """AtommanElasticConstants subset"""
        return self.__elastic

    @property
    def annealtemperature(self):
        """float: Temperature to use for annealing the system"""
        return self.__annealtemperature

    @annealtemperature.setter
    def annealtemperature(self, value):
        value = float(value)
        assert value >= 0.0
        self.__annealtemperature = float(value)

    @property
    def annealsteps(self):
        """int: Number of time steps to use for annealing the system"""
        if self.__annealsteps is None:
            if self.annealtemperature == 0.0:
                return 0
            else:
                return 10000
        else:
            return self.__annealsteps

    @annealsteps.setter
    def annealsteps(self, value):
        if value is None:
            self.__annealsteps = None
        else:
            self.__annealsteps = int(value)

    @property
    def randomseed(self):
        """str: MD integration scheme"""
        return self.__randomseed

    @randomseed.setter
    def randomseed(self, value):
        if value is None:
            value = random.randint(1, 900000000)
        else:
            value = int(value)
            assert value > 0 and value <= 900000000
        self.__randomseed = value

    @property
    def duplicatecutoff(self):
        """float: The cutoff used to identify duplicate atoms"""
        return self.__duplicatecutoff

    @duplicatecutoff.setter
    def duplicatecutoff(self, value):
        value = float(value)
        assert value >= 0.0
        self.__duplicatecutoff = value

    @property
    def boundarywidth(self):
        """float: The minimum width of the boundary region"""
        return self.__boundarywidth

    @boundarywidth.setter
    def boundarywidth(self, value):
        value = float(value)
        assert value >= 0.0
        self.__boundarywidth = float(value)

    @property
    def boundaryscale(self):
        """bool: Flag indicating if boundarywidth is scaled versus the system or absolute"""
        return self.__boundaryscale

    @boundaryscale.setter
    def boundaryscale(self, value):
        self.__boundaryscale = boolean(value)

    @property
    def onlylinear(self):
        """bool: Flag indicating if only linear gradient displacements are used"""
        return self.__onlylinear

    @onlylinear.setter
    def onlylinear(self, value):
        self.__onlylinear = boolean(value)

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
    def symbols_base(self):
        """list: Model symbols for the base system"""
        if self.__symbols_base is None:
            raise ValueError('No results yet!')
        return self.__symbols_base
    
    @property
    def symbols_defect(self):
        """list: Model symbols for the defect system"""
        if self.__symbols_defect is None:
            raise ValueError('No results yet!')
        return self.__symbols_defect

    @property
    def potential_energy_defect(self):
        """float: Potential energy of the defect system"""
        if self.__potential_energy_defect is None:
            raise ValueError('No results yet!')
        return self.__potential_energy_defect

    @property
    def dislocation(self):
        """atomman.defect.Dislocation: Volterra dislocation solution"""
        if self.__dislocation is None:
            raise ValueError('No results yet!')
        return self.__dislocation

    @property
    def preln(self):
        if self.__preln is None:
            return self.dislocation.dislsol.preln
        else:
            return self.__preln

    @property
    def K_tensor(self):
        if self.__K_tensor is None:
            return self.dislocation.dislsol.K_tensor
        else:
            return self.__K_tensor

    def set_values(self, name=None, **kwargs):
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameter
        ---------
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
        duplicatecutoff : float, optional
            Distance tolerance to use for identifying duplicate atoms when the
            dislocation has an edge component.
        boundarywidth : float, optional
            The minimum width of the boundary region.
        boundaryscale : bool, optional
            Indicates if boundarywidth is absolute (False) or relative to the
            unit cell's a lattice parameter (True).
        onlylinear : bool, optional
            If True, the dislocation solution used will only be based on a
            linear gradient of displacements rather than the Volterra
            dislocation solution.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=None, **kwargs)

        # Set calculation-specific values
        if 'annealtemperature' in kwargs:
            self.annealtemperature = kwargs['annealtemperature']
        if 'annealsteps' in kwargs:
            self.annealsteps = kwargs['annealsteps']
        if 'randomseed' in kwargs:
            self.randomseed = kwargs['randomseed']
        if 'duplicatecutoff' in kwargs:
            self.duplicatecutoff = kwargs['duplicatecutoff']
        if 'boundarywidth' in kwargs:
            self.boundarywidth = kwargs['boundarywidth']
        if 'boundaryscale' in kwargs:
            self.boundaryscale = kwargs['boundaryscale']
        if 'onlylinear' in kwargs:
            self.onlylinear = kwargs['onlylinear']

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
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
        
        # Load calculation-specific floats with units
        self.boundarywidth = value(input_dict, 'dislocation_boundarywidth',
                                   default_unit=self.units.length_unit,
                                   default_term='0 angstrom')
        self.duplicatecutoff = value(input_dict, 'dislocation_duplicatecutoff',
                                     default_unit=self.units.length_unit,
                                     default_term='0.5 angstrom')
        
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

        params['dislocation_boundarywidth'] = '3'
        params['dislocation_boundaryscale'] = 'True'
        params['dislocation_duplicatecutoff'] = '1 angstrom'
        params['annealtemperature'] = '10'
        params['annealsteps'] = '10000000'
        params['maxiterations'] = '10000'
        params['maxevaluations'] = '100000'

        # Set branch-specific parameters
        if branch == 'fcc_edge_mix':
            params['parent_family'] = 'A1--Cu--fcc'
            params['defect_id'] = 'A1--Cu--fcc--a-2-110--90-edge--{111}'
            params['sizemults'] = '1 200 50'
            params['dislocation_onlylinear'] = 'False'

        elif branch == 'fcc_screw':
            params['parent_family'] = 'A1--Cu--fcc'
            params['defect_id'] = 'A1--Cu--fcc--a-2-110--0-screw--{111}'
            params['sizemults'] = '1 200 50'
            params['dislocation_onlylinear'] = 'True'

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
    def templatekeys(self):
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
    def singularkeys(self):
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
            ]
        )
        return keys
    
    @property
    def multikeys(self):
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
    def modelroot(self):
        """str: The root element of the content"""
        return 'calculation-dislocation-periodic-array'

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
            self.__potential_energy_defect = uc.value_unit(calc['defect-system']['potential-energy'])
            
            elsol = calc['elastic-solution'] 
            self.__preln = uc.value_unit(elsol['pre-ln-factor'])
            self.__K_tensor = uc.value_unit(elsol['K-tensor'])

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
            meta['potential_energy_defect'] = self.potential_energy_defect
            meta['preln'] = self.preln
            meta['K_tensor'] = self.K_tensor

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
            
            'a_mult',
            'b_mult',
            'c_mult',
            
            'dislocation_key',

            'annealsteps',
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'annealtemperature':1,
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
            
        # Modify inputs for calculation
        input_dict['annealtemp'] = self.annealtemperature
        input_dict['annealsteps'] = self.annealsteps
        input_dict['randomseed'] = self.randomseed
        input_dict['linear'] = self.onlylinear
        input_dict['cutoff'] = self.duplicatecutoff
        input_dict['boundarywidth'] = self.boundarywidth
        input_dict['boundaryscale'] = self.boundaryscale

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
        self.__dumpfile_base = results_dict['dumpfile_base']
        self.__dumpfile_defect = results_dict['dumpfile_disl']
        self.__symbols_base = results_dict['symbols_base']
        self.__symbols_defect = results_dict['symbols_disl']
        self.__potential_energy_defect = results_dict['E_total_disl']
        self.__dislocation = results_dict['dislocation']
