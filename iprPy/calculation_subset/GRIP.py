# coding: utf-8

# Standard Python libraries
from pathlib import Path
from typing import Optional, Union
from copy import deepcopy

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc
from atomman.defect import GRIP as GRIPgb

from . import CalculationSubset
from ..input import boolean

class GRIP(CalculationSubset):
    """Handles calculation terms for GRIP algorithm parameters"""

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

        self.grip = GRIPgb()

############################## Class attributes ################################

    @property
    def grip(self) -> GRIPgb:
        """Path or None: The path to the stacking fault parameter file"""
        return self.__grip

    @grip.setter
    def grip(self, val: GRIPgb):
        if isinstance(val, GRIPgb):
            self.__grip = val
        else:
            raise TypeError('grip must be an atomman.defect.GRIP object')


    def set_values(self, **kwargs: any):
        """
        Allows for multiple class attribute values to be updated at once.

        Parameters
        ----------
        **kwargs : any
            Any of the GRIP settings
        """
        self.grip.set_values(**kwargs)

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
            templateheader = 'GRIP settings'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the GRIP grain boundary algorithm settings."])

        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self) -> dict:
        """dict : The subset-specific input keys and their descriptions."""
        # Auto-build from GRIP's value objects
        d = {}
        for value in self.grip.value_objects:
            if value.name == 'randomseed':
                break
            d[value.name] = value.description
        return d

    @property
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return list(self.templatekeys.keys()) + []

    @property
    def interpretkeys(self) -> list:
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return self.preparekeys + []

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

        # Extract GRIP kwargs from input_dict
        kwargs = {}
        for value in self.grip.value_objects:
            grip_key = value.name
            if grip_key == 'randomseed':
                break
            input_key = keymap[grip_key]
            if input_key in input_dict:
                kwargs[grip_key] = input_dict[input_key]

        # Update GRIP object
        if len(kwargs) > 0:
            self.grip.set_values(**kwargs)

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str : The root element name for the subset terms."""
        baseroot = 'grip'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model: DM):
        """Loads subset attributes from an existing model."""
        grip_model = DM([('grip', model[self.modelroot])])

        self.grip.load_model(grip_model)

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
        grip_model = self.grip.build_model()

        # Save defect parameters
        model[self.modelroot] = grip_model['grip']

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""

        root = f'{self.parent.modelroot}.{self.modelroot}'
        
        # Extract GRIP queries and modify paths
        queries = {}
        for key, query in self.grip.queries.items():
            query = deepcopy(query)
            query.path = root + query.path[4:]
            queries[key] = query
            
        return queries

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

        for key, value in self.grip.metadata().items():
            meta[f'{prefix}{key}'] = value

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

        input_dict['grip'] = self.grip