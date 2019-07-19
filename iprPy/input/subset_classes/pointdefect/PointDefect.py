# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset
from ...boolean import boolean

class PointDefect(Subset):
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
                    'pointdefect_file',
                    'pointdefect_type',
                    'pointdefect_atype',
                    'pointdefect_pos',
                    'pointdefect_dumbbell_vect',
                    'pointdefect_scale',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  self.templatekeys + [
                    'pointdefect_family',
                    'pointdefect_content',
                ]
    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'pointdefect_model',
                    'ucell',
                    'calculation_params',
                    'point_kwargs',
                ]

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Point defect parameters'
        
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
        pointdefect_file = input_dict.get(keymap['pointdefect_file'], None)
        pointdefect_content = input_dict.get(keymap['pointdefect_content'], None)
        
        # Replace defect model with defect content if given
        if pointdefect_content is not None:
            pointdefect_file = pointdefect_content
        
        # If defect model is given
        if pointdefect_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('pointdefect_type', 'pointdefect_atype', 'pointdefect_pos',
                        'pointdefect_dumbbell_vect', 'pointdefect_scale'):
                assert keymap[key] not in input_dict, (keymap[key] + ' and '
                                                    + keymap['pointdefect_file']
                                                    + ' cannot both be supplied')
            
            # Load defect model
            pointdefect_model = DM(pointdefect_file).find('point-defect')
            input_dict[keymap['pointdefect_family']] = pointdefect_model['system-family']
            # Save raw parameters
            calculation_params = pointdefect_model['calculation-parameter']
        
        # Build calculation_params for given values
        else:
            pointdefect_model = None
            calculation_params = DM()
            for key1, key2 in zip(('pointdefect_type', 'pointdefect_atype',
                                'pointdefect_pos', 'pointdefect_dumbbell_vect',
                                'pointdefect_scale'),
                                ('ptd_type', 'atype', 'pos', 'db_vect',
                                'scale')):
                if keymap[key1] in input_dict:
                    calculation_params[key2] = input_dict[keymap[key1]]
        
        # Save processed terms
        input_dict[keymap['pointdefect_model']] = pointdefect_model
        input_dict[keymap['calculation_params']] = calculation_params
        
        # Build point_kwargs from calculation_params
        if build is True:
            ucell = input_dict[keymap['ucell']]
            if not isinstance(calculation_params, (list, tuple)):
                calculation_params = [calculation_params]
            
            # Process parameters for running
            point_kwargs = []
            for raw in calculation_params:
                processed = {}
                
                scale = boolean(raw.get('scale', False))
                
                if 'ptd_type' in raw:
                    if   raw['ptd_type'].lower() in ['v', 'vacancy']:
                        processed['ptd_type'] = 'v'
                    elif raw['ptd_type'].lower() in ['i', 'interstitial']:
                        processed['ptd_type'] = 'i'
                    elif raw['ptd_type'].lower() in ['s', 'substitutional']:
                        processed['ptd_type'] = 's'
                    elif raw['ptd_type'].lower() in ['d', 'db', 'dumbbell']:
                        processed['ptd_type'] = 'db'  
                    else:
                        raise ValueError('invalid ptd_type')
                
                if 'atype' in raw:
                    processed['atype'] = int(raw['atype'])
                    
                if 'pos' in raw:
                    processed['pos'] = np.array(raw['pos'].strip().split(),
                                                dtype=float)
                    if scale is True:
                        processed['pos'] = ucell.unscale(processed['pos'])
                if 'db_vect' in raw:
                
                    processed['db_vect'] = np.array(raw['db_vect'].strip().split(),
                                                    dtype=float)
                    if scale is True:
                        processed['db_vect'] = ucell.unscale(processed['db_vect'])
                
                processed['scale'] = False
                
                point_kwargs.append(processed)
            
            # Save processed terms
            input_dict[keymap['point_kwargs']] = point_kwargs
        else:
            input_dict[keymap['point_kwargs']] = None

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
        pointdefect_model = input_dict[keymap['pointdefect_model']]
        pointdefect_family = input_dict.get(keymap['pointdefect_family'],
                                              input_dict['family'])
        calculation_params = input_dict[keymap['calculation_params']]

        # Save defect parameters
        record_model[f'{modelprefix}point-defect'] = ptd = DM()
        if pointdefect_model is not None:
            ptd['key'] = pointdefect_model['key']
            ptd['id'] =  pointdefect_model['id']
        ptd['system-family'] = pointdefect_family
        ptd['calculation-parameter'] = calculation_params
        
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

        ptd = record_model[f'{modelprefix}point-defect']
        params[f'{prefix}pointdefect_key'] = ptd['key']
        params[f'{prefix}pointdefect_id'] = ptd['id']