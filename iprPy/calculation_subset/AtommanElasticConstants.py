# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from datamodelbase import query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from . import CalculationSubset
from ..tools import dict_insert, aslist
from ..input import termtodict, dicttoterm, value

class AtommanElasticConstants(CalculationSubset):
    """Handles calculation terms for loading elastic constants using atomman"""
    
############################# Core properties #################################
     
    def __init__(self, parent, prefix='', templateheader=None,
                 templatedescription=None):
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
            a single record.
        templateheader : str, optional
            An alternate header to use in the template file for the subset.
        templatedescription : str, optional
            An alternate description of the subset for the templatedoc.
        """
        super().__init__(parent, prefix=prefix, templateheader=templateheader,
                         templatedescription=templatedescription)

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

    def _template_init(self, templateheader=None, templatedescription=None):
        """
        Sets the template header and description values.

        Parameters
        ----------
        templateheader : str, optional
            An alternate header to use in the template file for the subset.
        templatedescription : str, optional
            An alternate description of the subset for the templatedoc.
        """
        # Set default template header
        if templateheader is None:
            templateheader = 'Elastic Constants'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the computed elastic constants for the interatomic potential",
                "and crystal structure, relative to the loaded system's orientation.",
                "If the values are specified with the Voigt Cij terms and the system",
                "is in a standard setting for a crystal type, then only the unique",
                "Cij values for that crystal type are necessary.  If isotropic",
                "values are used, only two idependent parameters are necessary."])
        
        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self):
        """dict : The subset-specific input keys and their descriptions."""
                
        return  {
            'elasticconstants_file': ' '.join([
                "The path to a record containing the elastic constants to use.  If",
                "neither this or the individual Cij components (below) are given",
                "and load_style is 'system_model', this will be set to load_file."]),
            'C11':
                "The C11 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C12': 
                "The C12 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C13': 
                "The C13 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C14': 
                "The C14 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C15': 
                "The C15 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C16': 
                "The C16 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C22': 
                "The C22 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C23': 
                "The C23 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C24': 
                "The C24 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C25': 
                "The C25 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C26': 
                "The C26 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C33': 
                "The C33 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C34': 
                "The C34 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C35': 
                "The C35 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C36': 
                "The C36 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C44': 
                "The C44 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C45': 
                "The C45 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C46': 
                "The C46 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C55': 
                "The C55 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C56': 
                "The C56 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C66': 
                "The C66 component of the 6x6 Cij Voigt Cij elastic stiffness tensor (units of pressure).",
            'C_M': 
                "The isotropic P-wave modulus (units of pressure).",
            'C_lambda': 
                "The isotropic Lame's first parameter (units of pressure).",
            'C_mu': 
                "The isotropic shear modulus (units of pressure).",
            'C_E': 
                "The isotropic Young's modulus (units of pressure).",
            'C_nu': 
                "The isotropic Poisson's ratio (unitless).",
            'C_K': 
                "The isotropic bulk modulus (units of pressure)."
        }

    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  list(self.templatekeys.keys()) + [
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
        """str : The root element name for the subset terms."""
        baseroot = 'elastic-constants'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        try:
            c_model = DM([('elastic-constants', model[self.modelroot] )])
        except:
            self.__C = None
        else:
            self.__C = am.ElasticConstants(model=c_model)

    def build_model(self, model, **kwargs):
        """
        Adds the subset model to the parent model.
        
        Parameters
        ----------
        model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        kwargs : any
            Any options to pass on to dict_insert that specify where the subset
            content gets added to in the parent model.
        """
        # Save info on system file loaded
        c_model = self.C.model(unit=self.parent.units.pressure_unit)
        model[self.modelroot] = c_model['elastic-constants']

########################## Metadata interactions ##############################

    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        meta[f'{self.prefix}C'] = self.C
        if self.C is not None:
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
        """
        Generates calculation function input parameters based on the values
        assigned to attributes of the subset.

        Parameters
        ----------
        input_dict : dict
            The dictionary of input parameters to add subset terms to.
        """
        input_dict['C'] = self.C
