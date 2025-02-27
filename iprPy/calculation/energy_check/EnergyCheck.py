# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union


from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

# iprPy imports
from .. import Calculation
from .energy_check import energy_check
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad)
from ...input import boolean

class EnergyCheck(Calculation):
    """Class for managing potential energy checks of structures"""

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, Path, IOBase, DM, None]=None,
                 name: Optional[str]=None,
                 database = None,
                 params: Union[str, Path, IOBase, dict] = None,
                 **kwargs: any):
        """
        Initializes a Calculation object for a given style.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Record content in data model format to read in.  Cannot be given
            with params.
        name : str, optional
            The name to use for saving the record.  By default, this should be
            the calculation's key.
        database : yabadaba.Database, optional
            A default Database to associate with the Record, typically the
            Database that the Record was obtained from.  Can allow for Record
            methods to perform Database operations without needing to specify
            which Database to use.
        params : str, file-like object or dict, optional
            Calculation input parameters or input parameter file.  Cannot be
            given with model.
        **kwargs : any
            Any other core Calculation record attributes to set.  Cannot be
            given with model.
        """

        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        subsets = (self.commands, self.potential, self.system, self.units)

        # Initialize unique calculation attributes
        self.dumpforces = False
        self.__potential_energy = None
        self.__potential_energy_atom = None
        self.__pressure_xx = None
        self.__pressure_yy = None
        self.__pressure_zz = None

        # Define calc shortcut
        self.calc = energy_check

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'energy_check.py',
            'run0.template'
        ]

############################## Class attributes ###############################

    @property
    def commands(self) -> LammpsCommands:
        """LammpsCommands subset"""
        return self.__commands

    @property
    def potential(self) -> LammpsPotential:
        """LammpsPotential subset"""
        return self.__potential

    @property
    def units(self) -> Units:
        """Units subset"""
        return self.__units

    @property
    def system(self) -> AtommanSystemLoad:
        """AtommanSystemLoad subset"""
        return self.__system

    @property
    def dumpforces(self) -> bool:
        """bool: Indicates if the atomic forces are to be calculated and dumped"""
        return self.__dumpforces
    
    @dumpforces.setter
    def dumpforces(self, val: bool):
        self.__dumpforces = boolean(val)

    @property
    def potential_energy(self) -> float:
        """float: The measured potential energy for the system"""
        if self.__potential_energy is None:
            raise ValueError('No results yet!')
        return self.__potential_energy
    
    @property
    def potential_energy_atom(self) -> float:
        """float: The measured potential energy per atom for the system"""
        if self.__potential_energy_atom is None:
            raise ValueError('No results yet!')
        return self.__potential_energy_atom
    
    @property
    def pressure_xx(self) -> float:
        """float: The measured xx component of pressure for the system"""
        if self.__pressure_xx is None:
            raise ValueError('No results yet!')
        return self.__pressure_xx
    
    @property
    def pressure_yy(self) -> float:
        """float: The measured yy component of pressure for the system"""
        if self.__pressure_yy is None:
            raise ValueError('No results yet!')
        return self.__pressure_yy
    
    @property
    def pressure_zz(self) -> float:
        """float: The measured zz component of pressure for the system"""
        if self.__pressure_zz is None:
            raise ValueError('No results yet!')
        return self.__pressure_zz

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs: any):
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameters
        ----------
        name : str, optional
            The name to assign to the calculation.  By default, this is set as
            the calculation's key.
        dumpforces : bool, optional 
            Indicates if the atomic forces are to be calculated and dumped.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'dumpforces' in kwargs:
            self.dumpforces = kwargs['dumpforces']

####################### Parameter file interactions ###########################

    def load_parameters(self,
                        params: Union[dict, str, IOBase],
                        key: Optional[str] = None):
        """
        Reads in and sets calculation parameters.

        Parameters
        ----------
        params : dict, str or file-like object
            The parameters or parameter file to read in.
        key : str, optional
            A new key value to assign to the object.  If not given, will use
            calc_key field in params if it exists, or leave the key value
            unchanged.
        """
        # Load universal content
        input_dict = super().load_parameters(params, key=key)

        # Load input/output units
        self.units.load_parameters(input_dict)

        # Change default values for subset terms

        # Load calculation-specific strings

        # Load calculation-specific booleans
        self.dumpforces = input_dict.get('dumpforces', False)

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
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'dumpforces': ' '.join([
                "Bool flag indicating if atomic forces are to be reported in",
                "a dump file.  Default value is False"]),
        }

    @property
    def singularkeys(self) -> list:
        """list: Calculation keys that can have single values during prepare."""

        keys = (
            # Universal keys
            super().singularkeys

            # Subset keys
            + self.commands.keyset
            + self.units.keyset

            # Calculation-specific keys
            + [
                'dumpforces'
            ]
        )
        return keys

    @property
    def multikeys(self) -> list:
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
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-energy-check'

    def build_model(self) -> DM:
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

            # Save measured phase-state info
            calc['measured-phase-state'] = mps = DM()
            mps['pressure-xx'] = uc.model(self.pressure_xx,
                                          self.units.pressure_unit)
            mps['pressure-yy'] = uc.model(self.pressure_yy,
                                          self.units.pressure_unit)
            mps['pressure-zz'] = uc.model(self.pressure_zz,
                                          self.units.pressure_unit)

            # Save the evaluated potential energy
            calc['potential-energy'] = uc.model(self.potential_energy,
                                                self.units.energy_unit)
            calc['potential-energy-per-atom'] = uc.model(self.potential_energy_atom,
                                                self.units.energy_unit)

        self._set_model(model)
        return model

    def load_model(self,
                   model: Union[str, DM],
                   name: Optional[str] = None):
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
            mps = calc['measured-phase-state']
            self.__pressure_xx = uc.value_unit(mps['pressure-xx'])
            self.__pressure_yy = uc.value_unit(mps['pressure-yy'])
            self.__pressure_zz = uc.value_unit(mps['pressure-zz'])

            self.__potential_energy = uc.value_unit(calc['potential-energy'])
            self.__potential_energy_atom = uc.value_unit(calc['potential-energy-per-atom'])

########################## Metadata interactions ##############################

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        # Call super to extract universal and subset content
        meta = super().metadata()

        # Extract results
        if self.status == 'finished':
            meta['E_pot_total'] = self.potential_energy
            meta['E_pot_atom'] = self.potential_energy_atom
            meta['pressure_xx'] = self.pressure_xx
            meta['pressure_yy'] = self.pressure_yy
            meta['pressure_zz'] = self.pressure_zz

        return meta

    @property
    def compare_terms(self) -> list:
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

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""

        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Rename ucell to system
        input_dict['system'] = input_dict.pop('ucell')

        # Add calculation-specific inputs
        input_dict['dumpforces'] = self.dumpforces

        # Return input_dict
        return input_dict

    def process_results(self, results_dict: dict):
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
        self.__potential_energy = results_dict['E_pot_total']
        self.__potential_energy_atom = results_dict['E_pot_atom']
        self.__pressure_xx = results_dict['P_xx']
        self.__pressure_yy = results_dict['P_yy']
        self.__pressure_zz = results_dict['P_zz']
