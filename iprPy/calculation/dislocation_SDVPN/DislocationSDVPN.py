# coding: utf-8

# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union

import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .dislocation_SDVPN import sdvpn
from ...calculation_subset import (Units, AtommanSystemLoad, Dislocation,
                                   AtommanElasticConstants, AtommanGammaSurface)
from ...input import termtodict, value, boolean
from ...tools import aslist

class DislocationSDVPN(Calculation):
    """Class for managing semi-discrete variational Peierls-Nabarro calcuations"""

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
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        self.__defect = Dislocation(self)
        self.__elastic = AtommanElasticConstants(self)
        self.__gamma = AtommanGammaSurface(self)
        subsets = (self.system, self.elastic, self.gamma,
                   self.defect, self.units)

        # Initialize unique calculation attributes
        self.xnum = None
        self.xmax = None
        self.xstep = None
        self.xscale = False
        self.minimize_style = 'Powell'
        self.minimize_options = {}
        self.minimize_cycles = 10
        self.cutofflongrange = uc.set_in_units(1000, 'angstrom')
        self.tau = np.zeros((3,3))
        self.alpha = 0.0
        self.beta = np.zeros((3,3))
        self.cdiffelastic = False
        self.cdiffsurface = True
        self.cdiffstress = False
        self.halfwidth = uc.set_in_units(1, 'angstrom')
        self.normalizedisreg = True
        self.fullstress = True

        self.__sdvpn_solution = None
        self.__energies = None
        self.__disregistries = None

        # Define calc shortcut
        self.calc = sdvpn

        # Call parent constructor
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'dislocation_SDVPN.py'
        ]

