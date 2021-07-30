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
from .e_vs_r_scan import e_vs_r_scan
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

# Global class properties
modelroot = 'calculation-E-vs-r-scan'

class EvsRScan(Calculation):
    """Class for managing energy versus r volumetric scans for crystals"""

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
        self.number_of_steps_r = 201
        self.minimum_r = uc.set_in_units(2.0, 'angstrom')
        self.maximum_r = uc.set_in_units(6.0, 'angstrom')
        self.r_values = None
        self.a_values = None
        self.energy_values = None
        self.min_cells = None

        # Define calc shortcut
        self.calc = e_vs_r_scan

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
    def number_of_steps_r(self):
        return self.__number_of_steps_r

    @number_of_steps_r.setter
    def number_of_steps_r(self, value):
        value = int(value)
        assert value > 0
        self.__number_of_steps_r = value

    @property
    def minimum_r(self):
        return self.__minimum_r

    @minimum_r.setter
    def minimum_r(self, value):
        value = float(value)
        assert value > 0
        self.__minimum_r = value

    @property
    def maximum_r(self):
        return self.__maximum_r

    @maximum_r.setter
    def maximum_r(self, value):
        value = float(value)
        assert value > 0
        self.__maximum_r = value

    @property
    def r_values(self):
        """numpy.NDArray : Interatomic distances used for the scan."""
        if self.__r_values is None:
            raise ValueError('No results yet!')
        return self.__r_values

    @r_values.setter
    def r_values(self, value):
        if value is None:
            self.__r_values = value
        else:
            value = np.asarray(value, dtype=float)
            self.__r_values = value
            self.number_of_steps_r = len(value)
            self.minimum_r = value[0]
            self.maximum_r = value[-1]

    @property
    def a_values(self):
        """numpy.NDArray : Unit cell a lattice parameters associated with the scan."""
        if self.__a_values is None:
            raise ValueError('No results yet!')
        return self.__a_values

    @a_values.setter
    def a_values(self, value):
        if value is None:
            self.__a_values = value
        else:
            value = np.asarray(value, dtype=float)
            self.__a_values = value

    @property
    def energy_values(self):
        """numpy.NDArray : Measured potential energy for each r value."""
        if self.__energy_values is None:
            raise ValueError('No results yet!')
        return self.__energy_values

    @energy_values.setter
    def energy_values(self, value):
        if value is None:
            self.__energy_values = value
        else:
            value = np.asarray(value, dtype=float)
            self.__energy_values = value

    @property
    def min_cells(self):
        """list : atomman.Systems for the dimensions scanned with local energy minima."""
        if self.__min_cells is None:
            raise ValueError('No results yet!')
        for i in range(len(self.__min_cells)):
            if not isinstance(self.__min_cells[i], am.System):
                self.__min_cells[i] = am.load('system_model', self.__min_cells[i])
        return self.__min_cells

    @min_cells.setter
    def min_cells(self, value):
        if value is None:
            self.__min_cells = value
        else:
            self.__min_cells = aslist(value)

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
        if 'number_of_steps_r' in kwargs:
            self.number_of_steps_r = kwargs['number_of_steps_r']
        if 'minimum_r' in kwargs:
            self.minimum_r = kwargs['minimum_r']
        if 'maximum_r' in kwargs:
            self.maximum_r = kwargs['maximum_r']

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Load universal content
        input_dict = super().load_parameters(params, key=key)

        # Load input/output units
        self.units.load_parameters(input_dict)

        # Load calculation-specific booleans
        
        # Load calculation-specific integers
        self.number_of_steps_r = int(input_dict.get('number_of_steps_r', 201))

        # Load calculation-specific unitless floats
        
        # Load calculation-specific floats with units
        self.minimum_r = value(input_dict, 'minimum_r',
                               default_unit=self.units.length_unit,
                               default_term='2.0 angstrom')
        self.maximum_r = value(input_dict, 'maximum_r',
                               default_unit=self.units.length_unit,
                               default_term='6.0 angstrom')
        
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
            params['buildcombos'] = 'crystalprototype load_file prototype'
            params['sizemults'] = '10 10 10'
            params['minimum_r'] = '0.5 angstrom'
            params['maximum_r'] = '6.0 angstrom'
            params['number_of_steps_r'] = '276'

            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'prototype_{key}'] = kwargs[key]
                
                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]
        
        elif branch == 'bop':
            
            # Check for required kwargs
            assert 'lammps_command' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'crystalprototype load_file prototype'
            params['prototype_potential_pair_style'] = 'bop'
            params['sizemults'] = '10 10 10'
            params['minimum_r'] = '2.0 angstrom'
            params['maximum_r'] = '6.0 angstrom'
            params['number_of_steps_r'] = '201'

            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    if key != 'potential_pair_style':
                        params[f'prototype_{key}'] = kwargs[key]
                
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
        template += self.units.template()

        # Build calculation-specific content
        header = 'Run parameters'
        keys = ['minimum_r', 'maximum_r', 'number_of_steps_r']
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
                'minimum_r',
                'maximum_r',
                'number_of_steps_r',
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
        run_params['minimum_r'] = uc.model(self.minimum_r,
                                           self.units.length_unit)
        run_params['maximum_r'] = uc.model(self.maximum_r,
                                           self.units.length_unit)
        run_params['number_of_steps_r'] = self.number_of_steps_r

        # Build results
        if self.status == 'finished':
            calc['cohesive-energy-relation'] = scan = DM()
            scan['r'] = uc.model(self.r_values, self.units.length_unit)
            scan['a'] = uc.model(self.a_values, self.units.length_unit)
            scan['cohesive-energy'] = uc.model(self.energy_values,
                                                self.units.energy_unit)

            for cell in self.min_cells:
               system_model = cell.dump('system_model', box_unit=self.units.length_unit)
               calc.append('minimum-atomic-system', system_model['atomic-system'])

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

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.minimum_r = uc.value_unit(run_params['minimum_r'])
        self.maximum_r = uc.value_unit(run_params['maximum_r'])
        self.number_of_steps_r = run_params['number_of_steps_r']

        # Load results
        if self.status == 'finished':
            scan = calc['cohesive-energy-relation']
            self.r_values = uc.value_unit(scan['r'])
            self.a_values = uc.value_unit(scan['a'])
            self.energy_values = uc.value_unit(scan['cohesive-energy'])

            self.min_cells = []
            for cell in calc.aslist('minimum-atomic-system'):
               self.min_cells.append(DM([('atomic-system', cell)]))

    @staticmethod
    def mongoquery(name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None, lammps_version=None,
                   potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                   potential_key=None, potential_id=None, minimum_r=None,
                   maximum_r=None, number_of_steps_r=None, symbols=None):
        
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
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.minimum_r', minimum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maximum_r', maximum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_r', number_of_steps_r)

        return mquery

    @staticmethod
    def cdcsquery(key=None, iprPy_version=None,
                  atomman_version=None, script=None, branch=None,
                  status=None, lammps_version=None,
                  potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                  potential_key=None, potential_id=None, minimum_r=None,
                  maximum_r=None, number_of_steps_r=None, symbols=None):
        
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
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.minimum_r', minimum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.maximum_r', maximum_r)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.number_of_steps_r', number_of_steps_r)

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
        meta['minimum_r'] = self.minimum_r
        meta['maximum_r'] = self.maximum_r
        meta['number_of_steps_r'] = self.number_of_steps_r
        
        # Extract results
        if self.status == 'finished':
            meta['r_values'] = self.r_values
            meta['a_values'] = self.a_values
            meta['energy_values'] = self.energy_values

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
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, iprPy_version=None,
                     atomman_version=None, script=None, branch=None,
                     status=None, lammps_version=None,
                     potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                     potential_key=None, potential_id=None, minimum_r=None,
                     maximum_r=None, number_of_steps_r=None, symbols=None):
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
            &query.str_match.pandas(dataframe, 'minimum_r', minimum_r)
            &query.str_match.pandas(dataframe, 'maximum_r', maximum_r)
            &query.str_match.pandas(dataframe, 'number_of_steps_r', number_of_steps_r)
            &query.str_contains.pandas(dataframe, 'symbols', symbols)
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
        
        # Remove unused subset inputs
        del input_dict['transform']

        # Add calculation-specific inputs
        input_dict['rmin'] = self.minimum_r
        input_dict['rmax'] = self.maximum_r
        input_dict['rsteps'] = self.number_of_steps_r

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
        self.r_values = results_dict['r_values']
        self.a_values = results_dict['a_values']
        self.energy_values = results_dict['Ecoh_values']
        self.min_cells = results_dict['min_cell']
        