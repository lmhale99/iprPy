# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

from .. import Calculation
from ...input import subset

class PointDefectMobility(Calculation):
    """
    Class for handling different calculation styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.calculations submodule.
    """
    @property
    def files(self):
        """
        iter of str: Path to each file required by the calculation.
        """
        files = [
                 'calc_' + self.style + '.py',
                 'neb_lammps.template',
                ]
        for i in range(len(files)):
            files[i] = os.path.join(self.directory, files[i])
        
        return files
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
            'atomman_systemmanipulate',
            'pointdefectmobility',
            'units',
            'lammps_minimize',
        ]
        
        # Specify the calculation-specific run parameters
        runkeys = [
            'numberreplicas',
            'springconst',
            'thermosteps',
            'timestep',
            'dumpsteps',
            'minsteps',
            'climbsteps'
        ]
        
        return self._buildtemplate(subsets, runkeys)   
    @property
    def singularkeys(self):
        """list: Calculation keys that can have single values during prepare."""
        #Fetch universal key sets from parents
        universalkeys = super().singularkeys
        
        # Specify calculation-specific key sets 
        keys = (
             subset('units').keyset 
            +   [
                'branch',
                'maxiterations',
                'maxevaluations',
                'defectmobility_allowable_impurity_numbers',
                'defectmobility_impurity_list',
                'defectmobility_impurity_blacklist'
                ]
        )
        # Join and return
        
        return universalkeys + keys
        
        

    
    @property
    def multikeys(self):
        """list: Calculation keys that can have multiple values during prepare."""
        # Fetch universal key sets from parent
        universalkeys = super().multikeys
        
        # Because of the way that the system is currently defined, alot of the multikey combinations are
        # actually generated in the input\buildcombos_function\defectmobility.py script, not in the prepare
        # script like normal.  This is because of the requirement of defining different types of impurity elements
        # for allSymbols, which is in pointdefectmobility, is reliant on specific information from lammps_potential
        
        # Specify calculation-specific key sets 
        keys =  [
            (
                subset('lammps_commands').keyset + ['numberreplicas']
            ),
            (
                subset('pointdefectmobility').keyset
                + subset('lammps_potential').keyset 
                + subset('atomman_systemload').keyset
            ),
            (
                subset('atomman_systemmanipulate').keyset
            ),
            (
                subset('lammps_minimize').keyset + 
                [
                    'springconst',
                    'thermosteps',
                    'dumpsteps',
                    'timestep',
                    'minsteps',
                    'climbsteps',
                ]
            ),
        ]
              
        # Join and return
        return universalkeys + keys