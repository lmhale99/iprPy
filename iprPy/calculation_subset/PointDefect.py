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
from ..input import termtodict, dicttoterm, boolean

class PointDefectParams():
    """Class for managing point defect parameters"""

    def __init__(self, ptd_type='v', atype=None, pos='0.0 0.0 0.0', db_vect=None,
                 scale=False):
    
        self.ptd_type = ptd_type
        self.atype = atype
        self.pos = pos
        self.db_vect = db_vect
        self.scale = scale

    @property
    def ptd_type(self):
        return self.__ptd_type

    @ptd_type.setter
    def ptd_type(self, value):
        if value.lower() in ['v', 'vacancy']:
            value = 'v'
        elif value.lower() in ['i', 'interstitial']:
            value = 'i'
        elif value.lower() in ['s', 'substitutional']:
            value = 's'
        elif value.lower() in ['d', 'db', 'dumbbell']:
            value = 'db'  
        else:
            raise ValueError('invalid point defect type')
        self.__ptd_type = str(value)

    @property
    def atype(self):
        return self.__atype

    @atype.setter
    def atype(self, value):
        if value is None:
            self.__atype = None
        else:
            self.__atype = int(value)

    @property
    def pos(self):
        return self.__pos

    @pos.setter
    def pos(self, value):
        if value is None:
            self.__pos = None
        elif isinstance(value, str):
            value = np.array(value.strip().split(), dtype=float)
        else:
            value = np.asarray(value, dtype=float)
        assert value.shape == (3,)
        self.__pos = value

    @property
    def db_vect(self):
        return self.__db_vect

    @db_vect.setter
    def db_vect(self, value):
        if value is None:
            self.__db_vect = None
        elif isinstance(value, str):
            value = np.array(value.strip().split(), dtype=float)
        else:
            value = np.asarray(value, dtype=float)
        assert value.shape == (3,)
        self.__db_vect = value

    @property
    def scale(self):
        return self.__scale

    @scale.setter
    def scale(self, value):
        self.__scale = boolean(value)

    def calc_inputs(self, ucell=None):
        """
        Builds parameters for atomman.defect.point()
        
        Parameters
        ----------
        ucell: atomman.System, optional
            An alternate (unit cell) system to use as the reference for scaling
            pos and db_vect if scale is True.  If scale is True and ucell is
            not given, then the vectors will be scaled using the full system
            as the reference.            
        """
        
        params = {}
        
        params['ptd_type'] = self.ptd_type
        
        if self.atype is not None:
            params['atype'] = self.atype        
        
        if self.scale is True and ucell is not None:
            params['pos'] = ucell.unscale(self.pos)
        else:
            params['pos'] = self.pos
        
        if self.db_vect is not None:
            if self.scale is True and ucell is not None:
                params['db_vect'] = ucell.unscale(self.db_vect)
            else:
                params['db_vect'] = self.db_vect        
        
        if ucell is not None:
            params['scale'] = False
        else:
            params['scale'] = self.scale

        return params

    def build_model(self):
        """Builds parameters for atomman.defect.point()"""
        params = DM()
        params['ptd_type'] = self.ptd_type
        if self.atype is not None:
            params['atype'] = self.atype
        params['pos'] = f'{self.pos[0]:.13} {self.pos[1]:.13} {self.pos[2]:.13}'
        if self.db_vect is not None:
            params['db_vect'] = f'{self.db_vect[0]:.13} {self.db_vect[1]:.13} {self.db_vect[2]:.13}'
        params['scale'] = self.scale

        return params

class PointDefect(CalculationSubset):
    """Handles calculation terms for point defect parameters"""

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

        self.param_file = None
        self.key = None
        self.id = None
        self.__params = []
        self.family = None
        self.__content = None
        self.__model = None

