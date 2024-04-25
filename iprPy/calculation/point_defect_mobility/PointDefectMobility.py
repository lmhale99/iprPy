# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

import numpy as np
import numpy.typing as npt

# iprPy imports
from .. import Calculation
from ...input import boolean
from .point_defect_mobility import point_defect_mobility
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate,
                                   LammpsNEB, PointDefectNEB)

class PointDefectMobility(Calculation):
    """Class for managing point defect mobility calculations"""

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
        self.__system_mods = AtommanSystemManipulate(self)
        self.__neb = LammpsNEB(self)
        self.__defect = PointDefectNEB(self)
        subsets = (self.commands, self.potential, self.system,
                   self.system_mods, self.neb, self.defect, self.units)

        # Initialize unique calculation attributes
        #self.neb_pos1 = None
        #self.neb_pos2 = None
        #self.neb_symbol = None
        self.__neb_coordinates = None
        self.__neb_energies = None
        self.__neb_positions = None
        self.__forward_barrier = None
        self.__reverse_barrier = None        

        # Define calc shortcut
        self.calc = point_defect_mobility

        # Call parent constructor
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
                 'point_defect_mobility.py',
                 'neb_lammps.template',
        ]

############################## Class attributes ################################

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
    def system_mods(self) -> AtommanSystemManipulate:
        """AtommanSystemManipulate subset"""
        return self.__system_mods

    @property
    def neb(self) -> LammpsNEB:
        """LammpsNEB subset"""
        return self.__neb

    @property
    def defect(self) -> PointDefectNEB:
        """PointDefectNEB subset"""
        return self.__defect

    #@property
    #def neb_pos1(self) -> Optional[np.ndarray]:
    #    """numpy.ndarray: Position(s) of the NEB atom(s) for the first replica"""
    #    return self.__neb_pos1

    #@neb_pos1.setter
    #def neb_pos1(self, val: Union[str, npt.ArrayLike]):
    #    if val is None:
    #        self.__neb_pos1 = None
    #    else:
    #        if isinstance(val, str):
    #            val = np.array(val.strip().split(), dtype=float)
    #        else:
    #            val = np.asarray(val, dtype=float)
    #        try:
    #            val = val.reshape((-1, 3))
    #        except ValueError as e:
    #            raise ValueError('neb_pos1 needs (N,3) values') from e
    #        self.__neb_pos1 = val

    #@property
    #def neb_pos2(self) -> Optional[np.ndarray]:
    #    """numpy.ndarray: Position(s) of the NEB atom(s) for the last replica"""
    #    return self.__neb_pos2

    #@neb_pos2.setter
    #def neb_pos2(self, val: Union[str, npt.ArrayLike]):
    #    if val is None:
    #        self.__neb_pos2 = None
    #    else:
    #        if isinstance(val, str):
    #            val = np.array(val.strip().split(), dtype=float)
    #        else:
    #            val = np.asarray(val, dtype=float)
    #        try:
    #            val = val.reshape((-1, 3))
    #        except ValueError as e:
    #            raise ValueError('neb_pos2 needs (N,3) values') from e
    #        self.__neb_pos2 = val

    #@property
    #def neb_symbol(self) -> Optional[list]:
    #    """list or None: Symbol model(s) to assign to the NEB atom(s)"""
    #    return self.__neb_symbol
    
    #@neb_symbol.setter
    #def neb_symbol(self, val: Union[str, list, None]):
    #    if isinstance(val, str):
    #        self.__neb_symbol = val.split(' ')
    #    elif val is None:
    #        self.__neb_symbol = None
    #    else:
    #        self.__neb_symbol = list(val)

    @property
    def neb_coordinates(self) -> np.ndarray:
        """numpy.ndarray: Reaction coordinates for the final NEB step"""
        if self.__neb_coordinates is None:
            raise ValueError('No results yet!')
        return self.__neb_coordinates

    @property
    def neb_energies(self) -> np.ndarray:
        """numpy.ndarray: Energy values for the final NEB step"""
        if self.__neb_energies is None:
            raise ValueError('No results yet!')
        return self.__neb_energies
    
    @property
    def neb_positions(self) -> np.ndarray:
        """numpy.ndarray: Positions of each NEB atom in each replica for the final NEB step"""
        if self.__neb_positions is None:
            raise ValueError('No results yet!')
        return self.__neb_positions
    
    @property
    def forward_barrier(self) -> np.ndarray:
        """numpy.ndarray: Positions of each NEB atom in each replica for the final NEB step"""
        if self.__forward_barrier is None:
            raise ValueError('No results yet!')
        return self.__forward_barrier
    
    @property
    def reverse_barrier(self) -> np.ndarray:
        """numpy.ndarray: Positions of each NEB atom in each replica for the final NEB step"""
        if self.__reverse_barrier is None:
            raise ValueError('No results yet!')
        return self.__reverse_barrier  

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
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        #if 'neb_pos1' in kwargs:
        #    self.neb_pos1 = kwargs['neb_pos1']
        #if 'neb_pos2' in kwargs:
        #    self.neb_pos2 = kwargs['neb_pos2']
        #if 'neb_symbol' in kwargs:
        #    self.neb_symbol = kwargs['neb_symbol']

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
        input_dict['sizemults'] = input_dict.get('sizemults', '5 5 5')
        input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
        
        # Load calculation-specific strings
        #self.neb_pos1 = input_dict['neb_pos1']
        #self.neb_pos2 = input_dict['neb_pos2']
        #self.neb_symbol = input_dict.get('neb_symbol', None)

        # Load calculation-specific booleans
        #neb_scale = boolean(input_dict.get('neb_scale', False))

        # Load calculation-specific integers

        # Load calculation-specific unitless floats

        # Load calculation-specific floats with units

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load neb parameters
        self.neb.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Load defect parameters
        self.defect.load_parameters(input_dict)

        # Manipulate system
        self.system_mods.load_parameters(input_dict)
        
        # Scale atom positions relative to ucell
        #if neb_scale:
        #    self.neb_pos1 = self.system.ucell.box.position_relative_to_cartesian(self.neb_pos1)
        #    self.neb_pos2 = self.system.ucell.box.position_relative_to_cartesian(self.neb_pos2)


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
            raise NotImplementedError('no master prepare settings yet')
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
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            #'neb_pos1': ' '.join([
            #    'The position(s) for the NEB-controlled atoms in the first replica.',
            #    'Specify this as space-delimited float values where every three',
            #    'subsequent values represent the x y z coordinates of an atom.'
            #]),
            #'neb_pos2': ' '.join([
            #    'The position(s) for the NEB-controlled atoms in the last replica.',
            #    'Specify this as space-delimited float values where every three',
            #    'subsequent values represent the x y z coordinates of an atom.'
            #]),
            #'neb_scale': ' '.join([
            #    'Boolean indicating if the neb_pos values are to be taken',
            #     'as relative to the loaded unit cell and therefore should be',
            #     'scaled to absolute Cartesian values.'
            #]),
            #'neb_symbol': ' '.join([
            #    'The potential symbol model(s) to assign to the NEB atoms.  Should',
            #    'be a space-delimited list giving a value for each NEB atom.',
            #    'Optional if all atoms are of the same type.'
            #]),
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
                #'maxiterations',
                #'maxevaluations',
                #'defectmobility_allowable_impurity_numbers',
                #'defectmobility_impurity_list',
                #'defectmobility_impurity_blacklist'
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
            ] +

            # System mods keys
            [
                self.system_mods.keyset
            ] +

            # Defect keys
            [
                self.defect.keyset 
            ] +

            # NEB keys
            [
                self.neb.keyset
            ]
        )
        return keys


    
    
