# coding: utf-8

# Standard Python libraries
from typing import Optional

# Local imports
from . import CalculationSubset

class Units(CalculationSubset):
    """Handles calculation terms associated with input/output units settings"""

############################# Core properties ##################################

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

        self.__length_unit = 'angstrom'
        self.__pressure_unit = 'GPa'
        self.__energy_unit = 'eV'
        self.__force_unit = 'eV/angstrom'

############################## Class attributes ################################

    @property
    def length_unit(self) -> str:
        """str: The unit of length to use for input/output values"""
        return self.__length_unit

    @length_unit.setter
    def length_unit(self, val: str):
        self.__length_unit = str(val)

    @property
    def pressure_unit(self) -> str:
        """str: The unit of pressure to use for input/output values"""
        return self.__pressure_unit

    @pressure_unit.setter
    def pressure_unit(self, val: str):
        self.__pressure_unit = str(val)

    @property
    def energy_unit(self) -> str:
        """str: The unit of energy to use for input/output values"""
        return self.__energy_unit

    @energy_unit.setter
    def energy_unit(self, val: str):
        self.__energy_unit = str(val)

    @property
    def force_unit(self) -> str:
        """str: The unit of force to use for input/output values"""
        return self.__force_unit

    @force_unit.setter
    def force_unit(self, val: str):
        self.__force_unit = str(val)

    def set_values(self, **kwargs: any):
        """
        Allows for multiple class attribute values to be updated at once.

        Parameters
        ----------
        length_unit: str, optional
            The unit of length to use for input/output values
        pressure_unit: str, optional
            The unit of pressure to use for input/output values
        energy_unit: str, optional
            The unit of energy to use for input/output values
        force_unit: str, optional
            The unit of force to use for input/output values
        """
        if 'length_unit' in kwargs:
            self.length_unit = kwargs['length_unit']
        if 'pressure_unit' in kwargs:
            self.pressure_unit = kwargs['pressure_unit']
        if 'energy_unit' in kwargs:
            self.energy_unit = kwargs['energy_unit']
        if 'force_unit' in kwargs:
            self.force_unit = kwargs['force_unit']

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
            templateheader = 'Input/Output Units'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the default units to use for the other input keys",
                "and to use for saving to the results file."])

        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self) -> dict:
        """dict : The subset-specific input keys and their descriptions."""
        return  {
            'length_unit': ' '.join([
                "The unit of length to use. Default value is 'angstrom'."]),
            'pressure_unit': ' '.join([
                "The unit of pressure to use.  Default value is 'GPa'."]),
            'energy_unit': ' '.join([
                "The unit of energy to use.  Default value is 'eV'."]),
            'force_unit': ' '.join([
                "The unit of force to use.  Default value is 'eV/angstrom'."]),
        }

    @property
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  list(self.templatekeys.keys()) + []

    @property
    def interpretkeys(self) -> list:
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + []

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

        # Set default unit styles to any terms not given
        self.length_unit = input_dict.get(keymap['length_unit'], 'angstrom')
        self.energy_unit = input_dict.get(keymap['energy_unit'], 'eV')
        self.pressure_unit = input_dict.get(keymap['pressure_unit'], 'GPa')
        self.force_unit = input_dict.get(keymap['force_unit'], 'eV/angstrom')

########################### Data model interactions ###########################

########################## Metadata interactions ##############################

########################### Calculation interactions ##########################
