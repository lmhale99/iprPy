# coding: utf-8

# Standard Python libraries
from pathlib import Path
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from yabadaba import load_query

import atomman as am

# Local imports
from . import CalculationSubset
from ..input import boolean

class PointDefectParams():
    """Class for managing point defect parameters"""

    def __init__(self,
                 ptd_type: str = 'v',
                 atype: Optional[str] = None,
                 pos: Union[str, npt.ArrayLike] = '0.0 0.0 0.0',
                 db_vect: Union[str, npt.ArrayLike, None] = None,
                 scale: bool = False):
        """
        Define parameters for a point defect operation.

        Parameters
        ----------
        ptd_type: str, optional
            Indicates the point defect operation type: v, s, i, or db
        atype: int or None, optional
            Indicates the atom type of the defect atom added.  Used by
            ptd_type styles s, i and db.
        pos: str or array-like object, optional
            Gives the position where the point defect operation is
            performed.  For v, s, and db, this corresponds to the position of
            an existing atom to delete or modify.  For i, this corresponds to
            the position were the new interstitial atom is inserted.
        db_vect: str, array-like object or None
            The dumbbell vector to use for db style.  The atom at pos will be
            shifted by -db_vect and a new atom inserted at pos + db_vect.
        scale: bool
            Indicates if pos and db_vect are absolute Cartesian (False, default)
            or are scaled relative to the ucell.
        """
        self.ptd_type = ptd_type
        self.atype = atype
        self.pos = pos
        self.db_vect = db_vect
        self.scale = scale

    @property
    def ptd_type(self) -> str:
        """str: the type of point defect"""
        return self.__ptd_type

    @ptd_type.setter
    def ptd_type(self, val: str):
        if val.lower() in ['v', 'vacancy']:
            val = 'v'
        elif val.lower() in ['i', 'interstitial']:
            val = 'i'
        elif val.lower() in ['s', 'substitutional']:
            val = 's'
        elif val.lower() in ['d', 'db', 'dumbbell']:
            val = 'db'
        else:
            raise ValueError('invalid point defect type')
        self.__ptd_type = str(val)

    @property
    def atype(self) -> Optional[int]:
        """int or None: The int atype for the defect atom"""
        return self.__atype

    @atype.setter
    def atype(self, val: Optional[int]):
        if val is None:
            self.__atype = None
        else:
            self.__atype = int(val)

    @property
    def pos(self) -> Optional[np.ndarray]:
        """numpy.ndarray: The position of the defect atom"""
        return self.__pos

    @pos.setter
    def pos(self, val: Union[str, npt.ArrayLike, None]):
        if val is None:
            self.__pos = None
        else:
            if isinstance(val, str):
                val = np.array(val.strip().split(), dtype=float)
            else:
                val = np.asarray(val, dtype=float)
            assert val.shape == (3,)
            self.__pos = val

    @property
    def db_vect(self) -> Optional[np.ndarray]:
        """numpy.ndarray: The vector between dumbbell interstitial atoms"""
        return self.__db_vect

    @db_vect.setter
    def db_vect(self, val: Union[str, npt.ArrayLike, None]):
        if val is None:
            self.__db_vect = None
        else:
            if isinstance(val, str):
                val = np.array(val.strip().split(), dtype=float)
            else:
                val = np.asarray(val, dtype=float)
            assert val.shape == (3,)
            self.__db_vect = val

    @property
    def scale(self) -> bool:
        """bool: indicates if pos and db_vect are scaled by the unit cell box dimensions"""
        return self.__scale

    @scale.setter
    def scale(self, val: bool):
        self.__scale = boolean(val)

    def calc_inputs(self,
                    ucell: Optional[am.System] = None):
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

    def build_model(self) -> DM:
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

    def __init__(self,
                 parent,
                 prefix: str = '',
                 templateheader: Optional[str] = None,
                 templatedescription: Optional[str] = None):
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
    def param_file(self) -> Optional[Path]:
        """Path or None: The path to the point defect parameter file"""
        return self.__param_file

    @param_file.setter
    def param_file(self, val: Union[str, Path, None]):
        if val is None:
            self.__param_file = None
        else:
            self.__param_file = Path(val)

    @property
    def key(self) -> Optional[str]:
        """str or None: UUID key of the point defect parameter set"""
        return self.__key

    @key.setter
    def key(self, val: Optional[str]):
        if val is None:
            self.__key = None
        else:
            self.__key = str(val)

    @property
    def id(self) -> Optional[str]:
        """str or None: id of the point defect parameter set"""
        return self.__id

    @id.setter
    def id(self, val: Optional[str]):
        if val is None:
            self.__id = None
        else:
            self.__id = str(val)

    @property
    def params(self) -> list:
        """list: The point defect operation parameters to perform"""
        return self.__params

    @property
    def family(self) -> Optional[str]:
        """str or None: The prototype or reference crystal the point defect parameter set is for"""
        return self.__family

    @family.setter
    def family(self, val: Optional[str]):
        if val is None:
            self.__family = None
        else:
            self.__family = str(val)

    def set_values(self, **kwargs: any):
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

    def add_params(self,
                   ptd_type: str = 'v',
                   atype: Optional[int] = None,
                   pos: Union[str, npt.ArrayLike] ='0.0 0.0 0.0',
                   db_vect: Optional[str] = None,
                   scale: bool = False):
        """
        Create and add a point defect operation to the params list.

        Parameters
        ----------
        ptd_type: str, optional
            Indicates the point defect operation type: v, s, i, or db
        atype: int or None, optional
            Indicates the atom type of the defect atom added.  Used by
            ptd_type styles s, i and db.
        pos: str or array-like object, optional
            Gives the position where the point defect operation is
            performed.  For v, s, and db, this corresponds to the position of
            an existing atom to delete or modify.  For i, this corresponds to
            the position were the new interstitial atom is inserted.
        db_vect: str, array-like object or None
            The dumbbell vector to use for db style.  The atom at pos will be
            shifted by -db_vect and a new atom inserted at pos + db_vect.
        scale: bool
            Indicates if pos and db_vect are absolute Cartesian (False, default)
            or are scaled relative to the ucell.
        """

        self.params.append(PointDefectParams(ptd_type=ptd_type, atype=atype,
                                             pos=pos, db_vect=db_vect,
                                             scale=scale))

