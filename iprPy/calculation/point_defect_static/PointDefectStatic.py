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
from .point_defect_static import calc
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

# Global class properties
modelroot = 'calculation-point-defect-static'

class PointDefectStatic(Calculation):
    """Class for managing point defect formation calculations"""

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
        self.__defect = PointDefect(self)

        # Initialize unique calculation attributes        
        self.__system_base = None
        self.__system_defect = None
        self.__dumpfile_base = None
        self.__dumpfile_defect = None
        self.__symbols_base = None
        self.__symbols_defect = None
        self.__natoms_base = None
        self.__natoms_defect = None
        self.__potential_energy_base = None
        self.__potential_energy_defect = None
        self.__potential_energy = None
        self.__formation_energy = None
        self.__dipole_tensor = None
        self.__has_reconfigured = None
        self.__centrosummation = None
        self.__position_shift = None
        self.__db_vect_shift = None
        
        # Define calc shortcut
        self.calc = calc

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
    def defect(self):
        """PointDefect subset"""
        return self.__defect

    @property
    def dumpfile_base(self):
        """str: Name of the LAMMPS dump file of the base system"""
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
    def natoms_base(self):
        """int: Number of atoms in the base system"""
        if self.__natoms_base is None:
            raise ValueError('No results yet!')
        return self.__natoms_base
    
    @property
    def natoms_defect(self):
        """int: Number of atoms in the defect system"""
        if self.__natoms_defect is None:
            raise ValueError('No results yet!')
        return self.__natoms_defect

    @property
    def system_base(self):
        """atomman.System: The base system"""
        if self.__system_base is None:
            raise ValueError('System not set/loaded!')
        return self.__system_base
            
    @property
    def system_defect(self):
        """atomman.System: The defect system"""
        if self.__system_defect is None:
            raise ValueError('System not set/loaded!')
        return self.__system_defect

    @system_defect.setter
    def system_defect(self, value):
        if isinstance(value, am.System) or value is None:
            self.__system_defect = value
        else:
            raise ValueError('system_defect must be a System or None')

    @property
    def potential_energy_base(self):
        """float: Potential energy of the base system"""
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
    def potential_energy(self):
        """float: Potential energy per atom for the base system"""
        if self.__potential_energy is None:
            raise ValueError('No results yet!')
        return self.__potential_energy

    @property
    def formation_energy(self):
        """float: Point defect formation energy"""
        if self.__formation_energy is None:
            raise ValueError('No results yet!')
        return self.__formation_energy

    @property
    def dipole_tensor(self):
        """numpy.NDArray: The elastic dipole tensor for the point defect"""
        if self.__dipole_tensor is None:
            raise ValueError('No results yet!')
        return self.__dipole_tensor

    @property
    def has_reconfigured(self):
        """bool: Flag for if checks indicate the defect has reconfigured"""
        if self.__has_reconfigured is None:
            raise ValueError('No results yet!')
        return self.__has_reconfigured
        
    @property
    def centrosummation(self):
        """numpy.NDArray: sum of relative neighbor coordinates after relaxing"""
        if self.__centrosummation is None:
            raise ValueError('No results yet!')
        return self.__centrosummation
        
    @property
    def position_shift(self):
        """numpy.NDArray: shift in defect's position after relaxing"""
        if self.__position_shift is None:
            raise ValueError('Value not set!')
        return self.__position_shift
    
    @property
    def db_vect_shift(self):
        """numpy.NDArray: Change in dumbbell vector after relaxing"""
        if self.__db_vect_shift is None:
            raise ValueError('Value not set!')
        return self.__db_vect_shift

    def load_system_base(self):
        if self.__system_base is None:
            fname = self.dumpfile_base
            tar = self.database.get_tar(record=self)
            f = tar.extractfile(fname)
            self.__system_base = am.load('atom_dump', f, symbols=self.symbols_base)

    def load_system_defect(self):
        if self.__system_defect is None:
            fname = self.dumpfile_defect
            tar = self.database.get_tar(record=self)
            f = tar.extractfile(fname)
            self.__system_defect = am.load('atom_dump', f, symbols=self.symbols_defect)

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
        self.defect.set_values(**kwargs)

        # Set calculation-specific values

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Load universal content
        input_dict = super().load_parameters(params, key=key)
        
        # Load input/output units
        self.units.load_parameters(input_dict)
        
        # Change default values for subset terms
        input_dict['sizemults'] = input_dict.get('sizemults', '5 5 5')
        input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')

        # Load calculation-specific strings

        # Load calculation-specific booleans
        
        # Load calculation-specific integers

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
                'atomicparent load_file parent',
                'defect pointdefect_file'
            ]
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['defect_record'] = 'point_defect'
            params['sizemults'] = '12 12 12'
            params['forcetolerance'] = '1e-8'

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
        template += self.system_mods.template()
        template += self.defect.template()
        template += self.minimize.template()
        template += self.units.template()
        
        # Build calculation-specific content
        #header = 'Run parameters'
        #keys = []
        #template += self._template_builder(header, keys)
        
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
        """
        list: Calculation key sets that can have multiple values during prepare.
        """
        # Fetch universal key sets from parent
        universalkeys = super().multikeys
        
        # Specify calculation-specific key sets 
        keys =  [
            self.potential.keyset + self.system.keyset,
            self.system_mods.keyset,
            self.defect.keyset,
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
        self.system_mods.build_model(calc)
        self.defect.build_model(calc, after='system-info')
        self.minimize.build_model(calc)

        # Build results
        if self.status == 'finished':
            calc['defect-free-system'] = DM()
            calc['defect-free-system']['artifact'] = DM()
            calc['defect-free-system']['artifact']['file'] = self.dumpfile_base
            calc['defect-free-system']['artifact']['format'] = 'atom_dump'
            calc['defect-free-system']['symbols'] = self.symbols_base
            calc['defect-free-system']['potential-energy'] = uc.model(self.potential_energy_base, 
                                                                      self.units.energy_unit)
            
            calc['defect-system'] = DM()
            calc['defect-system']['artifact'] = DM()
            calc['defect-system']['artifact']['file'] = self.dumpfile_defect
            calc['defect-system']['artifact']['format'] = 'atom_dump'
            calc['defect-system']['symbols'] = self.symbols_defect
            calc['defect-system']['potential-energy'] = uc.model(self.potential_energy_defect,
                                                                 self.units.energy_unit)
            
            # Save the calculation results
            calc['cohesive-energy'] = uc.model(self.potential_energy,
                                               self.units.energy_unit)
            calc['number-of-atoms'] = self.natoms_defect
            calc['defect-formation-energy'] = uc.model(self.formation_energy,
                                                       self.units.energy_unit)
            calc['defect-elastic-dipole-tensor'] = uc.model(self.dipole_tensor,
                                                            self.units.energy_unit)
            
            # Save the reconfiguration checks
            calc['reconfiguration-check'] = r_c = DM()
            r_c['has_reconfigured'] = self.has_reconfigured
            r_c['centrosummation'] = self.centrosummation.tolist()
            if self.__position_shift is not None:
                r_c['position_shift'] = self.position_shift.tolist()
            if self.__db_vect_shift is not None:
                r_c['db_vect_shift'] = self.db_vect_shift.tolist()

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
        self.defect.load_model(calc)

        # Load results
        if self.status == 'finished':
            self.__dumpfile_base = calc['defect-free-system']['artifact']['file']
            self.__symbols_base = calc['defect-free-system']['symbols']
            self.__potential_energy_base = uc.value_unit(calc['defect-free-system']['potential-energy'])
            self.__natoms_base = None
            
            self.__dumpfile_defect= calc['defect-system']['artifact']['file']
            self.__symbols_defect = calc['defect-system']['symbols']
            self.__potential_energy_defect = uc.value_unit(calc['defect-system']['potential-energy'])
            self.__natoms_defect = calc['number-of-atoms']
            
            self.__potential_energy = uc.value_unit(calc['cohesive-energy'])
            self.__formation_energy = uc.value_unit(calc['defect-formation-energy'])
            self.__dipole_tensor = uc.value_unit(calc['defect-elastic-dipole-tensor'])
            
            # Save the reconfiguration checks
            r_c = calc['reconfiguration-check']
            self.__has_reconfigured = r_c['has_reconfigured']
            self.__centrosummation = np.array(r_c['centrosummation'])
            if 'position_shift' in r_c:
                self.__position_shift = np.array(r_c['position_shift'])
            else:
                self.__position_shift = None
            if 'db_vect_shift' in r_c:
                self.__db_vect_shift = np.array(r_c['db_vect_shift'])
            else:
                self.__db_vect_shift = None
            

    @staticmethod
    def mongoquery(name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None, lammps_version=None,
                   potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                   potential_key=None, potential_id=None, 
                   pointdefect_key=None, pointdefect_id=None):
        
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
        mquery.update(PointDefect.mongoquery(modelroot,
                                             pointdefect_key=pointdefect_key,
                                             pointdefect_id=pointdefect_id))

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
                  pointdefect_key=None, pointdefect_id=None):
        
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
        mquery.update(PointDefect.mongoquery(modelroot,
                                             pointdefect_key=pointdefect_key,
                                             pointdefect_id=pointdefect_id))

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
        self.defect.metadata(meta)

        # Extract calculation-specific content
        
        # Extract results
        if self.status == 'finished':            
            meta['dumpfile_base'] = self.dumpfile_base
            meta['dumpfile_defect'] = self.dumpfile_defect
            meta['E_pot_base'] = self.potential_energy_base
            meta['E_pot_defect'] = self.potential_energy_defect
            meta['E_pot'] = self.potential_energy
            meta['E_ptd_f'] = self.formation_energy
            meta['pij'] = self.dipole_tensor
            meta['has_reconfigured'] = self.has_reconfigured
            meta['centrosummation'] = self.centrosummation
            try:
                meta['position_shift'] = self.position_shift
            except:
                pass
            try:
                meta['db_vect_shift'] = self.db_vect_shift
            except:
                pass

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
            
            'pointdefect_key',
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
                     pointdefect_key=None, pointdefect_id=None):
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
            &PointDefect.pandasfilter(dataframe,
                                      pointdefect_key=pointdefect_key,
                                      pointdefect_id=pointdefect_id)

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
        self.system_mods.calc_inputs(input_dict)
        self.minimize.calc_inputs(input_dict)
        self.defect.calc_inputs(input_dict)

        # Modify inputs for calculation
        input_dict['cutoff'] = 1.05 * input_dict['ucell'].box.a
        del input_dict['ucell']
        del input_dict['transform']

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
            self.__dumpfile_defect = results_dict['dumpfile_ptd']
            self.__system_base = results_dict['system_base']
            self.__system_defect = results_dict['system_ptd']
            self.__symbols_base = results_dict['system_base'].symbols
            self.__symbols_defect = results_dict['system_ptd'].symbols
            self.__natoms_base = results_dict['system_base'].natoms
            self.__natoms_defect = results_dict['system_ptd'].natoms
            self.__potential_energy_base = results_dict['E_total_base']
            self.__potential_energy_defect = results_dict['E_total_ptd']
            self.__potential_energy = results_dict['E_coh']
            self.__formation_energy = results_dict['E_ptd_f']
            self.__dipole_tensor = results_dict['pij_tensor']
            self.__has_reconfigured = results_dict['has_reconfigured']
            self.__centrosummation = results_dict['centrosummation']
            self.__position_shift = results_dict.get('position_shift', None)
            self.__db_vect_shift = results_dict.get('db_vect_shift', None)

        self._results(json=results_json)