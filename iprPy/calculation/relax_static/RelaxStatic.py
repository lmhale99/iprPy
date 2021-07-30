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
from .relax_static import relax_static
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

# Global class properties
modelroot = 'calculation-relax-static'

class RelaxStatic(Calculation):
    """Class for managing static relaxations"""

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

        # Initialize unique calculation attributes
        self.pressure_xx = 0.0
        self.pressure_yy = 0.0
        self.pressure_zz = 0.0
        self.pressure_xy = 0.0
        self.pressure_xz = 0.0
        self.pressure_yz = 0.0
        self.displacementkick = 0.0
        self.maxcycles = 100     
        self.cycletolerance = 1e-10

        self.__initial_dump = None
        self.__final_dump = None
        self.__final_box = None
        self.__potential_energy = None
        self.__measured_pressure_xx = None
        self.__measured_pressure_yy = None
        self.__measured_pressure_zz = None
        self.__measured_pressure_xy = None
        self.__measured_pressure_xz = None
        self.__measured_pressure_yz = None
        
        # Define calc shortcut
        self.calc = relax_static

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
    def system_mods(self):
        """AtommanSystemManipulate subset"""
        return self.__system_mods
    
    @property
    def minimize(self):
        """LammpsMinimize subset"""
        return self.__minimize

    @property
    def pressure_xx(self):
        """float: Target relaxation pressure component xx"""
        return self.__pressure_xx

    @pressure_xx.setter
    def pressure_xx(self, value):
        self.__pressure_xx = float(value)

    @property
    def pressure_yy(self):
        """float: Target relaxation pressure component yy"""
        return self.__pressure_yy

    @pressure_yy.setter
    def pressure_yy(self, value):
        self.__pressure_yy = float(value)
    
    @property
    def pressure_zz(self):
        """float: Target relaxation pressure component zz"""
        return self.__pressure_zz

    @pressure_zz.setter
    def pressure_zz(self, value):
        self.__pressure_zz = float(value)

    @property
    def pressure_xy(self):
        """float: Target relaxation pressure component xy"""
        return self.__pressure_xy

    @pressure_xy.setter
    def pressure_xy(self, value):
        self.__pressure_xy = float(value)

    @property
    def pressure_xz(self):
        """float: Target relaxation pressure component xz"""
        return self.__pressure_xz

    @pressure_xz.setter
    def pressure_xz(self, value):
        self.__pressure_xz = float(value)
    
    @property
    def pressure_yz(self):
        """float: Target relaxation pressure component yz"""
        return self.__pressure_yz

    @pressure_yz.setter
    def pressure_yz(self, value):
        self.__pressure_yz = float(value)

    @property
    def displacementkick(self):
        """float: Magnitude of random displacements to use"""
        return self.__displacementkick

    @displacementkick.setter
    def displacementkick(self, value):
        if isinstance(value, str):
            self.__displacementkick = uc.set_literal(value)
        else:
            self.__displacementkick = float(value)
    
    @property
    def maxcycles(self):
        """int: Maximum number of relaxation cycles"""
        return self.__maxcycles

    @maxcycles.setter
    def maxcycles(self, value):
        self.__maxcycles = int(value)

    @property
    def cycletolerance(self):
        """float: Stopping tolerance associated with the relaxation cycles"""
        return self.__cycletolerance

    @cycletolerance.setter
    def cycletolerance(self, value):
        self.__cycletolerance = float(value)

    @property
    def initial_dump(self):
        """dict: Info about the initial dump file"""
        if self.__initial_dump is None:
            raise ValueError('No results yet!')
        return self.__initial_dump

    @property
    def final_dump(self):
        """dict: Info about the final dump file"""
        if self.__final_dump is None:
            raise ValueError('No results yet!')
        return self.__final_dump
    
    @property
    def final_box(self):
        """atomman.Box: Relaxed unit cell box"""
        if self.__final_box is None:
            raise ValueError('No results yet!')
        return self.__final_box

    @property
    def potential_energy(self):
        """float: Potential energy per atom for the relaxed system"""
        if self.__potential_energy is None:
            raise ValueError('No results yet!')
        return self.__potential_energy

    @property
    def measured_pressure_xx(self):
        """float: Measured relaxation pressure component xx"""
        if self.__measured_pressure_xx is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xx
    
    @property
    def measured_pressure_yy(self):
        """float: Measured relaxation pressure component yy"""
        if self.__measured_pressure_yy is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yy
    
    @property
    def measured_pressure_zz(self):
        """float: Measured relaxation pressure component zz"""
        if self.__measured_pressure_zz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_zz
    
    @property
    def measured_pressure_xy(self):
        """float: Measured relaxation pressure component xy"""
        if self.__measured_pressure_xy is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xy
    
    @property
    def measured_pressure_xz(self):
        """float: Measured relaxation pressure component xz"""
        if self.__measured_pressure_xz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xz
    
    @property
    def measured_pressure_yz(self):
        """float: Measured relaxation pressure component yz"""
        if self.__measured_pressure_yz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yz

    def set_values(self, name=None, **kwargs):
        """Used to set initial common values for the calculation."""
        
        # Set universal content
        super().set_values(name=None, **kwargs)

        # Set subset values
        self.units.set_values(**kwargs)
        self.potential.set_values(**kwargs)
        self.commands.set_values(**kwargs)
        self.system.set_values(**kwargs)
        self.system_mods.set_values(**kwargs)
        self.minimize.set_values(**kwargs)

        # Set calculation-specific values
        if 'pressure_xx' in kwargs:
            self.pressure_xx = kwargs['pressure_xx']
        if 'pressure_yy' in kwargs:
            self.pressure_yy = kwargs['pressure_yy']
        if 'pressure_zz' in kwargs:
            self.pressure_zz = kwargs['pressure_zz']
        if 'pressure_xy' in kwargs:
            self.pressure_xy = kwargs['pressure_xy']
        if 'pressure_xz' in kwargs:
            self.pressure_xz = kwargs['pressure_xz']
        if 'pressure_yz' in kwargs:
            self.pressure_yz = kwargs['pressure_yz']
        if 'displacementkick' in kwargs:
            self.displacementkick = kwargs['displacementkick']
        if 'maxcycles' in kwargs:
            self.maxcycles = kwargs['maxcycles']
        if 'cycletolerance' in kwargs:
            self.cycletolerance = kwargs['cycletolerance']

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Load universal content
        input_dict = super().load_parameters(params, key=key)
        
        # Load input/output units
        self.units.load_parameters(input_dict)
        
        # Change default values for subset terms
        input_dict['sizemults'] = input_dict.get('sizemults', '1 1 1')
        input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')

        # Load calculation-specific strings

        # Load calculation-specific booleans
        
        # Load calculation-specific integers
        self.maxcycles = int(input_dict.get('maxcycles', 100))

        # Load calculation-specific unitless floats
        self.cycletolerance = float(input_dict.get('cycletolerance', 1e-10))

        # Load calculation-specific floats with units
        self.pressure_xx = value(input_dict, 'pressure_xx',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_yy = value(input_dict, 'pressure_yy',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_zz = value(input_dict, 'pressure_zz',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_xy = value(input_dict, 'pressure_xy',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_xz = value(input_dict, 'pressure_xz',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.pressure_yz = value(input_dict, 'pressure_yz',
                                 default_unit=self.units.pressure_unit,
                                 default_term='0.0 GPa')
        self.displacementkick = value(input_dict, 'displacementkick',
                                 default_unit=self.units.length_unit,
                                 default_term='0.0 angstrom')
        
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
            params['buildcombos'] = [
                'atomicreference load_file reference',
                'atomicparent load_file parent'
            ]
            params['parent_record'] = 'calculation_E_vs_r_scan'
            params['parent_load_key'] = 'minimum-atomic-system'
            params['parent_status'] = 'finished'
            params['sizemults'] = '10 10 10'
            params['energytolerance'] = '0.0'
            params['forcetolerance'] = '1e-10 eV/angstrom'
            params['maxiterations'] = '10000'
            params['maxevaluations'] = '100000'
            params['maxatommotion'] = '0.01 angstrom'
            params['maxcycles'] = '100'
            params['cycletolerance'] = '1e-10'

            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'reference_{key}'] = kwargs[key]
                    params[f'parent_{key}'] = kwargs[key]
                
                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        elif branch == 'from_dynamic':

            # Check for required kwargs
            assert 'lammps_command' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'atomicarchive load_file archive'
            
            params['archive_record'] = 'calculation_relax_dynamic'
            params['archive_branch'] = 'main'
            params['archive_load_key'] = 'final-system'
            params['archive_status'] = 'finished'
            params['sizemults'] = '1 1 1'
            params['energytolerance'] = '0.0'
            params['forcetolerance'] = '1e-10 eV/angstrom'
            params['maxiterations'] = '10000'
            params['maxevaluations'] = '100000'
            params['maxatommotion'] = '0.01 angstrom'
            params['maxcycles'] = '100'
            params['cycletolerance'] = '1e-10'

            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'archive_{key}'] = kwargs[key]
                
                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        else:
            raise ValueError(f'Unknown branch {branch}')

        return params

    @property
    def template(self):
        """
        str: The template to use for generating calc.in files.
        """
        # Build universal content
        template = super().template

        # Build subset content
        template += self.commands.template()
        template += self.potential.template()
        template += self.system.template()
        template += self.system_mods.template()
        template += self.minimize.template()
        template += self.units.template()

        # Build calculation-specific content
        header = 'Run parameters'
        keys = ['pressure_xx', 'pressure_yy', 'pressure_zz',
                'pressure_xy', 'pressure_xz', 'pressure_yz',
                'displacementkick', 'maxcycles', 'cycletolerance']
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
            self.system_mods.keyset,
            [
                'pressure_xx',
                'pressure_yy',
                'pressure_zz',
                'pressure_xy',
                'pressure_xz',
                'pressure_yz',
            ],
            self.minimize.keyset + [
                'displacementkick',
                'maxcycles',
                'cycletolerance',
            ],
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
        self.system_mods.build_model(calc)
        self.minimize.build_model(calc)

        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(0.0, 'K')
        calc['phase-state']['pressure-xx'] = uc.model(self.pressure_xx,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-yy'] = uc.model(self.pressure_yy,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-zz'] = uc.model(self.pressure_zz,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-xy'] = uc.model(self.pressure_xy,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-xz'] = uc.model(self.pressure_xz,
                                                      self.units.pressure_unit)
        calc['phase-state']['pressure-yz'] = uc.model(self.pressure_yz,
                                                      self.units.pressure_unit)

        # Build results
        if self.status == 'finished':
            # Save info on initial and final configuration files
            calc['initial-system'] = DM()
            calc['initial-system']['artifact'] = DM()
            calc['initial-system']['artifact']['file'] = self.initial_dump['filename']
            calc['initial-system']['artifact']['format'] = 'atom_dump'
            calc['initial-system']['symbols'] = self.initial_dump['symbols']
            
            calc['final-system'] = DM()
            calc['final-system']['artifact'] = DM()
            calc['final-system']['artifact']['file'] = self.final_dump['filename']
            calc['final-system']['artifact']['format'] = 'atom_dump'
            calc['final-system']['symbols'] = self.final_dump['symbols']
            
            # Save measured box parameter info
            calc['measured-box-parameter'] = mbp = DM()            
            mbp['lx'] = uc.model(self.final_box.lx, self.units.length_unit)
            mbp['ly'] = uc.model(self.final_box.ly, self.units.length_unit)
            mbp['lz'] = uc.model(self.final_box.lz, self.units.length_unit)
            mbp['xy'] = uc.model(self.final_box.xy, self.units.length_unit)
            mbp['xz'] = uc.model(self.final_box.xz, self.units.length_unit)
            mbp['yz'] = uc.model(self.final_box.yz, self.units.length_unit)
            
            # Save measured phase-state info
            calc['measured-phase-state'] = mps = DM()
            mps['temperature'] = uc.model(0.0, 'K')
            mps['pressure-xx'] = uc.model(self.measured_pressure_xx,
                                          self.units.pressure_unit)
            mps['pressure-yy'] = uc.model(self.measured_pressure_yy,
                                          self.units.pressure_unit)
            mps['pressure-zz'] = uc.model(self.measured_pressure_zz,
                                          self.units.pressure_unit)
            mps['pressure-xy'] = uc.model(self.measured_pressure_xy,
                                          self.units.pressure_unit)
            mps['pressure-xz'] = uc.model(self.measured_pressure_xz,
                                          self.units.pressure_unit)
            mps['pressure-yz'] = uc.model(self.measured_pressure_yz,
                                          self.units.pressure_unit)
            
            # Save the final cohesive energy
            calc['cohesive-energy'] = uc.model(self.potential_energy,
                                               self.units.energy_unit,
                                               None)

        self._set_model(model)
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
        self.system_mods.load_model(calc)
        self.minimize.load_model(calc)

        # Load phase-state info
        self.pressure_xx = uc.value_unit(calc['phase-state']['pressure-xx'])
        self.pressure_yy = uc.value_unit(calc['phase-state']['pressure-yy'])
        self.pressure_zz = uc.value_unit(calc['phase-state']['pressure-zz'])
        self.pressure_xy = uc.value_unit(calc['phase-state']['pressure-xy'])
        self.pressure_xz = uc.value_unit(calc['phase-state']['pressure-xz'])
        self.pressure_yz = uc.value_unit(calc['phase-state']['pressure-yz'])

        # Load results
        if self.status == 'finished':
            self.__initial_dump = {
                'filename': calc['initial-system']['artifact']['file'],
                'symbols': calc['initial-system']['symbols']
            }
            

            self.__final_dump = {
                'filename': calc['final-system']['artifact']['file'],
                'symbols': calc['final-system']['symbols']
            }

            lx = uc.value_unit(calc['measured-box-parameter']['lx'])
            ly = uc.value_unit(calc['measured-box-parameter']['ly'])
            lz = uc.value_unit(calc['measured-box-parameter']['lz'])
            xy = uc.value_unit(calc['measured-box-parameter']['xy'])
            xz = uc.value_unit(calc['measured-box-parameter']['xz'])
            yz = uc.value_unit(calc['measured-box-parameter']['yz'])
            self.__final_box = am.Box(lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz)

            self.__potential_energy = uc.value_unit(calc['cohesive-energy'])
            
            mps = calc['measured-phase-state']
            self.__measured_pressure_xx = uc.value_unit(mps['pressure-xx'])
            self.__measured_pressure_yy = uc.value_unit(mps['pressure-yy'])
            self.__measured_pressure_zz = uc.value_unit(mps['pressure-zz'])
            self.__measured_pressure_xy = uc.value_unit(mps['pressure-xy'])
            self.__measured_pressure_xz = uc.value_unit(mps['pressure-xz'])
            self.__measured_pressure_yz = uc.value_unit(mps['pressure-yz'])

    @staticmethod
    def mongoquery(name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None, lammps_version=None,
                   potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                   potential_key=None, potential_id=None, 
                   ):
        
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
                  ):
        
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
        self.system_mods.metadata(meta)
        self.minimize.metadata(meta)

        # Extract calculation-specific content
        meta['temperature'] = 0.0
        meta['pressure_xx'] = self.pressure_xx
        meta['pressure_yy'] = self.pressure_yy
        meta['pressure_zz'] = self.pressure_zz
        meta['pressure_xy'] = self.pressure_xy
        meta['pressure_xz'] = self.pressure_xz
        meta['pressure_yz'] = self.pressure_yz
        
        # Extract results
        if self.status == 'finished':
            meta['lx'] = self.final_box.lx
            meta['ly'] = self.final_box.ly
            meta['lz'] = self.final_box.lz
            meta['xy'] = self.final_box.xy
            meta['xz'] = self.final_box.xz
            meta['yz'] = self.final_box.yz
            
            meta['E_pot'] = self.potential_energy
            meta['measured_temperature'] = 0.0
            meta['measured_pressure_xx'] = self.measured_pressure_xx
            meta['measured_pressure_yy'] = self.measured_pressure_yy
            meta['measured_pressure_zz'] = self.measured_pressure_zz
            meta['measured_pressure_xy'] = self.measured_pressure_xy
            meta['measured_pressure_xz'] = self.measured_pressure_xz
            meta['measured_pressure_yz'] = self.measured_pressure_yz

        return meta

    @property
    def compare_terms(self):
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',
        
            'parent_key',
            'load_options',
            'symbols',
            
            'potential_LAMMPS_key',
            
            'a_mult',
            'b_mult',
            'c_mult',
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'temperature':1e-2,
            'pressure_xx':1e-2,
            'pressure_yy':1e-2,
            'pressure_zz':1e-2,
            'pressure_xy':1e-2,
            'pressure_xz':1e-2,
            'pressure_yz':1e-2,
        }

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, iprPy_version=None,
                     atomman_version=None, script=None, branch=None,
                     status=None, lammps_version=None,
                     potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                     potential_key=None, potential_id=None, 
                     ):
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
        #self.system.calc_inputs(input_dict)
        self.system_mods.calc_inputs(input_dict)
        self.minimize.calc_inputs(input_dict)

        # Remove unused subset inputs
        del input_dict['transform']

        # Add calculation-specific inputs
        input_dict['p_xx'] = self.pressure_xx
        input_dict['p_yy'] = self.pressure_yy
        input_dict['p_zz'] = self.pressure_zz
        input_dict['p_xy'] = self.pressure_xy
        input_dict['p_xz'] = self.pressure_xz
        input_dict['p_yz'] = self.pressure_yz
        input_dict['dispmult'] = self.displacementkick
        input_dict['maxcycles'] = self.maxcycles
        input_dict['ctol'] = self.cycletolerance

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
        self.__initial_dump = {
            'filename': results_dict['dumpfile_initial'],
            'symbols': results_dict['symbols_initial']
        }
        self.__final_dump = {
            'filename': results_dict['dumpfile_final'],
            'symbols': results_dict['symbols_final']
        }
        lx = results_dict['lx'] / (self.system_mods.a_mults[1] - self.system_mods.a_mults[0])
        ly = results_dict['ly'] / (self.system_mods.b_mults[1] - self.system_mods.b_mults[0])
        lz = results_dict['lz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        xy = results_dict['xy'] / (self.system_mods.b_mults[1] - self.system_mods.b_mults[0])
        xz = results_dict['xz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        yz = results_dict['yz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        self.__final_box = am.Box(lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz)
        self.__potential_energy = results_dict['E_pot']
        self.__measured_pressure_xx = results_dict['measured_pxx']
        self.__measured_pressure_yy = results_dict['measured_pyy']
        self.__measured_pressure_zz = results_dict['measured_pzz']
        self.__measured_pressure_xy = results_dict['measured_pxy']
        self.__measured_pressure_xz = results_dict['measured_pxz']
        self.__measured_pressure_yz = results_dict['measured_pyz']