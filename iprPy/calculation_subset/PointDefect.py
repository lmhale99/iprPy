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
        else:
            if isinstance(value, str):
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
        else:
            if isinstance(value, str):
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
            a single record
        templateheader : str, optional
            An alternate header to use in the template file for the subset.
        templatedescription : str, optional
            An alternate description of the subset for the templatedoc.
        """
        super().__init__(parent, prefix=prefix, templateheader=templateheader,
                         templatedescription=templatedescription)

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
        param_file : str, optional
            The path to a file that fully defines the input parameters for
            a specific defect type.
        key : str, optional
            The UUID4 unique key associated with the defect parameter set.
        id : str, optional
            The unique id associated with the defect parameter set.
        family : str or None, optional
            The system's family identifier that the defect is defined for.
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
            templateheader = 'Point Defect'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the parameter set that defines a point defect."])
        
        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self):
        """dict : The subset-specific input keys and their descriptions."""
        
        return  {
            'pointdefect_file': ' '.join([
                "The path to a point_defect record file that contains input",
                "parameters associated with a specific point defect or a set",
                "of point defects."]),
            'pointdefect_type': ' '.join([
                "Indicates which type of point defect to generate.",
                "'v' or 'vacancy' for a vacancy,",
                "'i' or 'interstitial' for a position-based interstitial,",
                "'s' or 'substitutional' for a substitutional, and",
                "'d', 'db' or 'dumbbell' for a dumbbell interstitial."]),
            'pointdefect_atype': ' '.join([
                "Indicates the integer atom type to assign to an interstitial,",
                "substitutional, or dumbbell interstitial atom."]),
            'pointdefect_pos': ' '.join([
                "Indicates the position where the point defect is to be placed.",
                "For the interstitial type, this cannot correspond to a current",
                "atom's position. For the other styles, this must correspond to a",
                "current atom's position."]),
            'pointdefect_dumbbell_vect': ' '.join([
                "Specifies the dumbbell vector to use for a dumbbell interstitial.",
                "The atom defined by pointdefect_pos is shifted by",
                "-pointdefect_dumbbell_vect, and the inserted interstitial atom is",
                "placed at pointdefect_pos + pointdefect_dumbbell_vect."]),
            'pointdefect_scale': ' '.join([
                "Boolean indicating if pointdefect_pos and pointdefect_dumbbell_vect",
                "are taken as absolute Cartesian vectors, or taken as scaled values",
                "relative to the loaded system. Default value is False."]),
        }
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  list(self.templatekeys.keys()) + [
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
        """str : The root element name for the subset terms."""
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
        Adds the subset model to the parent model.
        
        Parameters
        ----------
        model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        kwargs : any
            Any options to pass on to dict_insert that specify where the subset
            content gets added to in the parent model.
        """
        # Save defect parameters
        model[self.modelroot] = ptd = DM()
        ptd['key'] = self.key
        ptd['id'] = self.id
        ptd['system-family'] = self.family
        for params in self.params:
            ptd.append('calculation-parameter', params.build_model())


    def mongoquery(self, pointdefect_key=None, pointdefect_id=None,
                   pointdefect_family=None, **kwargs):
        """
        Generate a query to parse records with the subset from a Mongo-style
        database.
        
        Parameters
        ----------
        pointdefect_id : str
            The id associated with a point defect parameter set.
        pointdefect_key : str
            The key associated with a point defect parameter set.
        pointdefect_family : str
            The "family" crystal structure/prototype that the point defect
            is defined for.
        kwargs : any
            The parent query terms and values ignored by the subset.

        Returns
        -------
        dict
            The Mongo-style find query terms.
        """
        # Init query and set root paths
        mquery = {}
        parentroot = f'content.{self.parent.modelroot}'
        root = f'{parentroot}.{self.modelroot}'
        runparam_prefix = f'{parentroot}.calculation.run-parameter.{self.modelprefix}'

        # Build query terms
        query.str_match.mongo(mquery, f'{root}.point-defect.key', pointdefect_key)
        query.str_match.mongo(mquery, f'{root}.point-defect.id', pointdefect_id)
        query.str_match.mongo(mquery, f'{root}.system-family', pointdefect_family)

        # Return query dict
        return mquery

    def cdcsquery(self, pointdefect_key=None, pointdefect_id=None,
                  pointdefect_family=None, **kwargs):
        """
        Generate a query to parse records with the subset from a CDCS-style
        database.
        
        Parameters
        ----------
        pointdefect_id : str
            The id associated with a point defect parameter set.
        pointdefect_key : str
            The key associated with a point defect parameter set.
        pointdefect_family : str
            The "family" crystal structure/prototype that the point defect
            is defined for.
        kwargs : any
            The parent query terms and values ignored by the subset.
        
        Returns
        -------
        dict
            The CDCS-style find query terms.
        """
        # Init query and set root paths
        mquery = {}
        parentroot = self.parent.modelroot
        root = f'{parentroot}.{self.modelroot}'
        runparam_prefix = f'{parentroot}.calculation.run-parameter.{self.modelprefix}'
        
        # Build query terms
        query.str_match.mongo(mquery, f'{root}.point-defect.key', pointdefect_key)
        query.str_match.mongo(mquery, f'{root}.point-defect.id', pointdefect_id)
        query.str_match.mongo(mquery, f'{root}.system-family', pointdefect_family)

        # Return query dict
        return mquery      

########################## Metadata interactions ##############################

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

    def pandasfilter(self, dataframe, pointdefect_key=None,
                     pointdefect_id=None, pointdefect_family=None, **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
        pointdefect_id : str
            The id associated with a point defect parameter set.
        pointdefect_key : str
            The key associated with a point defect parameter set.
        pointdefect_family : str
            The "family" crystal structure/prototype that the point defect
            is defined for.
        kwargs : any
            The parent query terms and values ignored by the subset.

        Returns
        -------
        pandas.Series of bool
            True for each entry where all filter terms+values match, False for
            all other entries.
        """
        prefix = self.prefix
        matches = (
            query.str_match.pandas(dataframe, f'{prefix}pointdefect_key',
                                   pointdefect_key)
            &query.str_match.pandas(dataframe, f'{prefix}pointdefect_id',
                                    pointdefect_id)
            &query.str_match.pandas(dataframe, f'{prefix}pointdefect_family',
                                    pointdefect_family)
        )
        return matches

    

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
        if len(self.params) == 1:
            input_dict['point_kwargs'] = self.params[0].calc_inputs(self.parent.system.ucell)
        elif len(self.params) > 1:
            input_dict['point_kwargs'] = []
            for params in self.params:
                input_dict['point_kwargs'].append(params.calc_inputs(self.parent.system.ucell))
        else:
            raise ValueError('No point defect parameters set')

      
        