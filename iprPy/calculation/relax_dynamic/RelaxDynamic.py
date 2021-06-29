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
from .relax_dynamic import relax_dynamic
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

# Global class properties
modelroot = 'calculation-relax-dynamic'

class RelaxDynamic(Calculation):
    """Class for managing dynamic relaxations"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""
        
        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        self.__system_mods = AtommanSystemManipulate(self)

        # Initialize unique calculation attributes
        self.pressure_xx = 0.0
        self.pressure_yy = 0.0
        self.pressure_zz = 0.0
        self.pressure_xy = 0.0
        self.pressure_xz = 0.0
        self.pressure_yz = 0.0
        self.temperature = 0.0
        self.integrator = None
        self.thermosteps = 100
        self.dumpsteps = None
        self.runsteps = 220000
        self.equilsteps = 20000
        self.randomseed = None
        
        self.__initial_dump = None
        self.__final_dump = None
        self.__final_box = None
        self.__lx_std = None
        self.__ly_std = None
        self.__lz_std = None
        self.__xy_std = None
        self.__xz_std = None
        self.__yz_std = None
        self.__numsamples = None
        self.__potential_energy = None
        self.__potential_energy_std = None
        self.__total_energy = None
        self.__total_energy_std = None
        self.__measured_pressure_xx = None
        self.__measured_pressure_xx_std = None
        self.__measured_pressure_yy = None
        self.__measured_pressure_yy_std = None
        self.__measured_pressure_zz = None
        self.__measured_pressure_zz_std = None
        self.__measured_pressure_xy = None
        self.__measured_pressure_xy_std = None
        self.__measured_pressure_xz = None
        self.__measured_pressure_xz_std = None
        self.__measured_pressure_yz = None
        self.__measured_pressure_yz_std = None
        self.__measured_temperature = None
        self.__measured_temperature_std = None

        # Define calc shortcut
        self.calc = relax_dynamic

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
    def temperature(self):
        """float: Target relaxation temperature"""
        return self.__temperature

    @temperature.setter
    def temperature(self, value):
        value = float(value)
        assert value >= 0.0
        self.__temperature = value

    @property
    def integrator(self):
        """str: MD integration scheme"""
        return self.__integrator

    @integrator.setter
    def integrator(self, value):
        if value is None:
            if self.temperature == 0.0:
                value = 'nph+l'
            else:
                value = 'npt'
        self.__integrator = str(value)

    @property
    def thermosteps(self):
        return self.__thermosteps

    @thermosteps.setter
    def thermosteps(self, value):
        value = int(value)
        assert value >= 0
        self.__thermosteps = value

    @property
    def dumpsteps(self):
        if self.__dumpsteps is None:
            return self.runsteps
        else:
            return self.__dumpsteps

    @dumpsteps.setter
    def dumpsteps(self, value):
        if value is None:
            self.__dumpsteps = None
        else:
            value = int(value)
            assert value >= 0
            self.__dumpsteps = value

    @property
    def runsteps(self):
        return self.__runsteps

    @runsteps.setter
    def runsteps(self, value):
        value = int(value)
        assert value >= 0
        self.__runsteps = value

    @property
    def equilsteps(self):
        return self.__equilsteps

    @equilsteps.setter
    def equilsteps(self, value):
        value = int(value)
        assert value >= 0
        self.__equilsteps = value

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
    def lx_std(self):
        """float: Standard deviation for final_box's lx length"""
        if self.__lx_std is None:
            raise ValueError('No results yet!')
        return self.__lx_std

    @property
    def ly_std(self):
        """float: Standard deviation for final_box's ly length"""
        if self.__ly_std is None:
            raise ValueError('No results yet!')
        return self.__ly_std
    
    @property
    def lz_std(self):
        """float: Standard deviation for final_box's lz length"""
        if self.__lz_std is None:
            raise ValueError('No results yet!')
        return self.__lz_std

    @property
    def xy_std(self):
        """float: Standard deviation for final_box's xy tilt"""
        if self.__xy_std is None:
            raise ValueError('No results yet!')
        return self.__xy_std

    @property
    def xz_std(self):
        """float: Standard deviation for final_box's xz tilt"""
        if self.__xz_std is None:
            raise ValueError('No results yet!')
        return self.__xz_std

    @property
    def yz_std(self):
        """float: Standard deviation for final_box's yz tilt"""
        if self.__yz_std is None:
            raise ValueError('No results yet!')
        return self.__yz_std

    @property
    def numsamples(self):
        """int: Number of measurement samples used in mean, std values"""
        if self.__numsamples is None:
            raise ValueError('No results yet!')
        return self.__numsamples

    @property
    def potential_energy(self):
        """float: Potential energy per atom for the relaxed system"""
        if self.__potential_energy is None:
            raise ValueError('No results yet!')
        return self.__potential_energy

    @property
    def potential_energy_std(self):
        """float: Standard deviation for potential_energy"""
        if self.__potential_energy_std is None:
            raise ValueError('No results yet!')
        return self.__potential_energy_std

    @property
    def total_energy(self):
        """float: Total energy per atom for the relaxed system"""
        if self.__total_energy is None:
            raise ValueError('No results yet!')
        return self.__total_energy

    @property
    def total_energy_std(self):
        """float: Standard deviation for total_energy"""
        if self.__total_energy_std is None:
            raise ValueError('No results yet!')
        return self.__total_energy_std

    @property
    def measured_pressure_xx(self):
        """float: Measured relaxation pressure component xx"""
        if self.__measured_pressure_xx is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xx
    
    @property
    def measured_pressure_xx_std(self):
        """float: Standard deviation for measured_pressure_xx"""
        if self.__measured_pressure_xx_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xx_std

    @property
    def measured_pressure_yy(self):
        """float: Measured relaxation pressure component yy"""
        if self.__measured_pressure_yy is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yy
    
    @property
    def measured_pressure_yy_std(self):
        """float: Standard deviation for measured_pressure_yy"""
        if self.__measured_pressure_yy_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yy_std

    @property
    def measured_pressure_zz(self):
        """float: Measured relaxation pressure component zz"""
        if self.__measured_pressure_zz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_zz
    
    @property
    def measured_pressure_zz_std(self):
        """float: Standard deviation for measured_pressure_zz"""
        if self.__measured_pressure_zz_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_zz_std

    @property
    def measured_pressure_xy(self):
        """float: Measured relaxation pressure component xy"""
        if self.__measured_pressure_xy is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xy
    
    @property
    def measured_pressure_xy_std(self):
        """float: Standard deviation for measured_pressure_xy"""
        if self.__measured_pressure_xy_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xy_std

    @property
    def measured_pressure_xz(self):
        """float: Measured relaxation pressure component xz"""
        if self.__measured_pressure_xz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xz
    
    @property
    def measured_pressure_xz_std(self):
        """float: Standard deviation for measured_pressure_xz"""
        if self.__measured_pressure_xz_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xz_std

    @property
    def measured_pressure_yz(self):
        """float: Measured relaxation pressure component yz"""
        if self.__measured_pressure_yz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yz

    @property
    def measured_pressure_yz_std(self):
        """float: Standard deviation for measured_pressure_yz"""
        if self.__measured_pressure_yz_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yz_std

    @property
    def measured_temperature(self):
        """float: Measured temperature for the relaxed system"""
        if self.__measured_temperature is None:
            raise ValueError('No results yet!')
        return self.__measured_temperature

    @property
    def measured_temperature_std(self):
        """float: Standard deviation for measured_temperature"""
        if self.__measured_temperature_std is None:
            raise ValueError('No results yet!')
        return self.__measured_temperature_std

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
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
        if 'integrator' in kwargs:
            self.integrator = kwargs['integrator']
        if 'thermosteps' in kwargs:
            self.thermosteps = kwargs['thermosteps']
        if 'dumpsteps' in kwargs:
            self.dumpsteps = kwargs['dumpsteps']
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'equilsteps' in kwargs:
            self.equilsteps = kwargs['equilsteps']
        if 'randomseed' in kwargs:
            self.randomseed = kwargs['randomseed']

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Load universal content
        input_dict = super().load_parameters(params, key=key)
        
        # Load input/output units
        self.units.load_parameters(input_dict)
        
        # Change default values for subset terms
        input_dict['sizemults'] = input_dict.get('sizemults', '10 10 10')
        
        # Load calculation-specific strings
        self.integrator = input_dict.get('integrator', None)

        # Load calculation-specific booleans
        
        # Load calculation-specific integers
        self.runsteps = int(input_dict.get('runsteps', 220000))
        self.thermosteps = int(input_dict.get('thermosteps', 100))
        self.dumpsteps = input_dict.get('dumpsteps', None)
        self.equilsteps = int(input_dict.get('equilsteps', 20000))
        if self.equilsteps >= self.runsteps:
            raise ValueError('runsteps must be greater than equilsteps')
        self.randomseed = input_dict.get('randomseed', None)

        # Load calculation-specific unitless floats
        self.temperature = float(input_dict.get('temperature', 0.0))

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
            params['buildcombos'] = [
                'atomicreference load_file reference',
                'atomicparent load_file parent'
            ]
            params['parent_record'] = 'calculation_E_vs_r_scan'
            params['parent_load_key'] = 'minimum-atomic-system'
            params['parent_status'] = 'finished'
            params['sizemults'] = '10 10 10'
            params['temperature'] = '0.0'
            params['integrator'] = 'nph+l'
            params['thermosteps'] = '1000'
            params['runsteps'] = '10000'
            params['equilsteps'] = '0'


            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'reference_{key}'] = kwargs[key]
                    params[f'parent_{key}'] = kwargs[key]
                
                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]
        
        elif branch == 'at_temp':
            
            # Check for required kwargs
            assert 'lammps_command' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'atomicparent load_file parent'
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['sizemults'] = '10 10 10'
            params['temperature'] = [
                '100', '200', '300', '400', '500', '600', '700', '800', '900','1000',
                '1100','1200','1300','1400','1500','1600','1700','1800','1900','2000',
                '2100','2200','2300','2400','2500','2600','2700','2800','2900','3000',
            ]
            params['integrator'] = 'npt'
            params['thermosteps'] = '100'
            params['runsteps'] = '220000'
            params['equilsteps'] = '20000'
            
            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    if key != 'potential_pair_style':
                        params[f'parent_{key}'] = kwargs[key]
                
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
        template += self.units.template()

        # Build calculation-specific content
        header = 'Run parameters'
        keys = ['temperature', 'pressure_xx', 'pressure_yy', 'pressure_zz',
                'pressure_xy', 'pressure_xz', 'pressure_yz', 'integrator',
                'thermosteps', 'dumpsteps', 'runsteps', 'equilsteps',
                'randomseed']
        template += self._template_builder(header, keys)
        
        return template     

    @property
    def singularkeys(self):
        """list: Calculation keys that can have single values during prepare."""
        # Fetch universal key sets from parent
        universalkeys = super().singularkeys
        
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
        """
        list: Calculation key sets that can have multiple values during prepare.
        """
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
            [
                'temperature',
            ],
            [
                'integrator',
                'thermosteps',
                'dumpsteps',
                'runsteps',
                'equilsteps',
                'randomseed',
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

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']
        
        run_params['integrator'] = self.integrator
        run_params['thermosteps'] = self.thermosteps
        run_params['dumpsteps'] = self.dumpsteps
        run_params['runsteps'] = self.runsteps
        run_params['equilsteps'] = self.equilsteps
        run_params['randomseed'] = self.randomseed

        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(self.temperature, 'K')
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
            
            calc['number-of-measurements'] = self.numsamples

            # Save measured box parameter info
            calc['measured-box-parameter'] = mbp = DM()            
            mbp['lx'] = uc.model(self.final_box.lx, self.units.length_unit,
                                 self.lx_std)
            mbp['ly'] = uc.model(self.final_box.ly, self.units.length_unit,
                                 self.ly_std)
            mbp['lz'] = uc.model(self.final_box.lz, self.units.length_unit,
                                 self.lz_std)
            mbp['xy'] = uc.model(self.final_box.xy, self.units.length_unit,
                                 self.xy_std)
            mbp['xz'] = uc.model(self.final_box.xz, self.units.length_unit,
                                 self.xz_std)
            mbp['yz'] = uc.model(self.final_box.yz, self.units.length_unit,
                                 self.yz_std)
            
            # Save measured phase-state info
            calc['measured-phase-state'] = mps = DM()
            mps['temperature'] = uc.model(self.measured_temperature, 'K',
                                          self.measured_temperature_std)
            mps['pressure-xx'] = uc.model(self.measured_pressure_xx,
                                          self.units.pressure_unit,
                                          self.measured_pressure_xx_std)
            mps['pressure-yy'] = uc.model(self.measured_pressure_yy,
                                          self.units.pressure_unit,
                                          self.measured_pressure_yy_std)
            mps['pressure-zz'] = uc.model(self.measured_pressure_zz,
                                          self.units.pressure_unit,
                                          self.measured_pressure_zz_std)
            mps['pressure-xy'] = uc.model(self.measured_pressure_xy,
                                          self.units.pressure_unit,
                                          self.measured_pressure_xy_std)
            mps['pressure-xz'] = uc.model(self.measured_pressure_xz,
                                          self.units.pressure_unit,
                                          self.measured_pressure_xz_std)
            mps['pressure-yz'] = uc.model(self.measured_pressure_yz,
                                          self.units.pressure_unit,
                                          self.measured_pressure_yz_std)
            
            # Save the final cohesive and total energies
            calc['cohesive-energy'] = uc.model(self.potential_energy,
                                               self.units.energy_unit,
                                               self.potential_energy_std)
            calc['average-total-energy'] = uc.model(self.total_energy,
                                               self.units.energy_unit,
                                               self.total_energy_std)

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

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.integrator = run_params['integrator']
        self.thermosteps = run_params['thermosteps']
        self.dumpsteps = run_params['dumpsteps']
        self.runsteps = run_params['runsteps']
        self.equilsteps = run_params['equilsteps']
        self.randomseed = run_params['randomseed']

        # Load phase-state info
        self.temperature = uc.value_unit(calc['phase-state']['temperature'])
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

            self.__numsamples = calc['number-of-measurements']

            lx = uc.value_unit(calc['measured-box-parameter']['lx'])
            self.__lx_std = uc.error_unit(calc['measured-box-parameter']['lx'])
            ly = uc.value_unit(calc['measured-box-parameter']['ly'])
            self.__ly_std = uc.error_unit(calc['measured-box-parameter']['ly'])
            lz = uc.value_unit(calc['measured-box-parameter']['lz'])
            self.__lz_std = uc.error_unit(calc['measured-box-parameter']['lz'])
            xy = uc.value_unit(calc['measured-box-parameter']['xy'])
            self.__xy_std = uc.error_unit(calc['measured-box-parameter']['xy'])
            xz = uc.value_unit(calc['measured-box-parameter']['xz'])
            self.__xz_std = uc.error_unit(calc['measured-box-parameter']['xz'])
            yz = uc.value_unit(calc['measured-box-parameter']['yz'])
            self.__yz_std = uc.error_unit(calc['measured-box-parameter']['yz'])
            self.__final_box = am.Box(lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz)

            self.__potential_energy = uc.value_unit(calc['cohesive-energy'])
            self.__potential_energy_std = uc.error_unit(calc['cohesive-energy'])
            self.__total_energy = uc.value_unit(calc['average-total-energy'])
            self.__total_energy_std = uc.error_unit(calc['average-total-energy'])
            
            mps = calc['measured-phase-state']
            self.__measured_temperature = uc.value_unit(mps['temperature'])
            self.__measured_temperature_std = uc.error_unit(mps['temperature'])
            self.__measured_pressure_xx = uc.value_unit(mps['pressure-xx'])
            self.__measured_pressure_xx_std = uc.error_unit(mps['pressure-xx'])
            self.__measured_pressure_yy = uc.value_unit(mps['pressure-yy'])
            self.__measured_pressure_yy_std = uc.error_unit(mps['pressure-yy'])
            self.__measured_pressure_zz = uc.value_unit(mps['pressure-zz'])
            self.__measured_pressure_zz_std = uc.error_unit(mps['pressure-zz'])
            self.__measured_pressure_xy = uc.value_unit(mps['pressure-xy'])
            self.__measured_pressure_xy_std = uc.error_unit(mps['pressure-xy'])
            self.__measured_pressure_xz = uc.value_unit(mps['pressure-xz'])
            self.__measured_pressure_xz_std = uc.error_unit(mps['pressure-xz'])
            self.__measured_pressure_yz = uc.value_unit(mps['pressure-yz'])
            self.__measured_pressure_yz_std = uc.error_unit(mps['pressure-yz'])

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

        # Extract calculation-specific content
        meta['temperature'] = self.temperature
        meta['pressure_xx'] = self.pressure_xx
        meta['pressure_yy'] = self.pressure_yy
        meta['pressure_zz'] = self.pressure_zz
        meta['pressure_xy'] = self.pressure_xy
        meta['pressure_xz'] = self.pressure_xz
        meta['pressure_yz'] = self.pressure_yz
        
        # Extract results
        if self.status == 'finished':
            meta['numsamples'] = self.numsamples

            meta['lx'] = self.final_box.lx
            meta['lx_std'] = self.lx_std
            meta['ly'] = self.final_box.ly
            meta['ly_std'] = self.ly_std
            meta['lz'] = self.final_box.lz
            meta['lz_std'] = self.lz_std
            meta['xy'] = self.final_box.xy
            meta['xy_std'] = self.xy_std
            meta['xz'] = self.final_box.xz
            meta['xz_std'] = self.xz_std
            meta['yz'] = self.final_box.yz
            meta['yz_std'] = self.yz_std
            
            meta['E_pot'] = self.potential_energy
            meta['E_pot_std'] = self.potential_energy_std
            meta['E_total'] = self.total_energy
            meta['E_total_std'] = self.total_energy_std
            meta['measured_temperature'] = self.measured_temperature
            meta['measured_temperature_std'] = self.measured_temperature_std
            meta['measured_pressure_xx'] = self.measured_pressure_xx
            meta['measured_pressure_xx_std'] = self.measured_pressure_xx_std
            meta['measured_pressure_yy'] = self.measured_pressure_yy
            meta['measured_pressure_yy_std'] = self.measured_pressure_yy_std
            meta['measured_pressure_zz'] = self.measured_pressure_zz
            meta['measured_pressure_zz_std'] = self.measured_pressure_zz_std
            meta['measured_pressure_xy'] = self.measured_pressure_xy
            meta['measured_pressure_xy_std'] = self.measured_pressure_xy_std
            meta['measured_pressure_xz'] = self.measured_pressure_xz
            meta['measured_pressure_xz_std'] = self.measured_pressure_xz_std
            meta['measured_pressure_yz'] = self.measured_pressure_yz
            meta['measured_pressure_yz_std'] = self.measured_pressure_yz_std

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

        # Remove unused subset inputs
        del input_dict['transform']

        # Add calculation-specific inputs
        input_dict['p_xx'] = self.pressure_xx
        input_dict['p_yy'] = self.pressure_yy
        input_dict['p_zz'] = self.pressure_zz
        input_dict['p_xy'] = self.pressure_xy
        input_dict['p_xz'] = self.pressure_xz
        input_dict['p_yz'] = self.pressure_yz
        input_dict['temperature'] = self.temperature
        input_dict['runsteps'] = self.runsteps
        input_dict['integrator'] = self.integrator
        input_dict['thermosteps'] = self.thermosteps
        input_dict['dumpsteps'] = self.dumpsteps
        input_dict['equilsteps'] = self.equilsteps
        input_dict['randomseed'] = self.randomseed

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
            self.__initial_dump = {
                'filename': results_dict['dumpfile_initial'],
                'symbols': results_dict['symbols_initial']
            }
            self.__final_dump = {
                'filename': results_dict['dumpfile_final'],
                'symbols': results_dict['symbols_final']
            }
            self.__numsamples = results_dict['nsamples']
            lx = results_dict['lx'] / (self.system_mods.a_mults[1] - self.system_mods.a_mults[0])
            ly = results_dict['ly'] / (self.system_mods.b_mults[1] - self.system_mods.b_mults[0])
            lz = results_dict['lz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
            xy = results_dict['xy'] / (self.system_mods.b_mults[1] - self.system_mods.b_mults[0])
            xz = results_dict['xz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
            yz = results_dict['yz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
            self.__final_box = am.Box(lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz)
            
            self.__lx_std = results_dict['lx_std']
            self.__ly_std = results_dict['ly_std']
            self.__lz_std = results_dict['lz_std']
            self.__xy_std = results_dict['xy_std']
            self.__xz_std = results_dict['xz_std']
            self.__yz_std = results_dict['yz_std']
            
            self.__potential_energy = results_dict['E_pot']
            self.__potential_energy_std = results_dict['E_pot_std']
            self.__total_energy = results_dict['E_total']
            self.__total_energy_std = results_dict['E_total_std']

            self.__measured_pressure_xx = results_dict['measured_pxx']
            self.__measured_pressure_xx_std = results_dict['measured_pxx_std']
            self.__measured_pressure_yy = results_dict['measured_pyy']
            self.__measured_pressure_yy_std = results_dict['measured_pyy_std']
            self.__measured_pressure_zz = results_dict['measured_pzz']
            self.__measured_pressure_zz_std = results_dict['measured_pzz_std']
            self.__measured_pressure_xy = results_dict['measured_pxy']
            self.__measured_pressure_xy_std = results_dict['measured_pxy_std']
            self.__measured_pressure_xz = results_dict['measured_pxz']
            self.__measured_pressure_xz_std = results_dict['measured_pxz_std']
            self.__measured_pressure_yz = results_dict['measured_pyz']
            self.__measured_pressure_yz_std = results_dict['measured_pyz_std']

            self.__measured_temperature = results_dict['temp']
            self.__measured_temperature_std = results_dict['temp_std']
        
        self._results(json=results_json)