############################## Class attributes ################################

    @property
    def param_file(self):
        return self.__param_file

    @param_file.setter
    def param_file(self, value):
        if value is None:
            self.__param_file = None
        else:
            self.__param_file = Path(value)

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        if value is None:
            self.__key = None
        else:
            self.__key = str(value)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if value is None:
            self.__id = None
        else:
            self.__id = str(value)

    @property
    def params(self):
        return self.__params
    
    @property
    def family(self):
        return self.__family

    @family.setter
    def family(self, value):
        if value is None:
            self.__family = None
        else:
            self.__family = str(value)

    def set_values(self, **kwargs):
        """
        Allows for multiple class attribute values to be updated at once.

        Parameters
        ----------
        load_style : str, optional
            The style for atomman.load() to use.
        load_file : str, optional
            The path to the file to load.
        symbols : list or None, optional
            The list of interaction model symbols to associate with the atom
            types in the load file.  A value of None will default to the
            symbols listed in the load file if the style contains that
            information.
        load_options : dict, optional
            Any other atomman.load() keyword options to use when loading.
        load_content : str or DataModelDict, optional
            The contents of load_file.  Allows for ucell and symbols/family
            to be extracted without the file being accessible at the moment.
        box_parameters : list or None, optional
            A list of 3 orthorhombic box parameters or 6 trigonal box length
            and angle parameters to scale the loaded system by.  Setting a
            value of None will perform no scaling.
        family : str or None, optional
            The system's family identifier.  If None, then the family will be
            set according to the family value in the load file if it has one,
            or as the load file's name otherwise.
        """
        if 'param_file' in kwargs:
            self.param_file = kwargs['param_file']
        if 'key' in kwargs:
            self.key = kwargs['key']
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'family' in kwargs:
            self.family = kwargs['family']

    def add_params(self, ptd_type='v', atype=None, pos='0.0 0.0 0.0',
                   db_vect=None, scale=False):
        self.params.append(PointDefectParams(ptd_type=ptd_type, atype=atype,
                                             pos=pos, db_vect=db_vect,
                                             scale=scale))        

####################### Parameter file interactions ###########################

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return '# Point defect parameters'

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
        self.param_file = input_dict.get(keymap['pointdefect_file'], None)
        self.__content = input_dict.get(keymap['pointdefect_content'], None)
        
        # Replace defect model with defect content if given
        param_file = self.param_file
        if self.__content is not None:
            param_file = self.__content
        
        # Extract parameters from a file
        if param_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('pointdefect_type', 'pointdefect_atype', 'pointdefect_pos',
                        'pointdefect_dumbbell_vect', 'pointdefect_scale'):
                if keymap[key] in input_dict:
                    raise ValueError(f"{keymap[key]} and {keymap['pointdefect_file']} cannot both be supplied")
            
            # Load defect model
            self.__model = model = DM(param_file).find('point-defect')

            # Extract parameter values from defect model
            self.key = model['key']
            self.id = model['id']
            self.family = model['system-family']
            for cp in model.aslist('calculation-parameter'):
                self.add_params(**cp)
        
        # Set parameter values directly
        else:
            self.__model = None
            self.key = None
            self.id = None
            self.family = self.parent.system.family
            cp = {}
            for key1, key2 in zip(('pointdefect_type', 'pointdefect_atype',
                                'pointdefect_pos', 'pointdefect_dumbbell_vect',
                                'pointdefect_scale'),
                                ('ptd_type', 'atype', 'pos', 'db_vect',
                                'scale')):
                if keymap[key1] in input_dict:
                    cp[key2] = input_dict[keymap[key1]]
            self.add_params(**cp)

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        baseroot = 'point-defect'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        ptd = model[self.modelroot]

        self.__model = None
        self.__param_file = None
        self.key = ptd['key']
        self.id = ptd['id']
        self.family = ptd['system-family']

        for cp in ptd.aslist('calculation-parameter'):
            self.add_params(**cp)
        
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
        # Save defect parameters
        model[self.modelroot] = ptd = DM()
        ptd['key'] = self.key
        ptd['id'] = self.id
        ptd['system-family'] = self.family
        for params in self.params:
            ptd.append('calculation-parameter', params.build_model())
        
    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        prefix = self.prefix

        meta[f'{prefix}pointdefect_key'] = self.key
        meta[f'{prefix}pointdefect_id'] = self.id
        meta[f'{prefix}pointdefect_family'] = self.family

########################### Calculation interactions ##########################

    def calc_inputs(self, input_dict):

        if len(self.params) == 1:
            input_dict['point_kwargs'] = self.params[0].calc_inputs(self.parent.system.ucell)
        elif len(self.params) > 1:
            input_dict['point_kwargs'] = []
            for params in self.params:
                input_dict['point_kwargs'].append(params.calc_inputs(self.parent.system.ucell))
        else:
            raise ValueError('No point defect parameters set')

      
        