############################## Class attributes ###############################

    @property
    def units(self) -> Units:
        """Units subset"""
        return self.__units

    @property
    def system(self) -> AtommanSystemLoad:
        """AtommanSystemLoad subset"""
        return self.__system

    @property
    def defect(self) -> Dislocation:
        """Dislocation subset"""
        return self.__defect

    @property
    def elastic(self) -> AtommanElasticConstants:
        """AtommanElasticConstants subset"""
        return self.__elastic

    @property
    def gamma(self) -> AtommanGammaSurface:
        """AtommanGammaSurface subset"""
        return self.__gamma

    @property
    def xnum(self) -> int:
        """int: The number of x coordinate values"""
        return self.__xnum

    @xnum.setter
    def xnum(self, val: int):
        if val is None:
            self.__xnum = val
        else:
            self.__xnum = int(val)

    @property
    def xmax(self) -> float:
        """float: The maximum x coordinate value"""
        return self.__xmax

    @xmax.setter
    def xmax(self, val: float):
        if val is None:
            self.__xmax = val
        else:
            self.__xmax = float(val)

    @property
    def xstep(self) -> float:
        """float: The step size between the x coordinate values"""
        return self.__xstep

    @xstep.setter
    def xstep(self, val: float):
        if val is None:
            self.__xstep = val
        else:
            self.__xstep = float(val)

    @property
    def xscale(self) -> Optional[bool]:
        """bool: Flag if xstep/xmax values are absolute or scaled"""
        return self.__xscale

    @xscale.setter
    def xscale(self, val: Optional[bool]):
        if val is None:
            self.__xscale = val
        else:
            self.__xscale = boolean(val)

    @property
    def minimize_style(self) -> str:
        """str: The scipy.minimize style to use"""
        return self.__minimize_style

    @minimize_style.setter
    def minimize_style(self, val: str):
        self.__minimize_style = str(val)

    @property
    def minimize_options(self) -> dict:
        """dict: kwarg options to pass to scipy.minimize"""
        return self.__minimize_options

    @minimize_options.setter
    def minimize_options(self, val: dict):
        assert isinstance(val, dict)
        self.__minimize_options = val

    @property
    def minimize_cycles(self) -> int:
        """int: The number of minimization cycles to run"""
        return self.__minimize_cycles

    @minimize_cycles.setter
    def minimize_cycles(self, val: int):
        self.__minimize_cycles = int(val)

    @property
    def cutofflongrange(self) -> float:
        """float: The cutoff to use for the long-range elastic energy term"""
        return self.__cutofflongrange

    @cutofflongrange.setter
    def cutofflongrange(self, val: float):
        val = float(val)
        assert val >= 0.0
        self.__cutofflongrange = float(val)

    @property
    def tau(self) -> np.ndarray:
        """numpy.NDArray: External stress tensor to apply to the system"""
        return self.__tau

    @tau.setter
    def tau(self, val: npt.ArrayLike):
        val = np.asarray(val)
        assert val.shape == (3,3)
        self.__tau = val

    @property
    def alpha(self) -> list:
        """list: Non-local correction term parameters"""
        return self.__alpha

    @alpha.setter
    def alpha(self, val: Union[str, list]):
        if isinstance(value, str):
            self.__alpha = [float(v) for v in val.split()]
        else:
            self.__alpha = [float(v) for v in aslist(val)]

    @property
    def beta(self) -> np.ndarray:
        """numpy.NDArray: Surface correction term parameter tensor"""
        return self.__beta

    @beta.setter
    def beta(self, val: npt.ArrayLike):
        val = np.asarray(val)
        assert val.shape == (3,3)
        self.__beta = val

    @property
    def cdiffelastic(self) -> Optional[bool]:
        """bool: Flag if central difference is used for the elastic term"""
        return self.__cdiffelastic

    @cdiffelastic.setter
    def cdiffelastic(self, val: Optional[bool]):
        if val is None:
            self.__cdiffelastic = val
        else:
            self.__cdiffelastic = boolean(val)

    @property
    def cdiffsurface(self) -> Optional[bool]:
        """bool: Flag if central difference is used for the surface term"""
        return self.__cdiffsurface

    @cdiffsurface.setter
    def cdiffsurface(self, val: Optional[bool]):
        if val is None:
            self.__cdiffsurface = val
        else:
            self.__cdiffsurface = boolean(val)

    @property
    def cdiffstress(self) -> Optional[bool]:
        """bool: Flag if central difference is used for the stress term"""
        return self.__cdiffstress

    @cdiffstress.setter
    def cdiffstress(self, val: Optional[bool]):
        if val is None:
            self.__cdiffstress = val
        else:
            self.__cdiffstress = boolean(val)

    @property
    def normalizedisreg(self) -> Optional[bool]:
        """
        bool: Flag indicating if the total cumulative disregistry is normalized
        to the Burgers vector
        """
        return self.__normalizedisreg

    @normalizedisreg.setter
    def normalizedisreg(self, val: Optional[bool]):
        if val is None:
            self.__normalizedisreg = val
        else:
            self.__normalizedisreg = boolean(val)

    @property
    def fullstress(self) -> Optional[bool]:
        """bool: Flag for switching which stress term equation is used"""
        return self.__fullstress

    @fullstress.setter
    def fullstress(self, val: Optional[bool]):
        if val is None:
            self.__fullstress = val
        else:
            self.__fullstress = boolean(val)

    @property
    def sdvpn_solution(self) -> am.defect.SDVPN:
        """atomman.defect.SDVPN: The dislocation solution object"""
        if self.__sdvpn_solution is None:
            raise ValueError('No results yet!')
        elif not isinstance(self.__sdvpn_solution, am.defect.SDVPN):
            self.__sdvpn_solution = am.defect.SDVPN(model=self.__sdvpn_solution)

        return self.__sdvpn_solution

    @property
    def energies(self) -> list:
        """list: The total energies for the solution after each minimization cycle"""
        if self.__energies is None:
            raise ValueError('No results yet!')
        else:
            return self.__energies

    @property
    def disregistries(self) -> list:
        """list: The disregistry profiles for the solution after each minimization cycle"""
        if self.__disregistries is None:
            raise ValueError('No results yet!')
        else:
            return self.__disregistries

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
        xnum : int, optional
            The number of x coordinates to use.
        xmax : flaot, optional
            The maximum x coordinate to use.
        xstep : float, optional
            The step size to use between the x coordinates.
        xscale : bool, optional
            Flag indicating if xmax and/or xstep values are to be taken as
            absolute or relative to ucell's a lattice parameter.
        minimize_style : str, optional
            The scipy.minimize style to use.
        minimize_options : dict, optional
            kwarg options to pass to scipy.minimize.
        minimize_cycles : int, optional
            The number of mimimization cycles to perform.
        cutofflongrange : float, optional
            The cutoff to use for the longrange energy term.
        tau : array-like object, optional
            The applied stress values to use.
        alpha : list, optional
            The non-local correction parameters to use.
        beta : array-like object, optional
            The surface correction parameters to use.
        cdiffelastic : bool, optional
            Flag if central difference is used for the elastic term.
        cdiffsurface : bool, optional
            Flag if central difference is used for the surface term.
        cdiffstress : bool, optional
            Flag if central difference is used for the stress term.
        halfwidth : float, optional
            An initial arctan halfwidth guess.
        normalizedisreg : bool, optional
            Flag indicating if the disregistry is normalized to the Burgers
            vector.
        fullstress : bool, optional
            Flag that determines which stress term expression is used.
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'xnum' in kwargs:
            self.xnum = kwargs['xnum']
        if 'xmax' in kwargs:
            self.xmax = kwargs['xmax']
        if 'xstep' in kwargs:
            self.xstep = kwargs['xstep']
        if 'xscale' in kwargs:
            self.xscale = kwargs['xscale']
        if 'minimize_style' in kwargs:
            self.minimize_style = kwargs['minimize_style']
        if 'minimize_options' in kwargs:
            self.minimize_options = kwargs['minimize_options']
        if 'minimize_cycles' in kwargs:
            self.minimize_cycles = kwargs['minimize_cycles']
        if 'cutofflongrange' in kwargs:
            self.cutofflongrange = kwargs['cutofflongrange']
        if 'tau' in kwargs:
            self.tau = kwargs['tau']
        if 'alpha' in kwargs:
            self.alpha = kwargs['alpha']
        if 'beta' in kwargs:
            self.beta = kwargs['beta']
        if 'cdiffelastic' in kwargs:
            self.cdiffelastic = kwargs['cdiffelastic']
        if 'cdiffsurface' in kwargs:
            self.cdiffsurface = kwargs['cdiffsurface']
        if 'cdiffstress' in kwargs:
            self.cdiffstress = kwargs['cdiffstress']
        if 'halfwidth' in kwargs:
            self.halfwidth = kwargs['halfwidth']
        if 'normalizedisreg' in kwargs:
            self.normalizedisreg = kwargs['normalizedisreg']
        if 'fullstress' in kwargs:
            self.fullstress = kwargs['fullstress']

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
        pl_unit = f'{self.units.pressure_unit}*{self.units.length_unit}'
        p_per_l_unit = f'{self.units.pressure_unit}/{self.units.length_unit}'

        # Change default values for subset terms

        # Load calculation-specific strings
        alpha = input_dict.get('alpha', '0.0')
        self.minimize_style = input_dict.get('minimize_style', 'Powell')
        minimize_options = input_dict.get('minimize_options', '')

        # Load calculation-specific booleans
        self.cdiffelastic = boolean(input_dict.get('cdiffelastic', False))
        self.cdiffsurface = boolean(input_dict.get('cdiffsurface', True))
        self.cdiffstress = boolean(input_dict.get('cdiffstress', False))
        self.fullstress = boolean(input_dict.get('fullstress', True))
        self.normalizedisreg = boolean(input_dict.get('normalizedisreg', True))
        xscale = boolean(input_dict.get('xscale', False))

        # Load calculation-specific integers
        self.xnum = input_dict.get('xnum', None)
        self.minimize_cycles = int(input_dict.get('minimize_cycles', 10))

        # Load calculation-specific unitless floats
        self.xstep = input_dict.get('xstep', None)
        self.xmax = input_dict.get('xmax', None)

        # Load calculation-specific floats with units
        bxx = value(input_dict, 'beta_xx', default_unit=pl_unit,
                    default_term='0.0 GPa*angstrom')
        bxy = value(input_dict, 'beta_xy', default_unit=pl_unit,
                    default_term='0.0 GPa*angstrom')
        bxz = value(input_dict, 'beta_xz', default_unit=pl_unit,
                    default_term='0.0 GPa*angstrom')
        byy = value(input_dict, 'beta_yy', default_unit=pl_unit,
                    default_term='0.0 GPa*angstrom')
        byz = value(input_dict, 'beta_yz', default_unit=pl_unit,
                    default_term='0.0 GPa*angstrom')
        bzz = value(input_dict, 'beta_zz', default_unit=pl_unit,
                    default_term='0.0 GPa*angstrom')
        txy = value(input_dict, 'tau_xy', default_unit=self.units.pressure_unit,
                    default_term='0.0 GPa')
        tyy = value(input_dict, 'tau_yy', default_unit=self.units.pressure_unit,
                    default_term='0.0 GPa')
        tyz = value(input_dict, 'tau_yz', default_unit=self.units.pressure_unit,
                    default_term='0.0 GPa')
        self.halfwidth = value(input_dict, 'halfwidth',
                               default_unit=self.units.length_unit,
                               default_term='1.0 angstrom')
        self.cutofflongrange = value(input_dict, 'cutofflongrange',
                                     default_unit=self.units.length_unit,
                                     default_term='1000 angstrom')

        # Process calculation-specific terms
        alpha = alpha.split()
        if len(alpha) > 1:
            try:
                float(alpha[-1])
            except:
                unit = alpha.pop()
        for i in range(len(alpha)):
            alpha[i] = uc.set_in_units(float(alpha[i]), p_per_l_unit)
        self.alpha = alpha
        self.beta = np.array([[bxx, bxy, bxz],
                              [bxy, byy, byz],
                              [bxz, byz, bzz]])
        self.tau = np.array([[0.0, txy, 0.0],
                             [txy, tyy, tyz],
                             [0.0, tyz, 0.0]])

        # Process minimize_options
        boolkeys = ['disp']
        intkeys = ['maxiter', 'maxfev']
        floatkeys = ['xatol', 'fatol', 'xtol', 'ftol', 'gtol', 'norm', 'eps']
        keys = boolkeys + intkeys + floatkeys
        min_options = termtodict(minimize_options, keys)
        for boolkey in boolkeys:
            if boolkey in min_options:
                min_options[boolkey] = boolean(min_options[boolkey])
        for intkey in intkeys:
            if intkey in min_options:
                min_options[intkey] = int(min_options[intkey])
        for floatkey in floatkeys:
            if floatkey in min_options:
                min_options[floatkey] = float(min_options[floatkey])
        self.minimize_options = min_options

        # Load initial system
        self.system.load_parameters(input_dict)

        # Load defect parameters
        self.defect.load_parameters(input_dict)

        # Load elastic constants
        self.elastic.load_parameters(input_dict)

        # Load gamma surface
        self.gamma.load_parameters(input_dict)

        # Scale xmax and xstep if needed
        if xscale is True:
            if self.xmax is not None:
                self.xmax *= self.system.ucell.box.a
            if self.xstep is not None:
                self.xstep *= self.system.ucell.box.a

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

        if branch == 'main':

            # Set common workflow settings
            params['buildcombos'] = [
                'atomicparent load_file parent',
                'defect dislocation_file'
            ]
            params['parent_record'] = 'calculation_elastic_constants_static'
            params['parent_load_key'] = 'system-info'
            params['parent_strainrange'] = '1e-7'
            params['defect_record'] = 'dislocation'

            # Copy kwargs to params
            for key in kwargs:
                params[key] = kwargs[key]

        else:
            raise ValueError(f'Unknown branch {branch}')

        return params

    @property
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'xmax': ' '.join([
                "The maximum value of the x-coordinates to use for the points",
                "where the disregistry is evaluated.  The solution is centered",
                "around x=0, therefore this also corresponds to the minimum value",
                "of x used.  The set of x-coordinates used is fully defined by",
                "giving at least two of xmax, xstep and xnum."]),
            'xstep': ' '.join([
                "The step size (delta x) value between the x-coordinates used to",
                "evaluate the disregistry.  The set of x-coordinates used is fully",
                "defined by giving at least two of xmax, xstep and xnum."]),
            'xnum': ' '.join([
                "The total number of x-coordinates at which to evaluate the",
                "disregistry.  The set of x-coordinates used is fully defined by",
                "giving at least two of xmax, xstep and xnum."]),
            'xscale': ' '.join([
                "Boolean indicating if xmax and xstep are taken in angstroms (False) or",
                "relative to the unit cell's a box vector (True).  Default value is False."]),
            'minimize_style': ' '.join([
                "The scipy.optimize.minimize method style to use when solving for the",
                "disregistry.  Default value is 'Powell', which seems to do decently",
                "well for this problem."]),
            'minimize_options': ' '.join([
                "Allows for the specification of the options dictionary used by",
                "scipy.optimize.minimize. This is given as 'key value key value...'."]),
            'minimize_cycles': ' '.join([
                "Specifies the number of times to run the minimization in succession.",
                "The minimization algorithms used by the underlying scipy code often",
                "benefit from restarting and rerunning the minimized configuration to",
                "achive a better fit.  Default value is 10."]),
            'cutofflongrange': ' '.join([
                "The radial cutoff (in distance units) to use for the long-range",
                "elastic energy.  The long-range elastic energy is",
                "configuration-independent, so this value changes the dislocation's",
                "energy but not the computed disregistry profile. Default value is",
                "1000 angstroms."]),
            'tau_xy': ' '.join([
                "Shear stress (in units of pressure) to apply to the system.",
                "Default value is 0 GPa."]),
            'tau_yy': ' '.join([
                "Normal stress (in units of pressure) to apply to the system.",
                "Default value is 0 GPa."]),
            'tau_yz': ' '.join([
                "Shear stress (in units of pressure) to apply to the system.",
                "Default value is 0 GPa."]),
            'alpha': ' '.join([
                "Coefficient(s) (in pressure/length units) of the non-local",
                "energy correction term to use.  Default value is 0.0, meaning",
                "this correction is not applied."]),
            'beta_xx': ' '.join([
                "The xx component of the surface energy coefficient tensor",
                "(in units pressure-length) to use. Default value is 0.0",
                "GPa-Angstrom."]),
            'beta_yy': ' '.join([
                "The yy component of the surface energy coefficient tensor",
                "(in units pressure-length) to use. Default value is 0.0",
                "GPa-Angstrom."]),
            'beta_zz': ' '.join([
                "The zz component of the surface energy coefficient tensor",
                "(in units pressure-length) to use. Default value is 0.0",
                "GPa-Angstrom."]),
            'beta_xy': ' '.join([
                "The xy component of the surface energy coefficient tensor",
                "(in units pressure-length) to use. Default value is 0.0",
                "GPa-Angstrom."]),
            'beta_xz': ' '.join([
                "The xz component of the surface energy coefficient tensor",
                "(in units pressure-length) to use. Default value is 0.0",
                "GPa-Angstrom."]),
            'beta_yz': ' '.join([
                "The yz component of the surface energy coefficient tensor",
                "(in units pressure-length) to use. Default value is 0.0",
                "GPa-Angstrom."]),
            'cdiffelastic': ' '.join([
                "Boolean indicating if the dislocation density is computed",
                "using central difference for the elastic term.  Default",
                "value is False"]),
            'cdiffsurface': ' '.join([
                "Boolean indicating if the dislocation density is computed",
                "using central difference for the surface term.  Default",
                "value is True"]),
            'cdiffstress': ' '.join([
                "Boolean indicating if the dislocation density is computed",
                "using central difference for the stress term.  Default",
                "value is False"]),
            'halfwidth': ' '.join([
                "The arctan disregistry halfwidth (in length units) to use",
                "for creating the initial disregistry guess."]),
            'normalizedisreg': ' '.join([
                "Boolean indicating how the disregistry profile is handled.",
                "If True (default), the disregistry is scaled such that the",
                "minimum x value has a disregistry of 0 and the maximum x",
                "value has a disregistry equal to the dislocation's Burgers",
                "vector.  Note that the disregistry for these endpoints is",
                "fixed, so if you use False the initial disregistry should be",
                "close to the final solution."]),
            'fullstress': ' '.join([
                "Boolean indicating which of two stress formulas to use.",
                "True uses the original full formulation, while False uses a",
                "newer, simpler representation.  Default value is True."]),
        }

    @property
    def singularkeys(self) -> list:
        """list: Calculation keys that can have single values during prepare."""

        keys = (
            # Universal keys
            super().singularkeys

            # Subset keys
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

            # Combination of system, elastic and gamma keys
            [
                self.system.keyset + 
                self.elastic.keyset + 
                self.gamma.keyset
            ] +

            # Defect multikeys
            self.defect.multikeys +

            # Run parameters
            [
                [
                    'xmax',
                    'xstep',
                    'xnum',
                    'xscale',
                    'minimize_style',
                    'minimize_options',
                    'minimize_cycles',
                    'cutofflongrange',
                    'tau_xy',
                    'tau_yy',
                    'tau_yz',
                    'alpha',
                    'beta_xx',
                    'beta_yy',
                    'beta_zz',
                    'beta_xy',
                    'beta_xz',
                    'beta_yz',
                    'cdiffelastic',
                    'cdiffsurface',
                    'cdiffstress',
                    'halfwidth',
                    'normalizedisreg',
                    'fullstress',
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-dislocation-SDVPN'

    def build_model(self) -> DM:
        """
        Generates and returns model content based on the values set to object.
        """
        # Build universal content
        model = super().build_model()
        calc = model[self.modelroot]

        # Build subset content
        self.system.build_model(calc, after='potential-LAMMPS')
        self.defect.build_model(calc, after='system-info')
        self.gamma.build_model(calc)
        self.elastic.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']

        run_params['halfwidth'] = uc.model(self.halfwidth,
                                           self.units.length_unit)

        # Scale xmax and xstep by alat
        if self.xscale is True:
            if self.system.box_parameters is not None:
                alat = float(self.system.box_parameters[0])
            else:
                try:
                    alat = self.system.ucell.box.a
                except:
                    pass
                else:
                    if self.xmax is not None:
                        self.xmax *= alat
                    if self.xstep is not None:
                        self.xstep *= alat
                    self.xscale = False

        x = am.defect.pn_arctan_disregistry(xmax=self.xmax,
                                            xnum=self.xnum,
                                            xstep=self.xstep)[0]

        run_params['xmax'] = x.max()
        run_params['xnum'] = len(x)
        run_params['xstep'] = x[1]-x[0]
        run_params['xscale'] = self.xscale
        run_params['min_cycles'] = self.minimize_cycles

        # Build results
        if self.status != 'finished':
            p_per_l_unit = f'{self.units.pressure_unit}/{self.units.length_unit}'
            p_l_unit = f'{self.units.pressure_unit}*{self.units.length_unit}'
            calc['semidiscrete-variational-Peierls-Nabarro'] = svpn = DM()
            svpn['parameter'] = params = DM()
            params['tau'] = uc.model(self.tau, self.units.pressure_unit)
            params['alpha'] = uc.model(self.alpha, p_per_l_unit)
            params['beta'] = uc.model(self.beta, p_l_unit)
            params['cdiffelastic'] = self.cdiffelastic
            params['cdiffsurface'] = self.cdiffsurface
            params['cdiffstress'] = self.cdiffstress
            params['cutofflongrange'] = uc.model(self.cutofflongrange,
                                                 self.units.length_unit)
            params['fullstress'] = self.fullstress
            params['min_method'] = self.minimize_style
            params['min_options'] = self.minimize_options


        else:
            pnsolution = self.sdvpn_solution
            pnmodel = pnsolution.model(length_unit=self.units.length_unit,
                                       #energyperarea_unit=self.units.energy_unit,
                                       pressure_unit=self.units.pressure_unit,
                                       include_gamma=False)
            key = 'semidiscrete-variational-Peierls-Nabarro'
            calc[key] = pnmodel[key]

            e_per_l_unit = f'{self.units.energy_unit}/{self.units.length_unit}'
            calc['misfit-energy'] = uc.model(pnsolution.misfit_energy(), e_per_l_unit)
            calc['elastic-energy'] = uc.model(pnsolution.elastic_energy(), e_per_l_unit)
            calc['long-range-energy'] = uc.model(pnsolution.longrange_energy(), e_per_l_unit)
            calc['stress-energy'] = uc.model(pnsolution.stress_energy(), e_per_l_unit)
            calc['surface-energy'] = uc.model(pnsolution.surface_energy(), e_per_l_unit)
            calc['nonlocal-energy'] = uc.model(pnsolution.nonlocal_energy(), e_per_l_unit)
            calc['total-energy'] = uc.model(pnsolution.total_energy(), e_per_l_unit)
            calc['total-energy-per-cycle'] = uc.model(self.energies, e_per_l_unit)

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
        self.halfwidth = uc.value_unit(run_params['halfwidth'])
        self.xmax = run_params['xmax']
        self.xnum = run_params['xnum']
        self.xstep = run_params['xstep']
        self.xscale = run_params.get('xscale', False)
        self.minimize_cycles = run_params['min_cycles']

        # Build results
        if self.status != 'finished':
            #p_per_l_unit = f'{self.units.pressure_unit}/{self.units.length_unit}'
            #p_l_unit = f'{self.units.pressure_unit}*{self.units.length_unit}'
            params = calc['semidiscrete-variational-Peierls-Nabarro']['parameter']

            self.tau = uc.value_unit(params['tau'])
            self.alpha = uc.value_unit(params['alpha'])
            self.beta = uc.value_unit(params['beta'])
            self.cdiffelastic = params['cdiffelastic']
            self.cdiffsurface = params['cdiffsurface']
            self.cdiffstress = params['cdiffstress']
            self.cutofflongrange = uc.value_unit(params['cutofflongrange'])
            self.fullstress = params['fullstress']
            self.minimize_style = params['min_method']
            self.minimize_options = params['min_options']

        # Load results
        if self.status == 'finished':
            self.__sdvpn_solution = calc
            self.__energies = uc.value_unit(calc['total-energy-per-cycle'])

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
        meta['halfwidth'] = self.halfwidth
        meta['xmax'] = self.xmax
        meta['xnum'] = self.xnum
        meta['xstep'] = self.xstep
        meta['xscale'] = self.xscale
        meta['tau'] = self.tau
        meta['alpha'] = self.alpha
        meta['beta'] = self.beta
        meta['cdiffelastic'] = self.cdiffelastic
        meta['cdiffsurface'] = self.cdiffsurface
        meta['cdiffstress'] = self.cdiffstress
        meta['cutofflongrange'] = self.cutofflongrange
        meta['fullstress'] = self.fullstress
        meta['min_method'] = self.minimize_style
        meta['min_options'] = self.minimize_options

        return meta

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',

            'xnum',

            'load_file',
            'load_options',
            'symbols',

            'dislocation_key',
            'gammasurface_calc_key',

            'cdiffelastic',
            'cdiffsurface',
            'cdiffstress',

            'fullstress',
            'min_method',
            'min_options',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'xmax':1e-2,
            'xstep':1e-2,
            'cutofflongrange':1e-2,
            'K11':1e-2, 
            'K12':1e-2, 
            'K13':1e-2, 
            'K22':1e-2, 
            'K23':1e-2, 
            'K33':1e-2,
            'tau11':1e-2, 
            'tau12':1e-2, 
            'tau13':1e-2, 
            'tau22':1e-2, 
            'tau23':1e-2, 
            'tau33':1e-2,
            'beta11':1e-2, 
            'beta12':1e-2, 
            'beta13':1e-2, 
            'beta22':1e-2, 
            'beta23':1e-2, 
            'beta33':1e-2,
            'alpha1':1e-2,
        }

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

        # Remove unused subset inputs
        del input_dict['sizemults']
        del input_dict['amin']
        del input_dict['bmin']
        del input_dict['cmin']
        del input_dict['shift']
        del input_dict['shiftscale']
        del input_dict['shiftindex']

        # Add calculation-specific inputs
        input_dict['cutofflongrange'] = self.cutofflongrange
        input_dict['tau'] = self.tau
        input_dict['alpha'] = self.alpha
        input_dict['beta'] = self.beta
        input_dict['cdiffelastic'] = self.cdiffelastic
        input_dict['cdiffsurface'] = self.cdiffsurface
        input_dict['cdiffstress'] = self.cdiffstress
        input_dict['fullstress'] = self.fullstress
        input_dict['halfwidth'] = self.halfwidth
        input_dict['normalizedisreg'] = self.normalizedisreg
        input_dict['xnum'] = self.xnum
        input_dict['xstep'] = self.xstep
        input_dict['xmax'] = self.xmax
        input_dict['xscale'] = self.xscale
        input_dict['min_method'] = self.minimize_style
        input_dict['min_options'] = self.minimize_options
        input_dict['min_cycles'] = self.minimize_cycles

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
        self.__sdvpn_solution = results_dict['SDVPN_solution']
        self.__energies = results_dict['minimization_energies']
        self.__disregistries = results_dict['disregistry_profiles']
