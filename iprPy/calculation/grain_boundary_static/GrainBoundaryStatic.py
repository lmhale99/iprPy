# coding: utf-8

# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union

import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .grain_boundary_static import grain_boundary_static
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, LammpsMinimize,
                                   GrainBoundary)
from ...input import value

class GrainBoundaryStatic(Calculation):
    """Class for static grain boundary energy calculations"""

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
        self.__minimize = LammpsMinimize(self)
        self.__defect = GrainBoundary(self)
        subsets = (self.commands, self.potential, self.system,
                   self.minimize, self.defect, self.units)

        # Initialize unique calculation attributes
        self.potential_energy = 0.0
        self.__gb_energies = None
        self.__min_gb_energy = None
        self.__final_dump = None
        
        # Define calc shortcut
        self.calc = grain_boundary_static

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'grain_boundary_static.py',
            'gbmin.template'
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
    def minimize(self) -> LammpsMinimize:
        """LammpsMinimize subset"""
        return self.__minimize

    @property
    def defect(self) -> GrainBoundary:
        """GrainBoundary subset"""
        return self.__defect

    @property
    def potential_energy(self) -> float:
        """float: The reference per-atom bulk potential energy to use when computing grain boundary energies"""
        return self.__potential_energy
    
    @potential_energy.setter
    def potential_energy(self, val: float):
        self.__potential_energy = float(val)

    @property
    def final_dump(self) -> dict:
        """dict: Info about the final dump file"""
        if self.__final_dump is None:
            raise ValueError('No results yet!')
        return self.__final_dump

    @property
    def min_gb_energy(self) -> float:
        """float: The minimum grain boundary energy found across all explored configurations"""
        if self.__min_gb_energy is None:
            raise ValueError('No results yet!')
        return self.__min_gb_energy

    @property
    def gb_energies(self) -> list:
        """list: The grain boundary energies found across all explored configurations"""
        if self.__gb_energies is None:
            raise ValueError('No results yet!')
        return self.__gb_energies

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
        potential_energy : float, optional
            The reference per-atom bulk potential energy to use when computing
            grain boundary energies.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'potential_energy' in kwargs:
            self.potential_energy = kwargs['potential_energy']

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
        input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
        input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-18 eV/angstrom')

        # Load calculation-specific strings

        # Load calculation-specific booleans

        # Load calculation-specific integers

        # Load calculation-specific unitless floats

        # Load calculation-specific floats with units
        self.potential_energy = value(input_dict, 'potential_energy',
                              default_unit=self.units.energy_unit,
                              default_term='0.0 eV')

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

        # Extract potential energy from load file if needed/possible
        if self.potential_energy == 0.0 and self.system.load_style == 'system_model':
            if self.system.load_content is not None:
                model = self.system.load_content
            else:
                model = self.system.load_file
            try:
                parent = am.library.load_record('relaxed_crystal', model=model)
            except:
                pass
            else:
                self.potential_energy = parent.potential_energy

    def master_prepare_inputs(self,
                              branch: str = 'main',
                              **kwargs: any) -> dict:
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
                'defect grainboundary_file'
            ]
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['defect_record'] = 'grain_boundary'
      
            params['grainboundary_minwidth'] = '120'
            params['forcetolerance'] = '1e-18 eV/angstrom'
            params['maxiterations'] = '10000'
            params['maxevaluations'] = '100000'
            params['maxevaluations'] = '100000'

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
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'potential_energy': ' '.join([
                "The reference per-atom potential energy from the bulk crystal",
                "to use for calculating the grain boundary energies. If not given,",
                "will try to extract from the load file if it is a relaxed_crystal",
                "record, or set to 0.0 otherwise."]),
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
                self.system.keyset +
                [
                    'potential_energy',
                ]
            ] +

            # Defect multikeys
            self.defect.multikeys +

            # Run parameter keys
            #[
            #    [
                    
            #    ]
            #] +

            # Minimize keys
            [
                self.minimize.keyset
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-grain-boundary-static'

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
        self.defect.build_model(calc, after='system-info')
        self.minimize.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']

        run_params['potential-energy'] = uc.model(self.potential_energy,
                                                 self.units.energy_unit)

        # Build results
        if self.status == 'finished':
            
            calc['final-system'] = DM()
            calc['final-system']['artifact'] = DM()
            calc['final-system']['artifact']['file'] = self.final_dump['filename']
            calc['final-system']['artifact']['format'] = 'atom_dump'
            calc['final-system']['symbols'] = self.final_dump['symbols']
            
            #energy_per_area_unit = f'{self.units.energy_unit}/{self.units.length_unit}^2'
            energy_per_area_unit = 'mJ/m^2'

            calc['minimum-grain-boundary-energy'] = uc.model(self.min_gb_energy, energy_per_area_unit)
            calc['grain-boundary-energies'] = uc.model(self.gb_energies, energy_per_area_unit)

            
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

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.potential_energy = uc.value_unit(run_params['potential-energy'])

        # Load results
        if self.status == 'finished':
            
            self.__final_dump = {
                'filename': calc['final-system']['artifact']['file'],
                'symbols': calc['final-system']['symbols']
            }

            self.__min_gb_energy = uc.value_unit(calc['minimum-grain-boundary-energy'])
            self.__gb_energies = uc.value_unit(calc['grain-boundary-energies'])

########################## Metadata interactions ##############################

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        # Call super to extract universal and subset content
        meta = super().metadata()

        # Extract calculation-specific content
        meta['potential_energy'] = self.potential_energy

        # Extract results
        if self.status == 'finished':
            meta['min_gb_energy'] = self.min_gb_energy
            meta['gb_energies'] = self.gb_energies
            

        return meta

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',

            'load_file',
            'load_options',
            'symbols',

            'potential_LAMMPS_key',
            'potential_key',

            'grainboundary_key',

        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

    def isvalid(self) -> bool:
        return self.system.family == self.defect.family

########################### Calculation interactions ##########################

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""

        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Add calculation-specific inputs
        input_dict['potential_energy'] = self.potential_energy

        # Return input_dict
        return input_dict

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'gb-*.dat',
            'log-*.lammps',
            '*.dump',
            'gbmin.in'
        ]

    def process_results(self, results_dict: dict):
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
        self.__final_dump = {
            'filename': results_dict['dumpfile_final'],
            'symbols': results_dict['symbols_final']
        }
        self.__gb_energies = results_dict['gb_energies']
        self.__min_gb_energy = results_dict['min_gb_energy']
