from ..Subset import Subset

class Units(Subset):
    """
    Defines interactions for input keys associated with specifying input/output
    units.
    """
    
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
    
    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Units for input/output values'
        
        return super().template(header=header)

    def interpret(self, input_dict):
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
        input_dict[keymap['length_unit']] = input_dict.get(keymap['length_unit'], 'angstrom')
        input_dict[keymap['energy_unit']] = input_dict.get(keymap['energy_unit'], 'eV')
        input_dict[keymap['pressure_unit']] = input_dict.get(keymap['pressure_unit'], 'GPa')
        input_dict[keymap['force_unit']] = input_dict.get(keymap['force_unit'], 'eV/angstrom')