# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.defect import pn_arctan_disregistry

# iprPy imports
from .. import CalculationRecord
from ...tools import aslist
from ...input import subset

class CalculationDislocationSDVPN(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-dislocation-SDVPN'
    
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
        dict: The terms to compare values using a tolerance.
        """
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
        # Build universal content
        super().buildcontent(script, input_dict, results_dict=results_dict)

        # Load content after root
        calc = self.content[self.contentroot]
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
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
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
        calc['gamma-surface']['calc_key'] = Path(input_dict['gammasurface_file']).stem
        
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
        
        # Extract universal content
        params = super().todict(full=full, flat=flat)
        calc = self.content[self.contentroot]
        
        rp = calc['calculation']['run-parameter']
        params['halfwidth'] = uc.value_unit(rp['halfwidth'])
        params['xmax'] = rp['xmax']
        params['xnum'] = rp['xnum']
        params['xstep'] = rp['xstep']
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        
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
            params['K_tensor'] = K_tensor
            params['tau'] = tau
            params['alpha'] = alpha
            params['beta'] = beta
        
        if full is True and params['status'] == 'finished':
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