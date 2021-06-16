# coding: utf-8

# iprPy imports
from .. import Calculation
from ...input import subset

class ElasticConstantsStatic(Calculation):
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
        self.calc = self.script.elastic_constants_static

    @property
    def files(self):
        """
        list: the names of each file required by the calculation.
        """
        # Fetch universal files from parent
        universalfiles = super().files

        # Specify calculation-specific keys 
        files = [
            'cij.template',
        ]
                
        # Join and return
        return universalfiles + files
    
    @property
    def inputsubsets(self):
        """list: The subsets whose input key sets are used for the calculation"""
        return  [
            'lammps_commands', 
            'lammps_potential',
            'atomman_systemload',
            'atomman_systemmanipulate',
            'units',
            'lammps_minimize',
        ]
    
    @property
    def inputkeys(self):
        """list: the calculation-specific input keys"""
        return  [
            'strainrange',
        ]
        
    @property
    def singularkeys(self):
        """
        list: Calculation keys that can have single values during prepare.
        """
        # Fetch universal key sets from parent
        universalkeys = super().singularkeys
        
        # Specify calculation-specific key sets 
        keys = (subset('lammps_commands').keyset 
               +subset('units').keyset + [])
               
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
        keys =  [
            (subset('lammps_potential').keyset 
            +subset('atomman_systemload').keyset),
            subset('atomman_systemmanipulate').keyset,
            [
                'strainrange',
            ],
            subset('lammps_minimize').keyset,
        ]
               
        # Join and return
        return universalkeys + keys

# Test module
ElasticConstantsStatic()