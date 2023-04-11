# coding: utf-8

# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union
import random

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .point_defect_diffusion import pointdiffusion
from ...calculation_subset import (LammpsPotential, LammpsCommands, Units,
                                   AtommanSystemLoad, AtommanSystemManipulate, PointDefect)

class PointDefectDiffusion(Calculation):
    """Class for managing point defect diffusion calculations"""

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, Path, IOBase, DM, None]=None,
                 name: Optional[str]=None,
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
        self.__defect = PointDefect(self)
        subsets = (self.commands, self.potential, self.system,
                   self.system_mods, self.defect, self.units)

        # Initialize unique calculation attributes
        self.temperature = 0.0
        self.thermosteps = 100
        self.dumpsteps = None
        self.runsteps = 200000
        self.equilsteps = 20000
        self.randomseed = None

        self.__nsamples = None
        self.__natoms = None
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
        self.__measured_temperature = None
        self.__measured_temperature_std = None
        self.__dx = None
        self.__dy = None
        self.__dz = None
        self.__d = None

        # Define calc shortcut
        self.calc = pointdiffusion

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'point_defect_diffusion.py',
            'diffusion.template'
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
    def system_mods(self) -> AtommanSystemManipulate:
        """AtommanSystemManipulate subset"""
        return self.__system_mods

    @property
    def defect(self) -> PointDefect:
        """PointDefect subset"""
        return self.__defect

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
    def dumpsteps(self, val: Optional[float]):
        if val is None:
            self.__dumpsteps = None
        else:
            val = int(val)
            assert val >= 0
            self.__dumpsteps = val

    @property
    def runsteps(self) -> int:
        """int : The number of NVE MD steps where diffusion is evaluated"""
        return self.__runsteps

    @runsteps.setter
    def runsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__runsteps = val

    @property
    def equilsteps(self) -> int:
        """int : The number of NVT MD steps performed before the NVE runsteps"""
        return self.__equilsteps

    @equilsteps.setter
    def equilsteps(self, val: int):
        val = int(val)
        assert val >= 0
        self.__equilsteps = val

    @property
    def randomseed(self) -> int:
        """int: A random generator seed"""
        return self.__randomseed

    @randomseed.setter
    def randomseed(self, val: Optional[int]):
        if val is None:
            val = random.randint(1, 900000000)
        else:
            val = int(val)
            assert val > 0 and val <= 900000000
        self.__randomseed = val

    @property
    def natoms(self) -> int:
        """int: Number of atoms in the defect system"""
        if self.__natoms is None:
            raise ValueError('No results yet!')
        return self.__natoms

    @property
    def nsamples(self) -> int:
        """int: Number of measurement samples used in mean, std values"""
        if self.__nsamples is None:
            raise ValueError('No results yet!')
        return self.__nsamples

    @property
    def potential_energy(self) -> float:
        """float: Potential energy for the relaxed system"""
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
        """float: Total energy for the relaxed system"""
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

    @property
    def dx(self) -> float:
        """float: Diffusion constant in the x direction"""
        if self.__dx is None:
            raise ValueError('No results yet!')
        return self.__dx

    @property
    def dy(self) -> float:
        """float: Diffusion constant in the y direction"""
        if self.__dy is None:
            raise ValueError('No results yet!')
        return self.__dy

    @property
    def dz(self) -> float:
        """float: Diffusion constant in the z direction"""
        if self.__dz is None:
            raise ValueError('No results yet!')
        return self.__dz

    @property
    def d(self) -> float:
        """float: Average diffusion constant"""
        if self.__d is None:
            raise ValueError('No results yet!')
        return self.__d

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
        temperature : str, optional
            The target run temperature
        thermosteps : int, optional
            Indicates how frequently thermo data is recorded.
        dumpsteps : int, optional
            Indicates how frequently atomic configurations are saved as LAMMPS
            dump files.
        runsteps : int, optional
            The number of NVE MD steps to perform where the atomic mean
            squared displacements are measured.
        equilsteps : int, optional
            The number of NVT MD steps to perform prior to the NVE run steps.
        randomseed : int, optional
            A random number generator seed that is used to create initial
            atomic velocities.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'temperature' in kwargs:
            self.temperature = kwargs['temperature']
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
        input_dict['sizemults'] = input_dict.get('sizemults', '12 12 12')

        # Load calculation-specific strings

        # Load calculation-specific booleans

        # Load calculation-specific integers
        self.runsteps = int(input_dict.get('runsteps', 200000))
        self.thermosteps = int(input_dict.get('thermosteps', 100))
        self.dumpsteps = int(input_dict.get('dumpsteps', 0))
        self.equilsteps = int(input_dict.get('equilsteps', 20000))
        self.randomseed = input_dict.get('randomseed', None)

        # Load calculation-specific unitless floats
        self.temperature = float(input_dict.get('temperature', 0.0))

        # Load calculation-specific floats with units

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Load defect parameters
        self.defect.load_parameters(input_dict)

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
                'atomicparent load_file parent',
                'defect pointdefect_file'
            ]
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['defect_record'] = 'point_defect'
            params['sizemults'] = '12 12 12'

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
            'temperature': ' '.join([
                "Target temperature for the simulations.  The NVT equilibrium",
                "steps will use this for the thermostat, then the energy scaled",
                "to try to capture this temperature for the NVE runs."]),
            'thermosteps': ' '.join([
                "How often LAMMPS will print thermo data.  Default value is",
                "runsteps//1000 or 1 if runsteps is less than 1000."]),
            'dumpsteps': ' '.join([
                "How often LAMMPS will save the atomic configuration to a",
                "LAMMPS dump file.  Default value is runsteps, meaning only",
                "the first and last states are saved."]),
            'runsteps': ' '.join([
                "The number of MD integration steps to perform in the NVE run."]),
            'equilsteps': ' '.join([
                "The number of NVT MD integration steps to perform prior to the",
                "NVE runsteps to allow the system to equilibriate."]),
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

            # Defect keys
            [
                self.defect.keyset
            ] +

            # Run parameters
            [
                [
                    'temperature',
                    'thermosteps',
                    'dumpsteps',
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
        return 'calculation-point-defect-diffusion'

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

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']

        run_params['thermosteps'] = self.thermosteps
        run_params['dumpsteps'] = self.dumpsteps
        run_params['runsteps'] = self.runsteps
        run_params['equilsteps'] = self.equilsteps
        run_params['randomseed'] = self.randomseed

        # Save phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(self.temperature, 'K')

        # Build results
        if self.status == 'finished':

            calc['number-of-measurements'] = self.nsamples
            calc['number-of-atoms'] = self.natoms

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
            mps['potential-energy'] = uc.model(self.potential_energy,
                                               self.units.energy_unit,
                                               self.potential_energy_std)
            mps['total-energy'] = uc.model(self.total_energy,
                                           self.units.energy_unit,
                                           self.total_energy_std)

            # Save the diffusion constants
            calc['diffusion-rate'] = dr = DM()
            diffusion_unit = f'{self.units.length_unit}^2/s'
            dr['total'] = uc.model(self.d, diffusion_unit)
            dr['x-direction'] = uc.model(self.dx, diffusion_unit)
            dr['y-direction'] = uc.model(self.dy, diffusion_unit)
            dr['z-direction'] = uc.model(self.dz, diffusion_unit)

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
        self.thermosteps = run_params['thermosteps']
        self.dumpsteps = run_params['dumpsteps']
        self.runsteps = run_params['runsteps']
        self.equilsteps = run_params['equilsteps']
        self.randomseed = run_params['randomseed']

        # Load phase-state info
        self.temperature = uc.value_unit(calc['phase-state']['temperature'])

        # Load results
        if self.status == 'finished':

            self.__nsamples = calc['number-of-measurements']
            self.__natoms = calc['number-of-atoms']

            mps = calc['measured-phase-state']
            self.__measured_temperature = uc.value_unit(mps['temperature'])
            self.__measured_temperature_std = uc.error_unit(mps['temperature'])
            self.__measured_pressure_xx = uc.value_unit(mps['pressure-xx'])
            self.__measured_pressure_xx_std = uc.error_unit(mps['pressure-xx'])
            self.__measured_pressure_yy = uc.value_unit(mps['pressure-yy'])
            self.__measured_pressure_yy_std = uc.error_unit(mps['pressure-yy'])
            self.__measured_pressure_zz = uc.value_unit(mps['pressure-zz'])
            self.__measured_pressure_zz_std = uc.error_unit(mps['pressure-zz'])
            self.__potential_energy = uc.value_unit(mps['potential-energy'])
            self.__potential_energy_std = uc.error_unit(mps['potential-energy'])
            self.__total_energy = uc.value_unit(mps['total-energy'])
            self.__total_energy_std = uc.error_unit(mps['total-energy'])

            dr = calc['diffusion-rate']
            self.__d = uc.value_unit(dr['total'])
            self.__dx = uc.value_unit(dr['x-direction'])
            self.__dy = uc.value_unit(dr['y-direction'])
            self.__dz = uc.value_unit(dr['z-direction'])

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

        # Extract results
        if self.status == 'finished':
            meta['nsamples'] = self.nsamples
            meta['natoms'] = self.natoms

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

            meta['d'] = self.d
            meta['dx'] = self.dx
            meta['dy'] = self.dy
            meta['dz'] = self.dz

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

            'a_mult',
            'b_mult',
            'c_mult',

            'pointdefect_key',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'temperature':1,
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
        input_dict['temperature'] = self.temperature
        input_dict['runsteps'] = self.runsteps
        input_dict['thermosteps'] = self.thermosteps
        input_dict['dumpsteps'] = self.dumpsteps
        input_dict['equilsteps'] = self.equilsteps
        input_dict['randomseed'] = self.randomseed

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

        self.__nsamples = results_dict['nsamples']
        self.__natoms = results_dict['natoms']

        self.__potential_energy = results_dict['E_pot']
        self.__potential_energy_std = results_dict['E_pot_std']
        self.__total_energy = results_dict['E_total']
        self.__total_energy_std = results_dict['E_total_std']

        self.__measured_pressure_xx = results_dict['pxx']
        self.__measured_pressure_xx_std = results_dict['pxx_std']
        self.__measured_pressure_yy = results_dict['pyy']
        self.__measured_pressure_yy_std = results_dict['pyy_std']
        self.__measured_pressure_zz = results_dict['pzz']
        self.__measured_pressure_zz_std = results_dict['pzz_std']
        self.__measured_temperature = results_dict['temp']
        self.__measured_temperature_std = results_dict['temp_std']

        self.__d = results_dict['d']
        self.__dx = results_dict['dx']
        self.__dy = results_dict['dy']
        self.__dz = results_dict['dz']
