# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset
from ... import value
from ....tools import aslist

class AtommanElasticConstants(Subset):
    """
    Defines interactions for input keys associated with specifying input/output
    units.
    """
    @property
    def templatekeys(self):
        """
        list : The input keys (without prefix) that appear in the input file.
        """
        return  [
                    'elasticconstants_file',
                    'C11',
                    'C12',
                    'C13',
                    'C14',
                    'C15',
                    'C16',
                    'C22',
                    'C23',
                    'C24',
                    'C25',
                    'C26',
                    'C33',
                    'C34',
                    'C35',
                    'C36',
                    'C44',
                    'C45',
                    'C46',
                    'C55',
                    'C56',
                    'C66',
                    'C_M',
                    'C_lambda',
                    'C_mu',
                    'C_E',
                    'C_nu',
                    'C_K',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  self.templatekeys + [
                    'elasticconstants_content',
                ]
    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'load_file',
                    'load_content',
                    'pressure_unit',
                    'C',
                ]

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Elastic constants'
        
        return super().template(header=header)

    def interpret(self, input_dict, build=True):
        """
        Interprets calculation parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary containing input parameter key-value pairs.
        """

        # Set default keynames
        keymap = self.keymap
        
        # Extract input values and assign default values
        C = None
        Ckey = keymap.get('Ckey', 'C')
        elasticconstants_file = input_dict.get(keymap['elasticconstants_file'], None)
        elasticconstants_content = input_dict.get(keymap['elasticconstants_content'], None)
        load_file = input_dict.get(keymap['load_file'], None)
        load_content = input_dict.get(keymap['load_content'], None)
        pressure_unit = input_dict[keymap['pressure_unit']]
        
        # Replace model with content if given
        if elasticconstants_content is not None:
            elasticconstants_file = elasticconstants_content
        
        # Pull out any single elastic constant terms
        Cdict = {}
        for key in input_dict:
            keyhead = key[:len(Ckey)]
            keytail = key[len(Ckey):]
            if keyhead == Ckey:
                if keytail[0] == '_':
                    Cdict[keytail[1:]] = value(input_dict, key, default_unit=pressure_unit)
                else:
                    Cdict['C'+keytail] = value(input_dict, key, default_unit=pressure_unit)
        
        # If model is given
        if elasticconstants_file is not None:
            assert len(Cdict) == 0, (keyhead + 'ij values and '
                                    + keymap['elasticconstants_file']
                                    + ' cannot both be specified.')
            
            if build is True:
                C = am.ElasticConstants(model=DM(elasticconstants_file))
        
        # Else if individual Cij terms are given
        elif len(Cdict) > 0:
            if build is True:
                C = am.ElasticConstants(**Cdict)
        
        # Else check load_file for elastic constants
        else:
            if build is True:
                if load_content is not None:
                    load_file = load_content
                
                C = am.ElasticConstants(model=DM(load_file))
        
        # Save processed terms
        input_dict[keymap['C']] = C

    def buildcontent(self, record_model, input_dict, results_dict=None):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        record_model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        input_dict : dict
            Dictionary of all input parameter terms.
        results_dict : dict, optional
            Dictionary containing any results produced by the calculation.
        """
        
        prefix = self.prefix
        modelprefix = prefix.replace('_', '-')

        # Extract terms
        keymap = self.keymap
        C = input_dict[keymap['C']]
        pressure_unit = input_dict[keymap['pressure_unit']]

        # Save info on system file loaded
        c_model = C.model(unit=pressure_unit)
        record_model[f'{modelprefix}elastic-constants'] = c_model['elastic-constants']            
        
    def todict(self, record_model, params, full=True, flat=False):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        record_model : DataModelDict.DataModelDict
            The record content (after root element) to interpret.
        params : dict
            The dictionary to add the interpreted content to
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
        """
        prefix = self.prefix
        modelprefix = prefix.replace('_', '-')

        c_model = DM()
        c_model['elastic-constants'] = record_model[f'{modelprefix}elastic-constants']

        if flat is True:
            for C in c_model['elastic-constants'].aslist('C'):
                params['C'+str(C['ij'][0])+str(C['ij'][2])] = uc.value_unit(C['stiffness'])
        else:
            try:
                params['C'] = am.ElasticConstants(model=calc)
            except:
                params['C'] = 'Invalid'