########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-point-defect-mobility'
    
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
        self.system_mods.build_model(calc)
        self.defect.build_model(calc, after='system-info')
        self.neb.build_model(calc)

        #Add the below information of intererest in the lower section - need to make adjustements since this does not work normally
        
        # Build results
        if self.status == 'finished':
                                                                      
            calc['results'] = DM()
            calc['results']['forward-barrier'] = uc.model(self.forward_barrier,
                                                          self.units.energy_unit)
            calc['results']['reverse-barrier'] = uc.model(self.reverse_barrier,
                                                          self.units.energy_unit)
            calc['results']['final-neb'] = DM()
            calc['results']['final-neb']['coordinates'] = uc.model(self.neb_coordinates)
            calc['results']['final-neb']['energy'] = uc.model(self.neb_energies,
                                                              self.units.energy_unit)
            for pos in self.neb_positions:
                atom = DM()
                atom['pos'] = uc.model(pos, self.units.length_unit)
            calc['results']['final-neb'].append('atom', atom)

        self._set_model(model)
        return model
    
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
        #meta['neb_pos1'] = self.neb_pos1
        #meta['neb_pos2'] = self.neb_pos2
        #meta['neb_symbol'] = self.neb_symbol

        # Extract results
        if self.status == 'finished':
            #List of params
            meta['forward_barrier'] = self.forward_barrier
            meta['reverse_barrier'] = self.reverse_barrier
            meta['neb_coordinates'] = self.neb_coordinates
            meta['neb_energies'] = self.neb_energies
            meta['neb_positions'] = self.neb_positions
        
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
                
                'a_mult',
                'b_mult',
                'c_mult',
                
                'pointdefectneb_key',
                'neb_symbol'

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

        #if self.neb_pos1 is None:
        #    raise ValueError('neb_pos1 not set!')
        #if self.neb_pos2 is None:
        #    raise ValueError('neb_pos2 not set!')
        #input_dict['neb_pos1'] = self.neb_pos1
        #input_dict['neb_pos2'] = self.neb_pos2
        #if self.neb_symbol is not None:
        #    input_dict['neb_symbol'] = self.neb_symbol

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        del input_dict['ucell']
        del input_dict['transform']

        # Return input_dict
        return input_dict


    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            '*.dump',
            'log.lammps*',
            'screen.*',
            'final.dat',
            'init.dat',
            'tmp.lammps.variable',
            'neb_lammps.in',            
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
        self.__neb_coordinates = results_dict['neb_coordinates']
        self.__neb_energies = results_dict['neb_energies']
        self.__neb_positions = results_dict['neb_positions']
        self.__forward_barrier = results_dict['forward_barrier']
        self.__reverse_barrier = results_dict['reverse_barrier']