####################### Parameter file interactions ###########################

    def _template_init(self,
                       templateheader: Optional[str] = None,
                       templatedescription: Optional[str] = None):
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
    def templatekeys(self) -> dict:
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
    def preparekeys(self) -> list:
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
    def interpretkeys(self) -> list:
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

    def load_parameters(self, input_dict: dict):
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
            self.__params = []
            for cp in model.aslist('calculation-parameter'):
                self.add_params(**cp)

        # Set parameter values directly
        else:
            self.__model = None
            self.key = None
            self.id = None
            self.family = self.parent.system.family
            self.__params = []
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
    def modelroot(self) -> str:
        """str : The root element name for the subset terms."""
        baseroot = 'point-defect'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model: DM):
        """Loads subset attributes from an existing model."""
        ptd = model[self.modelroot]

        self.__model = None
        self.__param_file = None
        self.key = ptd['key']
        self.id = ptd['id']
        self.family = ptd['system-family']
        self.__params = []
        for cp in ptd.aslist('calculation-parameter'):
            self.add_params(**cp)

    def build_model(self,
                    model: DM,
                    **kwargs: any):
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

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""

        root = f'{self.parent.modelroot}.{self.modelroot}'

        return {
            'pointdefect_id': load_query(
                style='str_match',
                name=f'{self.prefix}pointdefect_id',
                path=f'{root}.id',
                description='search by point defect parameter set id'),
            'pointdefect_key': load_query(
                style='str_match',
                name=f'{self.prefix}pointdefect_key',
                path=f'{root}.key',
                description='search by point defect parameter set UUID key'),
            'pointdefect_family': load_query(
                style='str_match',
                name=f'{self.prefix}pointdefect_family',
                path=f'{root}.system-family',
                description='search by crystal prototype that the point defect parameter set is for'),
        }

########################## Metadata interactions ##############################

    def metadata(self, meta: dict):
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

    def calc_inputs(self, input_dict: dict):
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
