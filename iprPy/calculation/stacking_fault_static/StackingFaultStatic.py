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
from .stacking_fault_static import stackingfault
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

# Global class properties
modelroot = 'calculation-stacking-fault-static'

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

        # Initialize unique calculation attributes
        self.a1 = 0.0
        self.a2 = 0.0
        self.__dumpfile_base = None
        self.__dumpfile_defect = None
        self.__potential_energy_base = None
        self.__potential_energy_defect = None
        #self.__displacement_base = None
        #self.__displacement_defect = None
        #self.__surface_area = None
        self.__gsf_energy = None
        self.__gsf_displacement = None
        
        # Define calc shortcut
        self.calc = stackingfault

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

    #@property
    #def displacement_base(self):
    #    """float: Planar displacement in the 0 shift reference system"""
    #    if self.__displacement_base is None:
    #        raise ValueError('No results yet!')
    #    return self.__displacement_base

    #@property
    #def displacement_defect(self):
    #    """float: Planar displacement in the defect system"""
    #    if self.__displacement_defect is None:
    #        raise ValueError('No results yet!')
    #    return self.__displacement_defect

    @property
    def gsf_displacement(self):
        """float: Difference in planar displacement between reference and defect systems"""
        if self.__gsf_displacement is None:
            raise ValueError('No results yet!')
        return self.__gsf_displacement

    #@property
    #def surface_area(self):
    #    """float: Area associated with the free surface"""
    #    if self.__surface_area is None:
    #        raise ValueError('No results yet!')
    #    return self.__surface_area

    @property
    def gsf_energy(self):
        """float: Generalized stacking fault energy associated with the defect system"""
        if self.__gsf_energy is None:
            raise ValueError('No results yet!')
        return self.__gsf_energy

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
            'stackingfault_a1',
            'stackingfault_a2', 
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
                'stackingfault_a1',
                'stackingfault_a2',
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
        input_dict['a1'] = self.a1
        input_dict['a2'] = self.a2

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
            self.__dumpfile_base = results_dict['dumpfile_0']
            self.__dumpfile_defect = results_dict['dumpfile_sf']
            self.__potential_energy_base = results_dict['E_total_0']
            self.__potential_energy_defect = results_dict['E_total_sf']
            self.__gsf_energy = results_dict['E_gsf']
            self.__gsf_displacement = results_dict['delta_disp']

        self._results(json=results_json)