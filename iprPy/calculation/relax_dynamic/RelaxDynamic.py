# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from copy import deepcopy
from typing import Optional, Union
import random

import numpy as np

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .relax_dynamic import relax_dynamic
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate)
from ...input import value

class RelaxDynamic(Calculation):
    """Class for managing dynamic relaxations"""

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
        subsets = (self.commands, self.potential, self.system,
                   self.system_mods, self.units)

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
        self.restartsteps = None
        self.runsteps = 220000
        self.equilsteps = 20000
        self.randomseed = None

        self.__initial_dump = None
        self.__final_dump = None
        self.__final_box = None
        self.__lx_mean = None
        self.__ly_mean = None
        self.__lz_mean = None
        self.__xy_mean = None
        self.__xz_mean = None
        self.__yz_mean = None
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
        super().__init__(model=model, name=name, database=database, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'relax_dynamic.py',
            'full_relax.template'
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
    def pressure_xx(self) -> float:
        """float: Target relaxation pressure component xx"""
        return self.__pressure_xx

    @pressure_xx.setter
    def pressure_xx(self, val: float):
        self.__pressure_xx = float(val)

    @property
    def pressure_yy(self) -> float:
        """float: Target relaxation pressure component yy"""
        return self.__pressure_yy

    @pressure_yy.setter
    def pressure_yy(self, val: float):
        self.__pressure_yy = float(val)

    @property
    def pressure_zz(self) -> float:
        """float: Target relaxation pressure component zz"""
        return self.__pressure_zz

    @pressure_zz.setter
    def pressure_zz(self, val: float):
        self.__pressure_zz = float(val)

    @property
    def pressure_xy(self) -> float:
        """float: Target relaxation pressure component xy"""
        return self.__pressure_xy

    @pressure_xy.setter
    def pressure_xy(self, val: float):
        self.__pressure_xy = float(val)

    @property
    def pressure_xz(self) -> float:
        """float: Target relaxation pressure component xz"""
        return self.__pressure_xz

    @pressure_xz.setter
    def pressure_xz(self, val: float):
        self.__pressure_xz = float(val)

    @property
    def pressure_yz(self) -> float:
        """float: Target relaxation pressure component yz"""
        return self.__pressure_yz

    @pressure_yz.setter
    def pressure_yz(self, val: float):
        self.__pressure_yz = float(val)

    @property
    def temperature(self) -> float:
        """float: Target relaxation temperature"""
        return self.__temperature

    @temperature.setter
    def temperature(self, val: float):
        val = float(val)
        assert val >= 0.0
        self.__temperature = val

    @property
    def integrator(self) -> str:
        """str: MD integration scheme"""
        return self.__integrator

    @integrator.setter
    def integrator(self, val: Optional[str]):
        if val is None:
            if self.temperature == 0.0:
                val = 'nph+l'
            else:
                val = 'npt'
        self.__integrator = str(val)

    @property
    def thermosteps(self) -> int:
        """int : How often termo data is recorded"""
        return self.__thermosteps

    @thermosteps.setter
    def thermosteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__thermosteps = val

    @property
    def dumpsteps(self) -> int:
        """int : How often atomic configurations are dumped"""
        if self.__dumpsteps is None:
            return self.runsteps
        else:
            return self.__dumpsteps

    @dumpsteps.setter
    def dumpsteps(self, val: int):
        if val is None:
            self.__dumpsteps = None
        else:
            val = int(val)
            assert val >= 0
            self.__dumpsteps = val

    @property
    def restartsteps(self) -> int:
        """int : How often restart files are dumped"""
        if self.__restartsteps is None:
            return self.runsteps
        else:
            return self.__restartsteps

    @restartsteps.setter
    def restartsteps(self, val: int):
        if val is None:
            self.__restartsteps = None
        else:
            val = int(val)
            assert val >= 0
            self.__restartsteps = val

    @property
    def runsteps(self) -> int:
        """int : The number of MD steps where properties are evaluated"""
        return self.__runsteps

    @runsteps.setter
    def runsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__runsteps = val

    @property
    def equilsteps(self) -> int:
        """int : The number of MD steps to perform prior to runsteps"""
        return self.__equilsteps

    @equilsteps.setter
    def equilsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilsteps = val

    @property
    def randomseed(self) -> int:
        """int: Random number generator seed"""
        return self.__randomseed

    @randomseed.setter
    def randomseed(self, val: int):
        if val is None:
            val = random.randint(1, 900000000)
        else:
            val = int(val)
            assert val > 0 and val <= 900000000
        self.__randomseed = val

    @property
    def initial_dump(self) -> dict:
        """dict: Info about the initial dump file"""
        if self.__initial_dump is None:
            raise ValueError('No results yet!')
        return self.__initial_dump

    @property
    def final_dump(self) -> dict:
        """dict: Info about the final dump file"""
        if self.__final_dump is None:
            raise ValueError('No results yet!')
        return self.__final_dump

    @property
    def final_box(self) -> am.Box:
        """atomman.Box: Relaxed unit cell box"""
        if self.__final_box is None:
            raise ValueError('No results yet!')
        return self.__final_box

    @property
    def lx_mean(self) -> float:
        """float: Mean lx length used for final_box"""
        if self.__lx_mean is None:
            raise ValueError('No results yet!')
        return self.__lx_mean

    @property
    def lx_std(self) -> float:
        """float: Standard deviation for final_box's lx length"""
        if self.__lx_std is None:
            raise ValueError('No results yet!')
        return self.__lx_std

    @property
    def ly_mean(self) -> float:
        """float: Mean ly length used for final_box"""
        if self.__ly_mean is None:
            raise ValueError('No results yet!')
        return self.__ly_mean

    @property
    def ly_std(self) -> float:
        """float: Standard deviation for final_box's ly length"""
        if self.__ly_std is None:
            raise ValueError('No results yet!')
        return self.__ly_std

    @property
    def lz_mean(self) -> float:
        """float: Mean lz length used for final_box"""
        if self.__lz_mean is None:
            raise ValueError('No results yet!')
        return self.__lz_mean

    @property
    def lz_std(self) -> float:
        """float: Standard deviation for final_box's lz length"""
        if self.__lz_std is None:
            raise ValueError('No results yet!')
        return self.__lz_std

    @property
    def xy_mean(self) -> float:
        """float: Mean xy tilt used for final_box"""
        if self.__xy_mean is None:
            raise ValueError('No results yet!')
        return self.__xy_mean

    @property
    def xy_std(self) -> float:
        """float: Standard deviation for final_box's xy tilt"""
        if self.__xy_std is None:
            raise ValueError('No results yet!')
        return self.__xy_std

    @property
    def xz_mean(self) -> float:
        """float: Mean xz tilt used for final_box"""
        if self.__xz_mean is None:
            raise ValueError('No results yet!')
        return self.__xz_mean

    @property
    def xz_std(self) -> float:
        """float: Standard deviation for final_box's xz tilt"""
        if self.__xz_std is None:
            raise ValueError('No results yet!')
        return self.__xz_std

    @property
    def yz_mean(self) -> float:
        """float: Mean yz tilt used for final_box"""
        if self.__yz_mean is None:
            raise ValueError('No results yet!')
        return self.__yz_mean

    @property
    def yz_std(self) -> float:
        """float: Standard deviation for final_box's yz tilt"""
        if self.__yz_std is None:
            raise ValueError('No results yet!')
        return self.__yz_std

    @property
    def numsamples(self) -> int:
        """int: Number of measurement samples used in mean, std values"""
        if self.__numsamples is None:
            raise ValueError('No results yet!')
        return self.__numsamples

    @property
    def potential_energy(self) -> float:
        """float: Potential energy per atom for the relaxed system"""
        if self.__potential_energy is None:
            raise ValueError('No results yet!')
        return self.__potential_energy

    @property
    def potential_energy_std(self) -> float:
        """float: Standard deviation for potential_energy"""
        if self.__potential_energy_std is None:
            raise ValueError('No results yet!')
        return self.__potential_energy_std

    @property
    def total_energy(self) -> float:
        """float: Total energy per atom for the relaxed system"""
        if self.__total_energy is None:
            raise ValueError('No results yet!')
        return self.__total_energy

    @property
    def total_energy_std(self) -> float:
        """float: Standard deviation for total_energy"""
        if self.__total_energy_std is None:
            raise ValueError('No results yet!')
        return self.__total_energy_std

    @property
    def measured_pressure_xx(self) -> float:
        """float: Measured relaxation pressure component xx"""
        if self.__measured_pressure_xx is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xx

    @property
    def measured_pressure_xx_std(self) -> float:
        """float: Standard deviation for measured_pressure_xx"""
        if self.__measured_pressure_xx_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xx_std

    @property
    def measured_pressure_yy(self) -> float:
        """float: Measured relaxation pressure component yy"""
        if self.__measured_pressure_yy is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yy

    @property
    def measured_pressure_yy_std(self) -> float:
        """float: Standard deviation for measured_pressure_yy"""
        if self.__measured_pressure_yy_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yy_std

    @property
    def measured_pressure_zz(self) -> float:
        """float: Measured relaxation pressure component zz"""
        if self.__measured_pressure_zz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_zz

    @property
    def measured_pressure_zz_std(self) -> float:
        """float: Standard deviation for measured_pressure_zz"""
        if self.__measured_pressure_zz_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_zz_std

    @property
    def measured_pressure_xy(self) -> float:
        """float: Measured relaxation pressure component xy"""
        if self.__measured_pressure_xy is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xy

    @property
    def measured_pressure_xy_std(self) -> float:
        """float: Standard deviation for measured_pressure_xy"""
        if self.__measured_pressure_xy_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xy_std

    @property
    def measured_pressure_xz(self) -> float:
        """float: Measured relaxation pressure component xz"""
        if self.__measured_pressure_xz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xz

    @property
    def measured_pressure_xz_std(self) -> float:
        """float: Standard deviation for measured_pressure_xz"""
        if self.__measured_pressure_xz_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_xz_std

    @property
    def measured_pressure_yz(self) -> float:
        """float: Measured relaxation pressure component yz"""
        if self.__measured_pressure_yz is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yz

    @property
    def measured_pressure_yz_std(self) -> float:
        """float: Standard deviation for measured_pressure_yz"""
        if self.__measured_pressure_yz_std is None:
            raise ValueError('No results yet!')
        return self.__measured_pressure_yz_std

    @property
    def measured_temperature(self) -> float:
        """float: Measured temperature for the relaxed system"""
        if self.__measured_temperature is None:
            raise ValueError('No results yet!')
        return self.__measured_temperature

    @property
    def measured_temperature_std(self) -> float:
        """float: Standard deviation for measured_temperature"""
        if self.__measured_temperature_std is None:
            raise ValueError('No results yet!')
        return self.__measured_temperature_std

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
        pressure_xx : float, optional
            The target Pxx pressure component for the relaxation.
        pressure_yy : float, optional
            The target Pyy pressure component for the relaxation.
        pressure_zz : float, optional
            The target Pzz pressure component for the relaxation.
        pressure_xy : float, optional
            The target Pxy pressure component for the relaxation.
        pressure_xz : float, optional
            The target Pxz pressure component for the relaxation.
        pressure_yz : float, optional
            The target Pyz pressure component for the relaxation.
        temperature : float, optional
            The target temperature for the relaxation.
        integrator : str, optional
            The integration scheme to use.
        thermosteps : int, optional
            Indicates how often the thermo data is output.
        dumpsteps : int, optional
            Indicates how often the atomic configuration is output to a LAMMPS
            dump file.
        restartsteps : int, optional
            Indicates how often the atomic configuration is output to a LAMMPS
            restart file.
        runsteps : int, optional
            The total number of integration steps.
        equilsteps : int, optional
            The number of integration steps ignored to allow the system to get
            closer to equilibrium.
        randomseed : int, optional
            A random number generator seed to use for constructing the initial
            atomic velocities.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

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
        if 'restartsteps' in kwargs:
            self.restartsteps = kwargs['restartsteps']
        if 'runsteps' in kwargs:
            self.runsteps = kwargs['runsteps']
        if 'equilsteps' in kwargs:
            self.equilsteps = kwargs['equilsteps']
        if 'randomseed' in kwargs:
            self.randomseed = kwargs['randomseed']

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
        input_dict['sizemults'] = input_dict.get('sizemults', '10 10 10')

        # Load calculation-specific strings
        self.integrator = input_dict.get('integrator', None)

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.runsteps = int(input_dict.get('runsteps', 220000))
        self.thermosteps = int(input_dict.get('thermosteps', 100))
        self.dumpsteps = input_dict.get('dumpsteps', None)
        self.restartsteps = input_dict.get('restartsteps', None)
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
                'atomicreference load_file reference',
                'atomicparent load_file parent'
            ]
            params['parent_record'] = 'calculation_E_vs_r_scan'
            params['parent_load_key'] = 'minimum-atomic-system'
            params['parent_status'] = 'finished'
            params['sizemults'] = '10 10 10'
            params['atomshift'] = '0.05 0.05 0.05'
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

        elif branch == 'at_temp_50K':

            # Check for required kwargs
            assert 'lammps_command' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'atomicparent load_file parent'
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['sizemults'] = '10 10 10'
            params['atomshift'] = '0.05 0.05 0.05'
            params['temperature'] = '50'
            params['integrator'] = 'npt'
            params['thermosteps'] = '100'
            params['runsteps'] = '1000000'
            params['restartsteps'] = '50000'
            params['equilsteps'] = '0'

            # Copy kwargs to params
            for key in kwargs:

                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    if key != 'potential_pair_style':
                        params[f'parent_{key}'] = kwargs[key]

                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        elif branch == 'at_temp':

            # Check for required kwargs
            assert 'lammps_command' in kwargs
            assert 'temperature' in kwargs

            temperature = float(kwargs['temperature'])
            archive_temperature = temperature - 50

            # Set default workflow settings
            params['buildcombos'] = 'atomicarchive load_file archive'

            params['archive_record'] = 'calculation_relax_dynamic'
            params['archive_temperature'] = str(archive_temperature)
            params['archive_load_key'] = 'final-system'
            params['archive_status'] = 'finished'
            params['sizemults'] = '1 1 1'
            params['integrator'] = 'npt'
            params['thermosteps'] = '100'
            params['runsteps'] = '1000000'
            params['restartsteps'] = '50000'
            params['equilsteps'] = '0'

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
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'temperature': ' '.join([
                "Target temperature for the simulations.  Default value is 0."]),
            'pressure_xx': ' '.join([
                "The Pxx normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_yy': ' '.join([
                "The Pyy normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_zz': ' '.join([
                "The Pzz normal pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_xy': ' '.join([
                "The Pxy shear pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_xz': ' '.join([
                "The Pxz shear pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'pressure_yz': ' '.join([
                "The Pyz shear pressure component to relax the box to.",
                "Default value is 0.0 GPa."]),
            'integrator': ' '.join([
                "The MD integration scheme to use.  Default value is"
                "'nph+l' for temperature = 0, and 'npt' otherwise."]),
            'thermosteps': ' '.join([
                "How often LAMMPS will print thermo data.  Default value is",
                "runsteps//1000 or 1 if runsteps is less than 1000."]),
            'dumpsteps': ' '.join([
                "How often LAMMPS will save the atomic configuration to a",
                "LAMMPS dump file.  Default value is runsteps, meaning only",
                "the first and last states are saved."]),
            'restartsteps': ' '.join([
                "How often LAMMPS will save the atomic configuration to a",
                "LAMMPS restart file.  Default value is runsteps, meaning only",
                "the first and last states are saved."]),
            'runsteps': ' '.join([
                "The total number of MD integration steps to run including",
                "equil steps."]),
            'equilsteps': ' '.join([
                "The number of MD integration steps at the beginning of",
                "the simulation to ignore as equilibration time."]),
            'randomseed': ' '.join([
                "An int random number seed to use for generating initial velocities.",
                "A random int will be selected if not given."]),

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
                self.system.keyset
            ] +

            # System mods keys
            [
                self.system_mods.keyset
            ] +

            # Pressure parameters
            [
                [
                    'pressure_xx',
                    'pressure_yy',
                    'pressure_zz',
                    'pressure_xy',
                    'pressure_xz',
                    'pressure_yz',
                ]
            ] +

            # Temperature
            [
                [
                    'temperature',
                ]
            ] +

            # Run parameters
            [
                [
                    'integrator',
                    'thermosteps',
                    'dumpsteps',
                    'restartsteps',
                    'runsteps',
                    'equilsteps',
                    'randomseed',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-relax-dynamic'

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

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']

        run_params['integrator'] = self.integrator
        run_params['thermosteps'] = self.thermosteps
        run_params['dumpsteps'] = self.dumpsteps
        run_params['restartsteps'] = self.restartsteps
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
            mbp['lx'] = uc.model(self.lx_mean, self.units.length_unit,
                                 self.lx_std)
            mbp['ly'] = uc.model(self.ly_mean, self.units.length_unit,
                                 self.ly_std)
            mbp['lz'] = uc.model(self.lz_mean, self.units.length_unit,
                                 self.lz_std)
            mbp['xy'] = uc.model(self.xy_mean, self.units.length_unit,
                                 self.xy_std)
            mbp['xz'] = uc.model(self.xz_mean, self.units.length_unit,
                                 self.xz_std)
            mbp['yz'] = uc.model(self.yz_mean, self.units.length_unit,
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
            if not np.isnan(self.total_energy):
                calc['average-total-energy'] = uc.model(self.total_energy,
                                                        self.units.energy_unit,
                                                        self.total_energy_std)

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
        self.integrator = run_params['integrator']
        self.thermosteps = run_params['thermosteps']
        self.dumpsteps = run_params['dumpsteps']
        self.restartsteps = run_params.get('restartsteps', None)
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

            self.__lx_mean = uc.value_unit(calc['measured-box-parameter']['lx'])
            self.__lx_std = uc.error_unit(calc['measured-box-parameter']['lx'])
            self.__ly_mean = uc.value_unit(calc['measured-box-parameter']['ly'])
            self.__ly_std = uc.error_unit(calc['measured-box-parameter']['ly'])
            self.__lz_mean = uc.value_unit(calc['measured-box-parameter']['lz'])
            self.__lz_std = uc.error_unit(calc['measured-box-parameter']['lz'])
            self.__xy_mean = uc.value_unit(calc['measured-box-parameter']['xy'])
            self.__xy_std = uc.error_unit(calc['measured-box-parameter']['xy'])
            self.__xz_mean = uc.value_unit(calc['measured-box-parameter']['xz'])
            self.__xz_std = uc.error_unit(calc['measured-box-parameter']['xz'])
            self.__yz_mean = uc.value_unit(calc['measured-box-parameter']['yz'])
            self.__yz_std = uc.error_unit(calc['measured-box-parameter']['yz'])
            self.__final_box = am.Box(lx=self.lx_mean, ly=self.ly_mean, lz=self.lz_mean,
                                      xy=self.xy_mean, xz=self.xz_mean, yz=self.yz_mean)

            self.__potential_energy = uc.value_unit(calc['cohesive-energy'])
            self.__potential_energy_std = uc.error_unit(calc['cohesive-energy'])
            if 'average-total-energy' in calc:
                self.__total_energy = uc.value_unit(calc['average-total-energy'])
                self.__total_energy_std = uc.error_unit(calc['average-total-energy'])
            elif self.temperature == 0.0:
                self.__total_energy = self.__potential_energy
                self.__total_energy_std = self.__potential_energy_std
            else:
                self.__total_energy = np.nan
                self.__total_energy_std = np.nan

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

    @property
    def queries(self) -> dict:
        queries = deepcopy(super().queries)
        queries.update({
            'temperature': load_query(
                style='float_match',
                name='temperature',
                path=f'{self.modelroot}.phase-state.temperature.value',
                description='search by temperature in Kelvin'),
        })
        return queries

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

            meta['lx'] = self.lx_mean
            meta['lx_std'] = self.lx_std
            meta['ly'] = self.ly_mean
            meta['ly_std'] = self.ly_std
            meta['lz'] = self.lz_mean
            meta['lz_std'] = self.lz_std
            meta['xy'] = self.xy_mean
            meta['xy_std'] = self.xy_std
            meta['xz'] = self.xz_mean
            meta['xz_std'] = self.xz_std
            meta['yz'] = self.yz_mean
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

    @property
    def compare_fterms(self) -> dict:
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

########################### Calculation interactions ##########################

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""

        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Remove unused subset inputs
        del input_dict['transform']
        del input_dict['ucell']

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
        input_dict['restartsteps'] = self.restartsteps
        input_dict['equilsteps'] = self.equilsteps
        input_dict['randomseed'] = self.randomseed

        # Return input_dict
        return input_dict

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'init.dat',
            'log*.lammps',
            'full_relax*.in',
            '*.dump',
            '*.restart',
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
        self.__initial_dump = {
            'filename': results_dict['dumpfile_initial'],
            'symbols': results_dict['symbols_initial']
        }
        self.__final_dump = {
            'filename': results_dict['dumpfile_final'],
            'symbols': results_dict['symbols_final']
        }
        self.__numsamples = results_dict['nsamples']
        self.__lx_mean = results_dict['lx'] / (self.system_mods.a_mults[1] - self.system_mods.a_mults[0])
        self.__ly_mean = results_dict['ly'] / (self.system_mods.b_mults[1] - self.system_mods.b_mults[0])
        self.__lz_mean = results_dict['lz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        self.__xy_mean = results_dict['xy'] / (self.system_mods.b_mults[1] - self.system_mods.b_mults[0])
        self.__xz_mean = results_dict['xz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        self.__yz_mean = results_dict['yz'] / (self.system_mods.c_mults[1] - self.system_mods.c_mults[0])
        self.__final_box = am.Box(lx=self.lx_mean, ly=self.ly_mean, lz=self.lz_mean,
                                  xy=self.xy_mean, xz=self.xz_mean, yz=self.yz_mean)

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
