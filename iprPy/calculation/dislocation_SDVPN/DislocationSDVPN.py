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
from .dislocation_SDVPN import sdvpn
from ...calculation_subset import *
from ...input import termtodict, value, boolean
from ...tools import aslist, dict_insert

# Global class properties
modelroot = 'calculation-dislocation-SDVPN'

class DislocationSDVPN(Calculation):
    """Class for managing semi-discrete variational Peierls-Nabarro calcuations"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""
        
        # Initialize subsets used by the calculation
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        self.__defect = Dislocation(self)
        self.__elastic = AtommanElasticConstants(self)
        self.__gamma = AtommanGammaSurface(self)

        # Initialize unique calculation attributes
        self.xnum = None
        self.xmax = None
        self.xstep = None
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
        super().__init__(model=model, name=name, params=params, **kwargs)

############################## Class attributes ################################

    @property
    def units(self):
        """Units subset"""
        return self.__units

    @property
    def system(self):
        """AtommanSystemLoad subset"""
        return self.__system
    
    @property
    def defect(self):
        """Dislocation subset"""
        return self.__defect

    @property
    def elastic(self):
        """AtommanElasticConstants subset"""
        return self.__elastic

    @property
    def gamma(self):
        """AtommanGammaSurface subset"""
        return self.__gamma

    @property
    def xnum(self):
        """int: The number of x coordinate values"""
        return self.__xnum

    @xnum.setter
    def xnum(self, value):
        if value is None:
            self.__xnum = value
        else:
            self.__xnum = int(value)

    @property
    def xmax(self):
        """float: The maximum x coordinate value"""
        return self.__xmax

    @xmax.setter
    def xmax(self, value):
        if value is None:
            self.__xmax = value
        else:
            self.__xmax = float(value)

    @property
    def xstep(self):
        """float: The step size between the x coordinate values"""
        return self.__xstep

    @xstep.setter
    def xstep(self, value):
        if value is None:
            self.__xstep = value
        else:
            self.__xstep = float(value)

    @property
    def minimize_style(self):
        """str: The scipy.minimize style to use"""
        return self.__minimize_style

    @minimize_style.setter
    def minimize_style(self, value):
        self.__minimize_style = str(value)

    @property
    def minimize_options(self):
        """dict: kwarg options to pass to scipy.minimize"""
        return self.__minimize_options

    @minimize_options.setter
    def minimize_options(self, value):
        assert isinstance(value, dict)
        self.__minimize_options = value

    @property
    def minimize_cycles(self):
        """int: The number of minimization cycles to run"""
        return self.__minimize_cycles

    @minimize_cycles.setter
    def minimize_cycles(self, value):
        self.__minimize_cycles = int(value)

    @property
    def cutofflongrange(self):
        """float: The cutoff to use for the long-range elastic energy term"""
        return self.__cutofflongrange

    @cutofflongrange.setter
    def cutofflongrange(self, value):
        value = float(value)
        assert value >= 0.0
        self.__cutofflongrange = float(value)

    @property
    def tau(self):
        """numpy.NDArray: External stress tensor to apply to the system"""
        return self.__tau

    @tau.setter
    def tau(self, value):
        value = np.asarray(value)
        assert value.shape == (3,3)
        self.__tau = value

    @property
    def alpha(self):
        """list: Non-local correction term parameters"""
        return self.__alpha
    
    @alpha.setter
    def alpha(self, value):
        if isinstance(value, str):
            self.__alpha = [float(v) for v in value.split()]
        else:
            self.__alpha = [float(v) for v in aslist(value)]

    @property
    def beta(self):
        """numpy.NDArray: Surface correction term parameter tensor"""
        return self.__beta

    @beta.setter
    def beta(self, value):
        value = np.asarray(value)
        assert value.shape == (3,3)
        self.__beta = value

    @property
    def cdiffelastic(self):
        """bool: Flag if central difference is used for the elastic term"""
        return self.__cdiffelastic

    @cdiffelastic.setter
    def cdiffelastic(self, value):
        if value is None:
            self.__cdiffelastic = value
        else:
            self.__cdiffelastic = boolean(value)

    @property
    def cdiffsurface(self):
        """bool: Flag if central difference is used for the surface term"""
        return self.__cdiffsurface

    @cdiffsurface.setter
    def cdiffsurface(self, value):
        if value is None:
            self.__cdiffsurface = value
        else:
            self.__cdiffsurface = boolean(value)

    @property
    def cdiffstress(self):
        """bool: Flag if central difference is used for the stress term"""
        return self.__cdiffstress

    @cdiffstress.setter
    def cdiffstress(self, value):
        if value is None:
            self.__cdiffstress = value
        else:
            self.__cdiffstress = boolean(value)
    
    @property
    def normalizedisreg(self):
        """bool: Flag indicating if the total cumulative disregistry is normalized to the Burgers vector"""
        return self.__normalizedisreg

    @normalizedisreg.setter
    def normalizedisreg(self, value):
        if value is None:
            self.__normalizedisreg = value
        else:
            self.__normalizedisreg = boolean(value)

    @property
    def fullstress(self):
        """bool: Flag for switching which stress term equation is used"""
        return self.__fullstress

    @fullstress.setter
    def fullstress(self, value):
        if value is None:
            self.__fullstress = value
        else:
            self.__fullstress = boolean(value)

    @property
    def sdvpn_solution(self):
        """atomman.defect.SDVPN: The dislocation solution object"""
        if self.__sdvpn_solution is None:
            raise ValueError('No results yet!')
        elif not isinstance(self.__sdvpn_solution, am.defect.SDVPN):
            self.__sdvpn_solution = am.defect.SDVPN(model=self.__sdvpn_solution)
        else:
            return self.__sdvpn_solution

    @property
    def energies(self):
        """list: The total energies for the solution after each minimization cycle"""
        if self.__energies is None:
            raise ValueError('No results yet!')
        else:
            return self.__energies

    @property
    def disregistries(self):
        """list: The disregistry profiles for the solution after each minimization cycle"""
        if self.__disregistries is None:
            raise ValueError('No results yet!')
        else:
            return self.__disregistries

    def set_values(self, name=None, **kwargs):
        """Used to set initial common values for the calculation."""
        
        # Set universal content
        super().set_values(name=None, **kwargs)

        # Set subset values
        self.units.set_values(**kwargs)
        self.system.set_values(**kwargs)
        self.defect.set_values(**kwargs)
        self.elastic.set_values(**kwargs)
        self.gamma.set_values(**kwargs)

        # Set calculation-specific values
        if 'xnum' in kwargs:
            self.xnum = kwargs['xnum']
        if 'xmax' in kwargs:
            self.xmax = kwargs['xmax']
        if 'xstep' in kwargs:
            self.xstep = kwargs['xstep']
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

    def load_parameters(self, params, key=None):
        
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
    def template(self):
        """str: The template to use for generating calc.in files."""
        
        # Build universal content
        template = super().template

        # Build subset content
        template += self.system.template()
        template += self.gamma.template()
        template += self.elastic.template()
        template += self.defect.template()
        template += self.units.template()
        
        # Build calculation-specific content
        header = 'Run parameters'
        keys = [
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
        template += self._template_builder(header, keys)
        
        return template     
    
    @property
    def singularkeys(self):
        """list: Calculation keys that can have single values during prepare."""

        # Fetch universal key sets from parent
        universalkeys = super().singularkeys
        
        # Specify calculation-specific key sets 
        keys = (
            # Universal keys
            super().singularkeys

            # Subset keys
            + self.units.keyset

            # Calculation-specific keys
            + [
                
            ]
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
        keys = [
            self.system.keyset + self.elastic.keyset + self.gamma.keyset,
            self.defect.keyset,
            [
                'xmax',
                'xstep',
                'xnum',
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
        
        x = am.defect.pn_arctan_disregistry(xmax=self.xmax,
                                            xnum=self.xnum,
                                            xstep=self.xstep)[0]
        
        run_params['xmax'] = x.max()
        run_params['xnum'] = len(x)
        run_params['xstep'] = x[1]-x[0]
        run_params['min_cycles'] = self.minimize_cycles

        # Build results
        if self.status != 'finished':
            p_per_l_unit = f'{self.units.pressure_unit}/{self.units.length_unit}'
            p_l_unit = f'{self.units.pressure_unit}*{self.units.length_unit}'
            calc['semidiscrete-variational-Peierls-Nabarro'] = sdvpn = DM()
            sdvpn['parameter'] = params = DM()
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

        return model

    def load_model(self, model, name=None):

        # Load universal content
        super().load_model(model, name=name)
        calc = self.model[self.modelroot]

        # Load subset content
        #self.units.load_model(calc)
        self.system.load_model(calc)
        self.gamma.load_model(calc)
        self.defect.load_model(calc)
        self.elastic.load_model(calc)

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.halfwidth = uc.value_unit(run_params['halfwidth'])
        self.xmax = run_params['xmax']
        self.xnum = run_params['xnum']
        self.xstep = run_params['xstep']
        self.minimize_cycles = run_params['min_cycles']

        # Build results
        if self.status != 'finished':
            p_per_l_unit = f'{self.units.pressure_unit}/{self.units.length_unit}'
            p_l_unit = f'{self.units.pressure_unit}*{self.units.length_unit}'
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
         

    @staticmethod
    def mongoquery(name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None, lammps_version=None,
                   potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                   potential_key=None, potential_id=None, 
                   dislocation_key=None, dislocation_id=None):
        
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
        mquery.update(Dislocation.mongoquery(modelroot,
                                             dislocation_key=dislocation_key,
                                             dislocation_id=dislocation_id))

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
                  dislocation_key=None, dislocation_id=None):
        
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
        mquery.update(Dislocation.mongoquery(modelroot,
                                             dislocation_key=dislocation_key,
                                             dislocation_id=dislocation_id))

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
        #self.units.metadata(meta)
        self.system.metadata(meta)
        self.defect.metadata(meta)
        self.elastic.metadata(meta)
        self.gamma.metadata(meta)

        # Extract calculation-specific content
        meta['halfwidth'] = self.halfwidth
        meta['xmax'] = self.xmax
        meta['xnum'] = self.xnum
        meta['xstep'] = self.xstep
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
        
        # Extract results
        #if self.status == 'finished':      
            #meta['preln'] = self.sdvpn_solution.dislsol.preln
            #meta['K_tensor'] = self.sdvpn_solution.dislsol.K_tensor
            #meta['SDVPN_model'] = self.sdvpn_solution

        return meta

    @property
    def compare_terms(self):
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
    def compare_fterms(self):
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

    def isvalid(self):
        return self.system.family == self.defect.family
    
    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, iprPy_version=None,
                     atomman_version=None, script=None, branch=None,
                     status=None, lammps_version=None,
                     potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                     potential_key=None, potential_id=None, 
                     dislocation_key=None, dislocation_id=None):
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
            &Dislocation.pandasfilter(dataframe,
                                      dislocation_key=dislocation_key,
                                      dislocation_id=dislocation_id)

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
        self.system.calc_inputs(input_dict)
        self.defect.calc_inputs(input_dict)
        self.elastic.calc_inputs(input_dict)
        self.gamma.calc_inputs(input_dict)

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
        input_dict['min_method'] = self.minimize_style
        input_dict['min_options'] = self.minimize_options
        input_dict['min_cycles'] = self.minimize_cycles

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
            self.__sdvpn_solution = results_dict['SDVPN_solution']
            self.__energies = results_dict['minimization_energies']
            self.__disregistries = results_dict['disregistry_profiles']

        self._results(json=results_json)