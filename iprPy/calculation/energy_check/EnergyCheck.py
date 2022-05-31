# coding: utf-8

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# iprPy imports
from .. import Calculation
from .energy_check import energy_check
from ...calculation_subset import *

class EnergyCheck(Calculation):
    """Class for managing potential energy checks of structures"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""
        
        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        subsets = (self.commands, self.potential, self.system, self.units)

        # Initialize unique calculation attributes
        self.__potential_energy = None

        # Define calc shortcut
        self.calc = energy_check

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self):
        """list: the names of each file used by the calculation."""
        return [
            'energy_check.py',
            'run0.template'
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
    def potential_energy(self):
        """float: The measured potential energy per atom for the system"""
        if self.__potential_energy is None:
            raise ValueError('No results yet!')
        return self.__potential_energy

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Load universal content
        input_dict = super().load_parameters(params, key=key)
        
        # Load input/output units
        self.units.load_parameters(input_dict)
        
        # Change default values for subset terms

        # Load calculation-specific strings

        # Load calculation-specific booleans
        
        # Load calculation-specific integers

        # Load calculation-specific unitless floats

        # Load calculation-specific floats with units
        
        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

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
            ] 
        )       
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'calculation-energy-check'
    
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

        # Build results
        if self.status == 'finished':
          
            # Save the final cohesive energy
            calc['potential-energy'] = uc.model(self.potential_energy,
                                                self.units.energy_unit,
                                                None)

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

        # Load results
        if self.status == 'finished':
            self.__potential_energy = uc.value_unit(calc['potential-energy'])

########################## Metadata interactions ##############################

    def metadata(self):
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        # Call super to extract universal and subset content
        meta = super().metadata()
        
        # Extract results
        if self.status == 'finished':
            meta['E_pot'] = self.potential_energy

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
            'potential_key',
        ]

########################### Calculation interactions ##########################

    def calc_inputs(self):
        """Builds calculation inputs from the class's attributes"""
        
        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Rename ucell to system
        input_dict['system'] = input_dict.pop('ucell')

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
        self.__potential_energy = results_dict['E_pot']