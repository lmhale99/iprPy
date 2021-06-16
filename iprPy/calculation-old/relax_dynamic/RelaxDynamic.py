# coding: utf-8

# iprPy imports
from .. import Calculation
from ...input import subset

class RelaxDynamic(Calculation):
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
        self.calc = self.script.relax_dynamic
    
    @property
    def files(self):
        """
        list: the names of each file required by the calculation.
        """
        # Fetch universal files from parent
        universalfiles = super().files

        # Specify calculation-specific keys 
        files = [
            'full_relax.template',
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
        ]
    
    @property
    def inputkeys(self):
        """list: the calculation-specific input keys"""
        return  [
            'temperature',
            'pressure_xx',
            'pressure_yy',
            'pressure_zz',
            'pressure_xy',
            'pressure_xz',
            'pressure_yz',
            'integrator',
            'thermosteps',
            'dumpsteps',
            'runsteps',
            'equilsteps',
            'randomseed',
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
                'pressure_xx',
                'pressure_yy',
                'pressure_zz',
                'pressure_xy',
                'pressure_xz',
                'pressure_yz',
            ],
            [
                'temperature',
            ],
            [
                'integrator',
                'thermosteps',
                'dumpsteps',
                'runsteps',
                'equilsteps',
                'randomseed',
            ],
        ]
               
        # Join and return
        return universalkeys + keys

# Test module
RelaxDynamic()