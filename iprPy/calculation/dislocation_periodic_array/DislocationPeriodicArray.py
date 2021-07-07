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

# Global class properties
modelroot = 'calculation-dislocation-periodic-array'

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
        super().__init__(model=model, name=name, params=params, **kwargs)

############################## Class attributes ################################

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
        """Used to set initial common values for the calculation."""
        
        # Set universal content
        super().set_values(name=None, **kwargs)

        # Set subset values
        self.units.set_values(**kwargs)
        self.potential.set_values(**kwargs)
        self.commands.set_values(**kwargs)
        self.system.set_values(**kwargs)
        self.minimize.set_values(**kwargs)
        self.defect.set_values(**kwargs)
        self.elastic.set_values(**kwargs)

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
            'atomicparent load_file parent',
            'defect dislocation_file'
        ]
        params['parent_record'] = 'calculation_elastic_constants_static'
        params['parent_load_key'] = 'system-info'
        params['parent_strainrange'] = '1e-7'
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
    def template(self):
        """str: The template to use for generating calc.in files."""
        
        # Build universal content
        template = super().template

        # Build subset content
        template += self.commands.template()
        template += self.potential.template()
        template += self.system.template()
        template += self.elastic.template()
        template += self.defect.template()
        template += self.minimize.template()
        template += self.units.template()
        
        # Build calculation-specific content
        header = 'Run parameters'
        keys = [
            'annealtemperature',
            'annealsteps',
            'randomseed',
            'dislocation_duplicatecutoff',
            'dislocation_boundarywidth',
            'dislocation_boundaryscale',
            'dislocation_onlylinear',
        ]
        template += self._template_builder(header, keys)
        
        return template     
    
    @property
    def singularkeys(self):
        """list: Calculation keys that can have single values during prepare."""

        # Fetch universal key sets from parent
        universalkeys = super().singularkeys
        
        # Specify calculation-specific key sets 
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
        """
        list: Calculation key sets that can have multiple values during prepare.
        """
        # Fetch universal key sets from parent
        universalkeys = super().multikeys
        
        # Specify calculation-specific key sets 
        keys = [
            self.potential.keyset + self.system.keyset + self.elastic.keyset,
            [
                'sizemults',
                'amin',
                'bmin',
                'cmin',
            ],
            self.defect.keyset,
            self.minimize.keyset + [
                'randomseed',
                'annealtemperature',
                'annealsteps',
            ]
        ]
                    
        # Join and return
        return universalkeys + keys

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        return modelroot

    def build_model(self):

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

        return model

    def load_model(self, model, name=None):

        # Load universal content
        super().load_model(model, name=name)
        calc = self.model[self.modelroot]

        # Load subset content
        #self.units.load_model(calc)
        self.potential.load_model(calc)
        self.commands.load_model(calc)
        self.system.load_model(calc)
        self.minimize.load_model(calc)
        self.defect.load_model(calc)
        self.elastic.load_model(calc)

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

    @staticmethod
    def mongoquery(name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None, lammps_version=None,
                   potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                   potential_key=None, potential_id=None, 
                   dislocation_key=None, dislocation_id=None):
        
        # Build universal terms
        mquery = Calculation.mongoquery(modelroot, name=name, key=key,
                                    iprPy_version=iprPy_version,
                                    atomman_version=atomman_version,
                                    script=script, branch=branch,
                                    status=status)

        # Build subset terms
        mquery.update(LammpsCommands.mongoquery(modelroot,
                                                lammps_version=lammps_version))
        mquery.update(LammpsPotential.mongoquery(modelroot,
                                                 potential_LAMMPS_key=potential_LAMMPS_key,
                                                 potential_LAMMPS_id=potential_LAMMPS_id,
                                                 potential_key=potential_key,
                                                 potential_id=potential_id))
        #mquery.update(AtommanSystemLoad.mongoquery(modelroot,...)
        #mquery.update(AtommanSystemManipulate.mongoquery(modelroot,...)
        mquery.update(Dislocation.mongoquery(modelroot,
                                             dislocation_key=dislocation_key,
                                             dislocation_id=dislocation_id))

        # Build calculation-specific terms
        root = f'content.{modelroot}'
        #query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.minimum_r', minimum_r)
        #query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maxnimum_r', maximum_r)
        #query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_r', number_of_steps_r)

        return mquery

    @staticmethod
    def cdcsquery(key=None, iprPy_version=None,
                  atomman_version=None, script=None, branch=None,
                  status=None, lammps_version=None,
                  potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                  potential_key=None, potential_id=None, 
                  dislocation_key=None, dislocation_id=None):
        
        # Build universal terms
        mquery = Calculation.cdcsquery(modelroot, key=key,
                                    iprPy_version=iprPy_version,
                                    atomman_version=atomman_version,
                                    script=script, branch=branch,
                                    status=status)

        # Build subset terms
        mquery.update(LammpsCommands.cdcsquery(modelroot,
                                               lammps_version=lammps_version))
        mquery.update(LammpsPotential.cdcsquery(modelroot,
                                                potential_LAMMPS_key=potential_LAMMPS_key,
                                                potential_LAMMPS_id=potential_LAMMPS_id,
                                                potential_key=potential_key,
                                                potential_id=potential_id))
        #mquery.update(AtommanSystemLoad.mongoquery(modelroot,...)
        #mquery.update(AtommanSystemManipulate.mongoquery(modelroot,...)
        mquery.update(Dislocation.mongoquery(modelroot,
                                             dislocation_key=dislocation_key,
                                             dislocation_id=dislocation_id))

        # Build calculation-specific terms
        root = modelroot
        #query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.minimum_r', minimum_r)
        #query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maxnimum_r', maximum_r)
        #query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_r', number_of_steps_r)

        return mquery

