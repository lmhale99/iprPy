# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset

class FreeSurface(Subset):
    """
    Defines interactions for input keys associated with specifying input/output
    units.
    """
    @property
    def templatekeys(self):
        """
        list : The input keys (without prefix) that appear in the input file.
        """
        return [
            'surface_file',
            'surface_cutboxvector',
        ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return self.templatekeys + [
            'surface_family',
            'surface_content',
            'a_uvw',
            'b_uvw',
            'c_uvw',
            'atomshift',
        ]
    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return self.preparekeys + [
            'surface_model',
        ]

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Free surface defect parameters'
        
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
        surface_file = input_dict.get(keymap['surface_file'], None)
        surface_content = input_dict.get(keymap['surface_content'], None)
        
        # Replace defect model with defect content if given
        if surface_content is not None:
            surface_file = surface_content
        
        # If defect model is given
        if surface_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('atomshift', 'a_uvw', 'b_uvw', 'c_uvw', 
                        'surface_cutboxvector'):
                assert keymap[key] not in input_dict, (keymap[key] + ' and '
                                                    + keymap['surface_model']
                                                    + ' cannot both be supplied')
            
            # Load defect model
            surface_model = DM(surface_file).find('free-surface')
                
            # Extract parameter values from defect model
            input_dict[keymap['surface_family']] = surface_model['system-family']
            input_dict[keymap['a_uvw']] = surface_model['calculation-parameter']['a_uvw']
            input_dict[keymap['b_uvw']] = surface_model['calculation-parameter']['b_uvw']
            input_dict[keymap['c_uvw']] = surface_model['calculation-parameter']['c_uvw']
            input_dict[keymap['atomshift']] = surface_model['calculation-parameter']['atomshift']
            input_dict[keymap['surface_cutboxvector']] = surface_model['calculation-parameter']['cutboxvector']
        
        # Set default parameter values if defect model not given
        else:
            surface_model = None
            input_dict[keymap['surface_cutboxvector']] = input_dict.get(keymap['surface_cutboxvector'], 'c')
            assert input_dict[keymap['surface_cutboxvector']] in ['a', 'b', 'c'], 'invalid surface_cutboxvector'
            
        # Save processed terms
        input_dict[keymap['surface_model']] = surface_model

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

        # Extract values
        keymap = self.keymap
        surface_model = input_dict[keymap['surface_model']]
        surface_family = input_dict.get(keymap['surface_family'],
                                        input_dict['family'])
        a_uvw = input_dict[keymap['a_uvw']]
        b_uvw = input_dict[keymap['b_uvw']]
        c_uvw = input_dict[keymap['c_uvw']]
        atomshift = input_dict[keymap['atomshift']]
        surface_cutboxvector = input_dict[keymap['surface_cutboxvector']]

        #Save defect parameters
        record_model[f'{modelprefix}free-surface'] = surf = DM()
        if surface_model is not None:
            surf['key'] = surface_model['key']
            surf['id'] = surface_model['id']
        else:
            surf['key'] = None
            surf['id'] = None
        surf['system-family'] = surface_family
        surf['calculation-parameter'] = cp = DM()
        cp['a_uvw'] = a_uvw
        cp['b_uvw'] = b_uvw
        cp['c_uvw'] = c_uvw
        cp['atomshift'] = atomshift
        cp['cutboxvector'] = surface_cutboxvector
        
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

        fs = record_model[f'{modelprefix}free-surface']
        params[f'{prefix}surface_key'] = fs['key']
        params[f'{prefix}surface_id'] = fs['id']