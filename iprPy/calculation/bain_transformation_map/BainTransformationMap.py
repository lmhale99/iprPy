# coding: utf-8

# iprPy imports
from .. import Calculation
from ...input import subset

class BainTransformationMap(Calculation):
    """
    Class for handling different calculation styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.calculations submodule.
    """

    def __init__(self):
        """
        Initializes a Calculation object for a given style.
        """
        # Call parent constructor
        super().__init__()

        # Define calc shortcut
        self.calc = self.script.crystal_space_group
    
    @property
    def files(self):
        """
        list: the names of each file required by the calculation.
        """
        # Fetch universal files from parent
        universalfiles = super().files

        # Specify calculation-specific keys 
        files = [
            'Bain.py',
            'min.template']
        
        # Join and return
        return universalfiles + files

    @property
    def template(self):
        """
        str: The template to use for generating calc.in files.
        """
        # Specify the subsets to include in the template
        subsets = [
            'lammps_commands', 
            'lammps_potential',
            'units',
            'lammps_minimize',
        ]
        
        # Specify the calculation-specific run parameters
        runkeys = [
            'a_bcc',
            'a_fcc',
            'sizemults',
            'number_a_scale',
            'minimum_a_scale', 
            'maximum_a_scale', 
            'number_c_scale', 
            'minimum_c_scale', 
            'maximum_c_scale', 
        ]
        
        return self._buildtemplate(subsets, runkeys)

    @property
    def singularkeys(self):
        """
        list: Calculation keys that can have single values during prepare.
        """        
        # Fetch universal keys from parent
        universalkeys = super().singularkeys
        
        # Specify calculation-specific keys 
        keys = (subset('lammps_commands').keyset
               +subset('units').keyset 
               +[

               ])

        # Join and return
        return universalkeys + keys
    
    @property
    def multikeys(self):
        """
        list: Calculation key sets that can have multiple values during prepare.
        """        
        # Fetch universal key sets from parent
        universalkeys = super().multikeys
        
        # Specify calculation-specific key sets 
        keys = [
            subset('lammps_potential').keyset + [
                'a_bcc',
                'a_fcc'
            ],
            subset('lammps_minimize').keyset,
            [
                'sizemults'
            ],
            [
                'number_a_scale',
                'minimum_a_scale', 
                'maximum_a_scale', 
                'number_c_scale', 
                'minimum_c_scale', 
                'maximum_c_scale'
            ]
        ]
        
        # Join and return
        return universalkeys + keys
