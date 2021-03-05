# coding: utf-8
# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# iprPy imports
from .. import CalculationRecord
from ...tools import aslist
from ...input import subset

class CalculationPhonon(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-phonon'
    
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return [
            'script',
            
            'load_file',
            'load_options',
            'symbols',
            
            'potential_LAMMPS_key',
            
            'a_mult',
            'b_mult',
            'c_mult',
        ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
                'symmetryprecision':1e-7,
               }
    
    def buildcontent(self, input_dict, results_dict=None):
        """
        Builds a data model of the specified record style based on input (and
        results) parameters.
        
        Parameters
        ----------
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
        super().buildcontent(input_dict, results_dict=results_dict)

        # Load content after root
        calc = self.content[self.contentroot]
        calc['calculation']['run-parameter'] = run_params = DM()
        
        # Copy over sizemults (rotations and shifts)
        subset('atomman_systemmanipulate').buildcontent(calc, input_dict, results_dict=results_dict)
        
        run_params['displacementdistance'] = uc.model(input_dict['displacementdistance'],
                                                      input_dict['length_unit'])
        run_params['symmetryprecision'] = input_dict['symmetryprecision']
        run_params['strainrange'] = input_dict['strainrange']
        run_params['numstrains'] = input_dict['numstrains']
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            
            calc['band-structure'] = DM()

            for qpoints in results_dict['band_structure']['qpoints']:
                calc['band-structure'].append('qpoints', uc.model(qpoints))
                
            for distances in results_dict['band_structure']['distances']:
                calc['band-structure'].append('distances', uc.model(distances))
                
            for frequencies in results_dict['band_structure']['frequencies']:
                calc['band-structure'].append('frequencies', uc.model(frequencies))

            calc['density-of-states'] = DM()
            calc['density-of-states']['frequency'] = uc.model(results_dict['density_of_states']['frequency'], 'THz')
            calc['density-of-states']['total_dos'] = uc.model(results_dict['density_of_states']['total_dos'])
            calc['density-of-states']['projected_dos'] = uc.model(results_dict['density_of_states']['projected_dos'])

            calc['thermal-properties'] = DM()
            calc['thermal-properties']['temperature'] = uc.model(results_dict['thermal_properties']['temperature'], 'K')
            calc['thermal-properties']['Helmholtz'] = uc.model(results_dict['thermal_properties']['Helmholtz'], 'eV')
            calc['thermal-properties']['entropy'] = uc.model(results_dict['thermal_properties']['entropy'], 'J/K/mol')
            calc['thermal-properties']['heat_capacity_v'] = uc.model(results_dict['thermal_properties']['heat_capacity_v'], 'J/K/mol')

            for key in results_dict['thermal_properties']:
                calc['thermal-properties'][key] = uc.model(results_dict['thermal_properties'][key])

            if results_dict['qha_object'] is not None:
                calc['thermal-properties']['volume'] = uc.model(results_dict['thermal_properties']['volume'], 'angstrom^3')
                calc['thermal-properties']['thermal_expansion'] = uc.model(results_dict['thermal_properties']['thermal_expansion'])
                calc['thermal-properties']['Gibbs'] = uc.model(results_dict['thermal_properties']['Gibbs'], 'eV')
                calc['thermal-properties']['bulk_modulus'] = uc.model(results_dict['thermal_properties']['bulk_modulus'], 'GPa')
                calc['thermal-properties']['heat_capacity_p_numerical'] = uc.model(results_dict['thermal_properties']['heat_capacity_p_numerical'], 'J/K/mol')
                calc['thermal-properties']['heat_capacity_p_polyfit'] = uc.model(results_dict['thermal_properties']['heat_capacity_p_polyfit'], 'J/K/mol')
                calc['thermal-properties']['gruneisen'] = uc.model(results_dict['thermal_properties']['gruneisen'])
                
                calc['volume-scan'] = DM()
                calc['volume-scan']['volume'] = uc.model(results_dict['volume_scan']['volume'], 'angstrom^3')
                calc['volume-scan']['strain'] = uc.model(results_dict['volume_scan']['strain'])
                calc['volume-scan']['energy'] = uc.model(results_dict['volume_scan']['energy'], 'eV')

                calc['E0'] = uc.model(results_dict['E0'], 'eV')
                calc['B0'] = uc.model(results_dict['B0'], 'GPa')
                calc['B0prime'] = uc.model(results_dict['B0prime'], 'GPa')
                calc['V0'] = uc.model(results_dict['V0'], 'angstrom^3')

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
        
        params['displacementdistance'] = uc.value_unit(calc['calculation']['run-parameter']['displacementdistance'])
        params['symmetryprecision'] = calc['calculation']['run-parameter']['symmetryprecision']
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        subset('atomman_systemmanipulate').todict(calc, params, full=full, flat=flat)
        
        if full is True and params['status'] == 'finished':
        
            if flat is False:
                params['band_structure'] = {}

                for key in calc['band-structure']:
                    params['band_structure'][key] = []
                    for prop in calc['band-structure'][key]:
                        params['band_structure'][key].append(uc.value_unit(prop))
                
                params['density_of_states'] = {}
                for key in calc['density-of-states']:
                    params['density_of_states'][key] = uc.value_unit(calc['density-of-states'][key])
                
                thermal_properties = {}
                for key in calc['thermal-properties']:
                    thermal_properties[key] = uc.value_unit(calc['thermal-properties'][key])
                params['thermal_properties'] = pd.DataFrame(thermal_properties)

                if 'volume-scan' in calc:
                    volume_scan = {}
                    for key in calc['volume-scan']:
                        volume_scan[key] = uc.value_unit(calc['volume-scan'][key])
                    params['volume_scan'] = pd.DataFrame(volume_scan)
            
            if 'volume-scan' in calc:
                params['E0'] = uc.value_unit(calc['E0'])
                params['B0'] = uc.value_unit(calc['B0'])
                params['B0prime'] = uc.value_unit(calc['B0prime'])
                params['V0'] = uc.value_unit(calc['V0'])

        return params