from . import CalculationSubset

class Units(CalculationSubset):
    """Handles calculation terms associated with input/output units settings"""

############################# Core properties ##################################
     
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

        self.__length_unit = 'angstrom'
        self.__pressure_unit = 'GPa'
        self.__energy_unit = 'eV'
        self.__force_unit = 'eV/angstrom'

############################## Class attributes ################################

    @property
    def length_unit(self):
        return self.__length_unit
    
    @length_unit.setter
    def length_unit(self, value):
        self.__length_unit = str(value)

    @property
    def pressure_unit(self):
        return self.__pressure_unit

    @pressure_unit.setter
    def pressure_unit(self, value):
        self.__pressure_unit = str(value)

    @property
    def energy_unit(self):
        return self.__energy_unit

    @energy_unit.setter
    def energy_unit(self, value):
        self.__energy_unit = str(value)

    @property
    def force_unit(self):
        return self.__force_unit

    @force_unit.setter
    def force_unit(self, value):
        self.__force_unit = str(value)

    def set_values(self, **kwargs):
        
        if 'length_unit' in kwargs:
            self.length_unit = kwargs['length_unit']
        if 'pressure_unit' in kwargs:
            self.pressure_unit = kwargs['pressure_unit']
        if 'energy_unit' in kwargs:
            self.energy_unit = kwargs['energy_unit']
        if 'force_unit' in kwargs:
            self.force_unit = kwargs['force_unit']

####################### Parameter file interactions ###########################

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return '# Units for input/output values'

    @property
    def templatekeys(self):
        """
        list : The default input keys used by the calculation.
        """
        return  [
                    'length_unit',
                    'pressure_unit',
                    'energy_unit',
                    'force_unit',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The default input keys used by prepare.
        """
        return  self.templatekeys + []

    @property
    def interpretkeys(self):
        """
        list : The default input keys accessed when interpreting input files.
        """
        return  self.preparekeys + []

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
        
        # Set default unit styles to any terms not given
        self.length_unit = input_dict.get(keymap['length_unit'], 'angstrom')
        self.energy_unit = input_dict.get(keymap['energy_unit'], 'eV')
        self.pressure_unit = input_dict.get(keymap['pressure_unit'], 'GPa')
        self.force_unit = input_dict.get(keymap['force_unit'], 'eV/angstrom')