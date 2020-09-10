# coding: utf-8

# iprPy imports
from .. import Calculation
from ...input import subset

class DislocationMonopole(Calculation):
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
        self.calc = self.script.dislocationmonopole

    @property
    def files(self):
        """
        list: the names of each file required by the calculation.
        """
        # Fetch universal files from parent
        universalfiles = super().files

        # Specify calculation-specific keys 
        files = [
            'disl_relax.template',
        ]
        
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
            'atomman_systemload',
            'atomman_elasticconstants',
            'dislocation',
            'units',
            'lammps_minimize',
        ]
        
        # Specify the calculation-specific run parameters
        runkeys = [
            'annealtemperature',
            'annealsteps',
            'randomseed',
            'dislocation_boundaryshape',
            'dislocation_boundarywidth',
            'dislocation_boundaryscale',            
        ]
        
        return self._buildtemplate(subsets, runkeys)

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
                'dislocation_boundaryshape',
                'dislocation_boundarywidth',
                'dislocation_boundaryscale',
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
                subset('lammps_potential').keyset 
                + subset('atomman_systemload').keyset
                + subset('atomman_elasticconstants').keyset
            ),
            (
                [
                    'sizemults',
                    'amin',
                    'bmin',
                    'cmin',
                ]
            ),     
            (
                subset('dislocation').keyset
            ),        
            (   subset('lammps_minimize').keyset 
                + [
                    'randomseed',
                    'annealtemperature',
                    'annealsteps',
                ]
            )
        ]
                    
        # Join and return
        return universalkeys + keys

# Test module
DislocationMonopole()