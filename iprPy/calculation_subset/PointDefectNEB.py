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
import atomman.unitconvert as uc

# Local imports
from .PointDefect import PointDefect
from ..input import boolean

class PointDefectNEB(PointDefect):
    """Handles calculation terms for point defect mobility parameters"""

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

        self.neb_pos1 = None
        self.neb_pos2 = None
        self.neb_scale = False
        self.neb_symbol = None

############################## Class attributes ################################

    @property
    def neb_pos1(self) -> Optional[np.ndarray]:
        """numpy.ndarray: Position(s) of the NEB atom(s) for the first replica"""
        return self.__neb_pos1

    @neb_pos1.setter
    def neb_pos1(self, val: Union[str, npt.ArrayLike]):
        if val is None:
            self.__neb_pos1 = None
        else:
            if isinstance(val, str):
                val = np.array(val.strip().split(), dtype=float)
            else:
                val = np.asarray(val, dtype=float)
            try:
                val = val.reshape((-1, 3))
            except ValueError as e:
                raise ValueError('neb_pos1 needs (N,3) values') from e
            self.__neb_pos1 = val

    @property
    def neb_pos2(self) -> Optional[np.ndarray]:
        """numpy.ndarray: Position(s) of the NEB atom(s) for the last replica"""
        return self.__neb_pos2

    @neb_pos2.setter
    def neb_pos2(self, val: Union[str, npt.ArrayLike]):
        if val is None:
            self.__neb_pos2 = None
        else:
            if isinstance(val, str):
                val = np.array(val.strip().split(), dtype=float)
            else:
                val = np.asarray(val, dtype=float)
            try:
                val = val.reshape((-1, 3))
            except ValueError as e:
                raise ValueError('neb_pos2 needs (N,3) values') from e
            self.__neb_pos2 = val

    @property
    def neb_scale(self) -> bool:
        """bool: True indicates neb_pos1 and neb_pos2 are relative to the loaded ucell"""
        return self.__neb_scale
    
    @neb_scale.setter
    def neb_scale(self, val: Union[str, bool]):
        self.__neb_scale = boolean(val)

    @property
    def neb_symbol(self) -> Optional[list]:
        """list or None: Symbol model(s) to assign to the NEB atom(s)"""
        return self.__neb_symbol
    
    @neb_symbol.setter
    def neb_symbol(self, val: Union[str, list, None]):
        if isinstance(val, str):
            self.__neb_symbol = val.split(' ')
        elif val is None:
            self.__neb_symbol = None
        else:
            self.__neb_symbol = list(val)

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
        neb_pos1 : str or array-like, optional
            The position(s) for the NEB-controlled atoms in the first replica.
        neb_pos2 : str or array-like, optional
            The position(s) for the NEB-controlled atoms in the last replica.
        neb_scale : str or bool, optional
            True indicates that neb_pos values are relative to the loaded ucell.
        neb_symbol : str or list, optional
            The potential symbol model(s) to assign to the NEB atoms.
        """
        # Call super to set point defect content
        super().set_values(**kwargs)

        # Set neb values
        if 'neb_pos1' in kwargs:
            self.neb_pos1 = kwargs['neb_pos1']
        if 'neb_pos2' in kwargs:
            self.neb_pos2 = kwargs['neb_pos2']
        if 'neb_scale' in kwargs:
            self.neb_scale = kwargs['neb_scale']
        if 'neb_symbol' in kwargs:
            self.neb_symbol = kwargs['neb_symbol']

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
            templateheader = 'Point Defect NEB'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the parameter set for a NEB point defect calculation."])

        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self) -> dict:
        """dict : The subset-specific input keys and their descriptions."""
        # Start dict with pointdefectneb_file
        d = {
            'pointdefectneb_file': ' '.join([
                "The path to a point_defect_neb record file that contains input",
                "parameters associated with a specific NEB point defect",
                "calculation configuration"]),
        }
        
        # Add point defect templatekeys without pointdefect_file
        pointdefect_templatekeys = super().templatekeys
        del pointdefect_templatekeys['pointdefect_file']
        d.update(pointdefect_templatekeys)

        # Define and add the neb keys
        d.update({
            'neb_pos1': ' '.join([
                'The position(s) for the NEB-controlled atoms in the first replica.',
                'Specify this as space-delimited float values where every three',
                'subsequent values represent the x y z coordinates of an atom.'
            ]),
            'neb_pos2': ' '.join([
                'The position(s) for the NEB-controlled atoms in the last replica.',
                'Specify this as space-delimited float values where every three',
                'subsequent values represent the x y z coordinates of an atom.'
            ]),
            'neb_scale': ' '.join([
                'Boolean indicating if the neb_pos values are to be taken',
                'as relative to the loaded unit cell and therefore should be',
                'scaled to absolute Cartesian values.'
            ]),
            'neb_symbol': ' '.join([
                'The potential symbol model(s) to assign to the NEB atoms.  Should',
                'be a space-delimited list giving a value for each NEB atom.',
                'Optional if all atoms are of the same type.'
            ]),
        })
        return d

    @property
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  list(self.templatekeys.keys()) + [
                    'pointdefectneb_family',
                    'pointdefectneb_content',
                ]

    @property
    def interpretkeys(self) -> list:
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'pointdefectneb_model',
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
        self.param_file = input_dict.get(keymap['pointdefectneb_file'], None)
        self.__content = input_dict.get(keymap['pointdefectneb_content'], None)
        self.neb_symbol = input_dict.get(keymap['neb_symbol'], None)

        # Replace defect model with defect content if given
        param_file = self.param_file
        if self.__content is not None:
            param_file = self.__content

        # Extract parameters from a file
        if param_file is not None:

            # Verify competing parameters are not defined
            for key in ('pointdefect_type', 'pointdefect_atype', 'pointdefect_pos',
                        'pointdefect_dumbbell_vect', 'pointdefect_scale', 
                        'neb_pos1', 'neb_pos2', 'neb_scale'):
                if keymap[key] in input_dict:
                    raise ValueError(f"{keymap[key]} and {keymap['pointdefectneb_file']} cannot both be supplied")

            # Load defect model
            self.__model = model = DM(param_file).find('point-defect-neb')

            # Extract parameter values from defect model
            self.key = model['key']
            self.id = model['id']
            self.family = model['system-family']
            self.__params = []
            self.neb_pos1 = model['calculation-parameter']['neb_pos1']
            self.neb_pos2 = model['calculation-parameter']['neb_pos2']
            self.neb_scale = model['calculation-parameter'].get('neb_scale', False)

            for ptd in model['calculation-parameter'].aslist('point-defect'):
                self.add_params(**ptd)

        # Set parameter values directly
        else:
            self.__model = None
            self.key = None
            self.id = None
            self.family = self.parent.system.family
            self.neb_pos1 = input_dict[keymap['neb_pos1']]
            self.neb_pos2 = input_dict[keymap['neb_pos2']]
            self.neb_scale = input_dict.get(keymap['neb_scale'], False)

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
        baseroot = 'point-defect-neb'
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
        self.neb_pos1 = uc.value_unit(ptd['calculation-parameter']['neb_pos1'])
        self.neb_pos2 = uc.value_unit(ptd['calculation-parameter']['neb_pos2'])
        self.neb_scale = ptd['calculation-parameter']['neb_scale']
        self.neb_symbol = ptd['calculation-parameter']['neb_symbol']
        for cp in ptd['calculation-parameter'].aslist('point-defect'):
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
        ptd['calculation-parameter'] = DM()
        ptd['calculation-parameter']['neb_pos1'] = uc.model(self.neb_pos1, 'angstrom')
        ptd['calculation-parameter']['neb_pos2'] = uc.model(self.neb_pos2, 'angstrom')
        ptd['calculation-parameter']['neb_scale'] = self.neb_scale
        ptd['calculation-parameter']['neb_symbol'] = self.neb_symbol

        for params in self.params:
            ptd['calculation-parameter'].append('point-defect', params.build_model())

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""

        root = f'{self.parent.modelroot}.{self.modelroot}'

        return {
            'pointdefectneb_id': load_query(
                style='str_match',
                name=f'{self.prefix}pointdefectneb_id',
                path=f'{root}.id',
                description='search by point defect neb parameter set id'),
            'pointdefectneb_key': load_query(
                style='str_match',
                name=f'{self.prefix}pointdefectneb_key',
                path=f'{root}.key',
                description='search by point defect neb parameter set UUID key'),
            'pointdefectneb_family': load_query(
                style='str_match',
                name=f'{self.prefix}pointdefectneb_family',
                path=f'{root}.system-family',
                description='search by crystal prototype that the point defect neb parameter set is for'),
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

        meta[f'{prefix}pointdefectneb_key'] = self.key
        meta[f'{prefix}pointdefectneb_id'] = self.id
        meta[f'{prefix}pointdefectneb_family'] = self.family

        meta[f'{prefix}neb_pos1'] = self.neb_pos1
        meta[f'{prefix}neb_pos2'] = self.neb_pos2
        meta[f'{prefix}neb_scale'] = self.neb_scale
        meta[f'{prefix}neb_symbol'] = self.neb_symbol

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
        if self.neb_pos1 is None:
            raise ValueError('neb_atom_pos1 not set!')
        if self.neb_pos2 is None:
            raise ValueError('neb_atom_pos2 not set!')
        
        if self.neb_scale:
            box = self.parent.system.ucell.box
            input_dict['neb_pos1'] = box.position_relative_to_cartesian(self.neb_pos1)
            input_dict['neb_pos2'] = box.position_relative_to_cartesian(self.neb_pos2)
        else:
            input_dict['neb_pos1'] = self.neb_pos1
            input_dict['neb_pos2'] = self.neb_pos2
        
        if self.neb_symbol is not None:
            input_dict['neb_symbol'] = self.neb_symbol

        if len(self.params) == 1:
            input_dict['point_kwargs'] = self.params[0].calc_inputs(self.parent.system.ucell)
        elif len(self.params) > 1:
            input_dict['point_kwargs'] = []
            for params in self.params:
                input_dict['point_kwargs'].append(params.calc_inputs(self.parent.system.ucell))
        #else:
        #    raise ValueError('No point defect parameters set')