########################## Metadata interactions ##############################

    def metadata(self):
        """
        Converts the structured content to a simpler dictionary.
        
        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        # Extract universal content
        meta = super().metadata()
        
        # Extract subset content
        self.potential.metadata(meta)
        self.commands.metadata(meta)
        self.system.metadata(meta)
        self.minimize.metadata(meta)
        self.defect.metadata(meta)
        self.elastic.metadata(meta)

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
    
    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, iprPy_version=None,
                     atomman_version=None, script=None, branch=None,
                     status=None, lammps_version=None,
                     potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                     potential_key=None, potential_id=None, 
                     dislocation_key=None, dislocation_id=None):
        matches = (
            # Filter by universal terms
            Calculation.pandasfilter(dataframe, name=name, key=key,
                                 iprPy_version=iprPy_version,
                                 atomman_version=atomman_version,
                                 script=script, branch=branch, status=status)
            
            # Filter by subset terms
            &LammpsCommands.pandasfilter(dataframe,
                                         lammps_version=lammps_version)
            &LammpsPotential.pandasfilter(dataframe,
                                          potential_LAMMPS_key=potential_LAMMPS_key,
                                          potential_LAMMPS_id=potential_LAMMPS_id,
                                          potential_key=potential_key,
                                          potential_id=potential_id)
            #&AtommanSystemLoad.pandasfilter(dataframe, ...)
            #&AtommanSystemManipulate.pandasfilter(dataframe, ...)
            &Dislocation.pandasfilter(dataframe,
                                      dislocation_key=dislocation_key,
                                      dislocation_id=dislocation_id)

            # Filter by calculation-specific terms
            #&query.str_match.pandas(dataframe, 'minimum_r', minimum_r)
            #&query.str_match.pandas(dataframe, 'maximum_r', maximum_r)
            #&query.str_match.pandas(dataframe, 'number_of_steps_r', number_of_steps_r)
            #&query.str_contains.pandas(dataframe, 'symbols', symbols)
        )
        
        return matches

########################### Calculation interactions ##########################

    def calc_inputs(self):
        """Builds calculation inputs from the class's attributes"""
        
        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        self.commands.calc_inputs(input_dict)
        self.potential.calc_inputs(input_dict)
        self.system.calc_inputs(input_dict)
        self.minimize.calc_inputs(input_dict)
        self.defect.calc_inputs(input_dict)
        self.elastic.calc_inputs(input_dict)

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
    
    def run(self, newkey=False, results_json=False, verbose=False):
        """
        Runs the calculation using the current class attribute values. Status
        after running will be either "finished" or "error".

        Parameters
        ----------
        newkey : bool, optional
            If True, then the calculation's key and name will be replaced with
            a new UUID4.  This allows for iterations on previous runs to be
            uniquely labeled.  Default value is False.
        results_json : bool, optional
            If True, then a "results.json" file will be generated following
            the run.
        verbose : bool, optional
            If True, a message relating to the calculation's status will be
            printed upon completion.  Default value is False.
        """
        # Run calculation
        results_dict = super().run(newkey=newkey, verbose=verbose)
        
        # Process results
        if self.status == 'finished':
            self.__dumpfile_base = results_dict['dumpfile_base']
            self.__dumpfile_defect = results_dict['dumpfile_disl']
            self.__symbols_base = results_dict['symbols_base']
            self.__symbols_defect = results_dict['symbols_disl']
            self.__potential_energy_defect = results_dict['E_total_disl']
            self.__dislocation = results_dict['dislocation']

        self._results(json=results_json)