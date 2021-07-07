# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from . import CalculationSubset
from ..tools import dict_insert, aslist
from ..input import termtodict, dicttoterm, value

class AtommanElasticConstants(CalculationSubset):
    """Handles calculation terms for loading elastic constants using atomman"""
    
############################# Core properties #################################
     
    def __init__(self, parent, prefix=''):
        """
        Initializes a calculation record subset object.

        Parameters
        ----------
        parent : iprPy.calculation.Calculation
            The parent calculation object that the subset object is part of.
            This allows for the subset methods to access parameters set to the
            calculation itself or other subsets.
        prefix : str, optional
            An optional prefix to add to metadata field names to allow for
            differentiating between multiple subsets of the same style within
            a single record
        """
        super().__init__(parent, prefix=prefix)

        self.elasticconstants_file = None
        self.__elasticconstants_content = None
        self.__C = None

############################## Class attributes ################################
    
    @property
    def elasticconstants_file(self):
        return self.__elasticconstants_file

    @elasticconstants_file.setter
    def elasticconstants_file(self, value):
        if value is None:
            self.__elasticconstants_file = None
        else:
            self.__elasticconstants_file = Path(value)

    @property
    def elasticconstants_content(self):
        return self.__elasticconstants_content

    @property
    def C(self):
        return self.__C

    def set_values(self, **kwargs):
        pass

####################### Parameter file interactions ###########################

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return '# Elastic constants'

    @property
    def templatekeys(self):
        """list : The input keys (without prefix) that appear in the input file."""
        
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

    def load_parameters(self, input_dict):
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
        Ckey = keymap.get('Ckey', 'C')
        self.elasticconstants_file = input_dict.get(keymap['elasticconstants_file'], None)
        self.__elasticconstants_content = input_dict.get(keymap['elasticconstants_content'], None)
        
        # Replace model with content if given
        cij_file = self.elasticconstants_file
        if self.elasticconstants_content is not None:
            cij_file = self.elasticconstants_content
        
        # Pull out any single elastic constant terms
        Cdict = {}
        for key in input_dict:
            keyhead = key[:len(Ckey)]
            keytail = key[len(Ckey):]
            if keyhead == Ckey:
                if keytail[0] == '_':
                    Cdict[keytail[1:]] = value(input_dict, key, default_unit=self.parent.units.pressure_unit)
                else:
                    Cdict['C'+keytail] = value(input_dict, key, default_unit=self.parent.units.pressure_unit)
        
        # Load from cij file
        if cij_file is not None:
            if len(Cdict) != 0:
                raise ValueError(f"{keyhead}ij values and {keymap['elasticconstants_file']} cannot both be specified.")
            
            self.__C = am.ElasticConstants(model=cij_file)
        
        # Load from explicit parameters
        elif len(Cdict) > 0:
            self.__C = am.ElasticConstants(**Cdict)
        
        # Check load_file for elastic constants
        else:
            load_file = self.parent.system.load_file
            if self.parent.system.load_content is not None:
                load_file = self.parent.system.load_content
            
            self.__C = am.ElasticConstants(model=load_file)

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        baseroot = 'elastic-constants'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        c_model = DM([('elastic-constants', model[self.modelroot] )])
        self.__C = am.ElasticConstants(model=c_model)

    def build_model(self, model, **kwargs):
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
        # Save info on system file loaded
        c_model = self.C.model(unit=self.parent.units.pressure_unit)
        model[self.modelroot] = c_model['elastic-constants']

    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        meta[f'{self.prefix}C'] = self.C
        
        meta[f'{self.prefix}C11'] = self.C.Cij[0,0]
        meta[f'{self.prefix}C12'] = self.C.Cij[0,1]
        meta[f'{self.prefix}C13'] = self.C.Cij[0,2]
        meta[f'{self.prefix}C14'] = self.C.Cij[0,3]
        meta[f'{self.prefix}C15'] = self.C.Cij[0,4]
        meta[f'{self.prefix}C16'] = self.C.Cij[0,5]
        meta[f'{self.prefix}C22'] = self.C.Cij[1,1]
        meta[f'{self.prefix}C23'] = self.C.Cij[1,2]
        meta[f'{self.prefix}C24'] = self.C.Cij[1,3]
        meta[f'{self.prefix}C25'] = self.C.Cij[1,4]
        meta[f'{self.prefix}C26'] = self.C.Cij[1,5]
        meta[f'{self.prefix}C33'] = self.C.Cij[2,2]
        meta[f'{self.prefix}C34'] = self.C.Cij[2,3]
        meta[f'{self.prefix}C35'] = self.C.Cij[2,4]
        meta[f'{self.prefix}C36'] = self.C.Cij[2,5]
        meta[f'{self.prefix}C44'] = self.C.Cij[3,3]
        meta[f'{self.prefix}C45'] = self.C.Cij[3,4]
        meta[f'{self.prefix}C46'] = self.C.Cij[3,5]
        meta[f'{self.prefix}C55'] = self.C.Cij[4,4]
        meta[f'{self.prefix}C56'] = self.C.Cij[4,5]
        meta[f'{self.prefix}C66'] = self.C.Cij[5,5]

########################### Calculation interactions ##########################

    def calc_inputs(self, input_dict):

        input_dict['C'] = self.C
