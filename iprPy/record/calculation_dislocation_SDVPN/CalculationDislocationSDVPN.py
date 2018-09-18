# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.defect import pn_arctan_disregistry

# iprPy imports
from ... import __version__ as iprPy_version
from .. import Record
from ...tools import aslist

class CalculationDislocationSDVPN(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-dislocation-SDVPN'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-calculation-dislocation-SDVPN.xsd')
    
    @property
    def compare_terms(self):
        """
        list of str: The default terms used by isnew() for comparisons.
        """
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
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        return [
                'xmax',
                'xstep',
                'cutofflongrange',
                'K11', 'K12', 'K13', 'K22', 'K23', 'K33',
                'tau11', 'tau12', 'tau13', 'tau22', 'tau23', 'tau33',
                'beta11', 'beta12', 'beta13', 'beta22', 'beta23', 'beta33',
                'alpha1',
               ]
    
    def buildcontent(self, script, input_dict, results_dict=None):
        """
        Builds a data model of the specified record style based on input (and
        results) parameters.
        
        Parameters
        ----------
        script : str
            The name of the calculation script used.
        input_dict : dict
            Dictionary of all input parameter terms.
        results_dict : dict, optional
            Dictionary containing any results produced by the calculation.
            
        Returns
        -------
        DataModelDict
            Data model consistent with the record's schema format.
        
        Raises
        ------
        AttributeError
            If buildcontent is not defined for record style.
        """
        # Create the root of the DataModelDict
        output = DM()
        output[self.contentroot] = calc = DM()
        
        # Assign uuid
        calc['key'] = input_dict['calc_key']
        
        # Save calculation parameters
        calc['calculation'] = DM()
        calc['calculation']['iprPy-version'] = iprPy_version
        calc['calculation']['atomman-version'] = am.__version__
        
        calc['calculation']['script'] = script
        calc['calculation']['run-parameter'] = run_params = DM()
        run_params['halfwidth'] = uc.model(input_dict['halfwidth'],
                                           input_dict['length_unit'])
        
        x = pn_arctan_disregistry(xmax=input_dict['xmax'],
                                  xnum=input_dict['xnum'],
                                  xstep=input_dict['xstep'])[0]
        
        run_params['xmax'] = x.max()
        run_params['xnum'] = len(x)
        run_params['xstep'] = x[1]-x[0]
        run_params['min_cycles'] = input_dict['minimize_numcycles']

        # Save info on system file loaded
        calc['system-info'] = DM()
        calc['system-info']['family'] = input_dict['family']
        calc['system-info']['artifact'] = DM()
        calc['system-info']['artifact']['file'] = input_dict['load_file']
        calc['system-info']['artifact']['format'] = input_dict['load_style']
        calc['system-info']['artifact']['load_options'] = input_dict['load_options']
        calc['system-info']['symbol'] = input_dict['symbols']
        
        #Save defect parameters
        calc['dislocation-monopole'] = disl = DM()
        if input_dict['dislocation_model'] is not None:
            disl['key'] = input_dict['dislocation_model']['key']
            disl['id'] = input_dict['dislocation_model']['id']
            disl['character'] = input_dict['dislocation_model']['character']
            disl['Burgers-vector'] = input_dict['dislocation_model']['Burgers-vector']
            disl['slip-plane'] = input_dict['dislocation_model']['slip-plane']
            disl['line-direction'] = input_dict['dislocation_model']['line-direction']
        
        disl['system-family'] = input_dict['family']
        disl['calculation-parameter'] = cp = DM()
        cp['a_uvw'] = input_dict['a_uvw']
        cp['b_uvw'] = input_dict['b_uvw']
        cp['c_uvw'] = input_dict['c_uvw']
        cp['atomshift'] = input_dict['atomshift']
        cp['burgersvector'] = input_dict['dislocation_burgersvector']
        
        calc['gamma-surface'] = DM()
        calc['gamma-surface']['calc_key'] = os.path.splitext(
                                             os.path.basename(
                                              input_dict['gammasurface_file']))[0]
        
        calc['stress-state'] = uc.model(input_dict['tau'], input_dict['pressure_unit'])
        
        if results_dict is None:
            calc['status'] = 'not calculated'
            
            # Fill in model input parameters
            calc['semidiscrete-variational-Peierls-Nabarro'] = sdvpn = DM()
            sdvpn['parameter'] = params = DM()
            params['tau'] = uc.model(input_dict['tau'],
                                     input_dict['pressure_unit'])
            params['alpha'] = uc.model(input_dict['alpha'],
                                       input_dict['pressure_unit'] + '/'
                                       + input_dict['length_unit'])
            params['beta'] = uc.model(input_dict['beta'],
                                      input_dict['pressure_unit'] + '*'
                                      + input_dict['length_unit'])
            params['cdiffelastic'] = input_dict['cdiffelastic']
            params['cdiffsurface'] = input_dict['cdiffsurface']
            params['cdiffstress'] = input_dict['cdiffstress']
            params['cutofflongrange'] = uc.model(input_dict['cutofflongrange'],
                                                 input_dict['length_unit'])
            params['fullstress'] = input_dict['fullstress']
            params['min_method'] = input_dict['minimize_style']
            params['min_options'] = input_dict['minimize_options']
            
        else:
            c_model = input_dict['C'].model(unit=input_dict['pressure_unit'])
            calc['elastic-constants'] = c_model['elastic-constants']
            
            pnsolution = results_dict['SDVPN_solution']
            pnmodel = pnsolution.model(length_unit=input_dict['length_unit'],
                                       energy_unit=input_dict['energy_unit'],
                                       pressure_unit=input_dict['pressure_unit'],
                                       include_gamma=False)
            calc['semidiscrete-variational-Peierls-Nabarro'] = pnmodel['semidiscrete-variational-Peierls-Nabarro']
            
            e_per_l_unit = input_dict['energy_unit'] + '/' + input_dict['length_unit']
            calc['misfit-energy'] = uc.model(pnsolution.misfit_energy(), e_per_l_unit)
            calc['elastic-energy'] = uc.model(pnsolution.elastic_energy(), e_per_l_unit)
            calc['long-range-energy'] = uc.model(pnsolution.longrange_energy(), e_per_l_unit)
            calc['stress-energy'] = uc.model(pnsolution.stress_energy(), e_per_l_unit)
            calc['surface-energy'] = uc.model(pnsolution.surface_energy(), e_per_l_unit)
            calc['nonlocal-energy'] = uc.model(pnsolution.nonlocal_energy(), e_per_l_unit)
            calc['total-energy'] = uc.model(pnsolution.total_energy(), e_per_l_unit)
            calc['total-energy-per-cycle'] = uc.model(results_dict['minimization_energies'], e_per_l_unit)
        
        self.content = output
    
    def todict(self, full=True, flat=False):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        full : bool, optional
            Flag used by the calculation records.  A True value will include
            terms for both the calculation's input and results, while a value
            of False will only include input terms (Default is True).
        flat : bool, optional
            Flag affecting the format of the dictionary terms.  If True, the
            dictionary terms are limited to having only str, int, and float
            values, which is useful for comparisons.  If False, the term
            values can be of any data type, which is convenient for analysis.
            (Default is False).
            
        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        
        calc = self.content[self.contentroot]
        params = {}
        params['key'] = calc['key']
        params['script'] = calc['calculation']['script']
        params['iprPy_version'] = calc['calculation']['iprPy-version']
        params['atomman_version'] = calc['calculation']['atomman-version']
        
        rp = calc['calculation']['run-parameter']
        params['halfwidth'] = uc.value_unit(rp['halfwidth'])
        params['xmax'] = rp['xmax']
        params['xnum'] = rp['xnum']
        params['xstep'] = rp['xstep']
        
        params['load_file'] = calc['system-info']['artifact']['file']
        params['load_style'] = calc['system-info']['artifact']['format']
        params['load_options'] = calc['system-info']['artifact']['load_options']
        params['family'] = calc['system-info']['family']
        symbols = aslist(calc['system-info']['symbol'])
        
        params['dislocation_key'] = calc['dislocation-monopole']['key']
        params['dislocation_id'] = calc['dislocation-monopole']['id']
        
        params['gammasurface_calc_key'] = calc['gamma-surface']['calc_key']
        
        pnp = calc['semidiscrete-variational-Peierls-Nabarro']['parameter']
        try:
            K_tensor = uc.value_unit(pnp['K_tensor'])
        except:
            K_tensor = np.nan
        tau = uc.value_unit(pnp['tau'])
        alpha = uc.value_unit(pnp['alpha'])
        beta = uc.value_unit(pnp['beta'])
        params['cdiffelastic'] = pnp['cdiffelastic']
        params['cdiffsurface'] = pnp['cdiffsurface']
        params['cdiffstress'] = pnp['cdiffstress']
        params['cutofflongrange'] = uc.value_unit(pnp['cutofflongrange'])
        params['fullstress'] = pnp['fullstress']
        params['min_method'] = pnp['min_method']
        params['min_options'] = pnp['min_options']
        
        if flat is True:
            params['symbols'] = ' '.join(symbols)
            for i in range(3):
                for j in range(i,3):
                    try:
                        params['K'+str(i+1)+str(j+1)] = K_tensor[i,j]
                    except:
                        params['K'+str(i+1)+str(j+1)] = np.nan
                    params['tau'+str(i+1)+str(j+1)] = tau[i,j]
                    params['beta'+str(i+1)+str(j+1)] = beta[i,j]
            if not isinstance(alpha, list):
                alpha = [alpha]
            for i in range(len(alpha)):
                params['alpha'+str(i+1)] = alpha[i]
        else:
            params['symbols'] = symbols
            params['K_tensor'] = K_tensor
            params['tau'] = tau
            params['alpha'] = alpha
            params['beta'] = beta
        
        params['status'] = calc.get('status', 'finished')
        
        if full is True:
            if params['status'] == 'error':
                params['error'] = calc['error']
            
            elif params['status'] == 'not calculated':
                pass
            else:
                if flat is True:
                    pass
                else:
                    try:
                        params['C'] = am.ElasticConstants(model=calc)
                    except:
                        params['C'] = np.nan
                    if True:
                        params['SDVPN_model'] = DM()
                        params['SDVPN_model']['semidiscrete-variational-Peierls-Nabarro'] = calc.find('semidiscrete-variational-Peierls-Nabarro')
                    else:
                        params['SDVPN_model'] = np.nan
        
        return params