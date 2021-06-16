# coding: utf-8

from .. import Calculation
from ...input import subset

class DislocationSDVPN(Calculation):
    """
    Class for handling different calculation styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.calculations submodule.
    """

    def __init__(self):

        # Call parent constructor
        super().__init__()

        # Define calc shortcut
        self.calc = self.script.peierlsnabarro

    @property
    def files(self):
        """
        iter of str: Path to each file required by the calculation.
        """
        # Fetch universal files from parent
        universalfiles = super().files

        # Specify calculation-specific keys 
        files = []
        
        # Join and return
        return universalfiles + files
    
    @property
    def inputsubsets(self):
        """list: The subsets whose input key sets are used for the calculation"""
        return  [
            'atomman_systemload',
            'atomman_gammasurface',
            'atomman_elasticconstants',
            'dislocation',
            'units',
        ]
    
    @property
    def inputkeys(self):
        """list: the calculation-specific input keys"""
        return  [
            'xmax',
            'xstep',
            'xnum',
            'minimize_style',
            'minimize_options',
            'minimize_cycles',
            'cutofflongrange',
            'tau_xy',
            'tau_yy',
            'tau_yz',
            'alpha',
            'beta_xx',
            'beta_yy',
            'beta_zz',
            'beta_xy',
            'beta_xz',
            'beta_yz',
            'cdiffelastic',
            'cdiffsurface',
            'cdiffstress',
            'halfwidth',
            'normalizedisreg',
            'fullstress',
        ]

    @property
    def singularkeys(self):
        """
        list: Calculation keys that can have single values during prepare.
        """
        # Fetch universal key sets from parent
        universalkeys = super().singularkeys
        
        # Specify calculation-specific key sets 
        keys = (
            subset('lammps_commands').keyset 
            + subset('units').keyset 
            + [
                'sizemults',
                'amin',
                'bmin',
                'cmin',
            ]
        )

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
                   (
                subset('atomman_systemload').keyset
                + subset('atomman_elasticconstants').keyset
                + subset('atomman_gammasurface').keyset
            ),
            (
                subset('dislocation').keyset
            ),
            (
                [
                    'xmax',
                    'xstep',
                    'xnum',
                    'minimize_style',
                    'minimize_options',
                    'minimize_cycles',
                    'cutofflongrange',
                    'tau_xy',
                    'tau_yy',
                    'tau_yz',
                    'alpha',
                    'beta_xx',
                    'beta_yy',
                    'beta_zz',
                    'beta_xy',
                    'beta_xz',
                    'beta_yz',
                    'cdiffelastic',
                    'cdiffsurface',
                    'cdiffstress',
                    'halfwidth',
                    'normalizedisreg',
                    'fullstress',
                ]
            )
        ]
                   
        # Join and return
        return universalkeys + keys

# Test module
DislocationSDVPN()