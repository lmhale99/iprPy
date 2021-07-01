# coding: utf-8

# Standard Python libraries
import uuid
from copy import deepcopy

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
from .stacking_fault_map_2D import stackingfaultmap
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

# Global class properties
modelroot = 'calculation-stacking-fault-map-2D'

class StackingFaultPath():
    """Class for managing a path along a stacking fault map"""

    def __init__(self, sp):
        self.__direction = sp['direction']
        self.__coord = uc.value_unit(sp['minimum-energy-path'])
        self.__path = self.gamma.path(self.coord)
        self.__usf_mep = uc.value_unit(sp['unstable-fault-energy-mep'])
        self.__usf_urp = uc.value_unit(sp['unstable-fault-energy-unrelaxed-path'])
        self.__shear_mep = uc.value_unit(sp['ideal-shear-stress-mep'])
        self.__shear_urp = uc.value_unit(sp['ideal-shear-stress-unrelaxed-path'])

    @property
    def direction(self):
        return self.__direction

    @property
    def coord(self):
        return self.__coord

    @property
    def path(self):
        return self.__path

    @property
    def usf_mep(self):
        return self.__usf_mep

    @property
    def usf_urp(self):
        return self.__usf_urp

    @property
    def shear_mep(self):
        return self.__shear_mep

    @property
    def shear_urp(self):
        return self.__shear_urp

    def build_model(self, length_unit, energy_unit, stress_unit):
        sp = DM()
        sp['direction'] = self.direction
        sp['minimum-energy-path'] = uc.model(self.coord, length_unit)
        sp['unstable-fault-energy-mep'] = uc.model(self.usf_mep, energy_unit)
        sp['unstable-fault-energy-unrelaxed-path'] = uc.model(self.usf_urp, energy_unit)
        sp['ideal-shear-stress-mep'] = uc.model(self.shear_mep, stress_unit)
        sp['ideal-shear-stress-unrelaxed-path'] = uc.model(self.shear_urp, stress_unit)
        return sp

class StackingFaultMap2D(Calculation):
    """Class for managing 2D maps of stacking fault energy calculations"""

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

        # Initialize unique calculation attributes
        self.num_a1 = 10
        self.num_a2 = 10
        self.__gamma = None
        self.__paths = None

        # Define calc shortcut
        self.calc = stackingfaultmap

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
        """StackingFault subset"""
        return self.__defect

    @property
    def num_a1(self):
        """int: Number of fractional shifts along the a1vect direction to evaluate"""
        return self.__num_a1

    @num_a1.setter
    def num_a1(self, value):
        self.__num_a1 = int(value)

    @property
    def num_a2(self):
        """int: Number of fractional shifts along the a2vect direction to evaluate"""
        return self.__num_a2

    @num_a2.setter
    def num_a2(self, value):
        self.__num_a2 = int(value)

    @property
    def gamma(self):
        """atomman.defect.GammaSurface: GSF results"""
        if self.__gamma is None:
            raise ValueError('No results yet!')
        if not isinstance(self.__gamma, am.defect.GammaSurface):
            self.__gamma = am.defect.GammaSurface(model=self.__gamma)
        return self.__gamma

    @property
    def paths(self):
        if self.__paths is None:
            raise ValueError('No path results!')
        elif not isinstance(self.__paths, list):
            pass
        else:
            return self.__paths

    def load_paths(self, model=None):

        if model is None:
            model = self.__paths
            if model is None:
                raise ValueError('No path results!')
            if isinstance(model, list):
                return
        
        model = DM(model)
        self.__paths = []
        for sp in model.iteraslist('slip-path'):
            self.paths.append(StackingFaultPath(sp))            

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

        # Set calculation-specific values
        if 'num_a1' in kwargs:
            self.num_a1 = kwargs['num_a1']
        if 'num_a2' in kwargs:
            self.num_a2 = kwargs['num_a2']

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
    def template(self):
        """str: The template to use for generating calc.in files."""
        
        # Build universal content
        template = super().template

        # Build subset content
        template += self.commands.template()
        template += self.potential.template()
        template += self.system.template()
        template += self.defect.template()
        template += self.minimize.template()
        template += self.units.template()
        
        # Build calculation-specific content
        header = 'Run parameters'
        keys = [
            'stackingfault_num_a1',
            'stackingfault_num_a2', 
        ]
        template += self._template_builder(header, keys)
        
        return template     

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

        # Fetch universal key sets from parent
        universalkeys = super().multikeys
        
        # Specify calculation-specific key sets 
        keys =  [
            self.potential.keyset + self.system.keyset,
            [
                'sizemults',
                'stackingfault_minwidth',
            ],
            self.defect.keyset,
            [
                'stackingfault_num_a1',
                'stackingfault_num_a2',
            ],            
            self.minimize.keyset,
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

            try:
                paths = self.paths
            except:
                pass
            else:
                for path in paths:
                    calc.append('slip-path', path.build_model())

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

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.num_a1 = run_params['stackingfault_num_a1']
        self.nun_a2 = run_params['stackingfault_num_a2']

        # Load results
        if self.status == 'finished':
            self.__gamma = calc

            if 'slip-path' in calc:
                self.__paths = calc          

    @staticmethod
    def mongoquery(name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None, lammps_version=None,
                   potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                   potential_key=None, potential_id=None, 
                   stackingfault_key=None, stackingfault_id=None):
        
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
        mquery.update(StackingFault.mongoquery(modelroot,
                                             stackingfault_key=stackingfault_key,
                                             stackingfault_id=stackingfault_id))

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
                  stackingfault_key=None, stackingfault_id=None):
        
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
        mquery.update(StackingFault.mongoquery(modelroot,
                                             stackingfault_key=stackingfault_key,
                                             stackingfault_id=stackingfault_id))

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

        # Extract calculation-specific content
        
        # Extract results
        if self.status == 'finished':      
            try:
                paths = self.paths
            except:
                pass
            else:
                for path in paths:
                    direction = path.direction
                    meta[f'E_usf_mep_[{direction}]'] = path.usf_mep
                    meta[f'E_usf_urp_[{direction}]'] = path.usf_urp
                    meta[f'τ_ideal_mep_[{direction}]'] = path.shear_mep
                    meta[f'τ_ideal_urp_[{direction}]'] = path.shear_urp

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
            
            'stackingfault_key',

            'num_a1',
            'num_a2'
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

    def isvalid(self):
        return self.system.family == self.defect.family
    
    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, iprPy_version=None,
                     atomman_version=None, script=None, branch=None,
                     status=None, lammps_version=None,
                     potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                     potential_key=None, potential_id=None, 
                     stackingfault_key=None, stackingfault_id=None):
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
            &StackingFault.pandasfilter(dataframe,
                                      stackingfault_key=stackingfault_key,
                                      stackingfault_id=stackingfault_id)

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

        # Remove unused subset inputs

        # Add calculation-specific inputs
        input_dict['num_a1'] = self.num_a1
        input_dict['num_a2'] = self.num_a2

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
            self.__gamma = results_dict['gamma']

        self._results(json=results_json)