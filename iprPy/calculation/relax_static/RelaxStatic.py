# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

# iprPy imports
from .. import Calculation

class RelaxStatic(Calculation):
    """
    Class for handling different calculation styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.calculations submodule.
    """
    def __init__(self):
        
        # Call parent constructor
        Calculation.__init__(self)

        # Define calc shortcut
        self.calc = self.script.relax_static
    
    @property
    def files(self):
        """
        iter of str: Path to each file required by the calculation.
        """
        files = [
                 'calc_' + self.style + '.py',
                 'minbox.template',
                ]
        for i in range(len(files)):
            files[i] = os.path.join(self.directory, files[i])
        
        return files
    
    @property
    def singularkeys(self):
        """list: Calculation keys that can have single values during prepare."""
        return [
                'lammps_command',
                'mpi_command',
                'length_unit',
                'pressure_unit',
                'energy_unit',
                'force_unit',
               ]
    
    @property
    def multikeys(self):
        """list: Calculation keys that can have multiple values during prepare."""
        return [
                   [
                    'potential_file',
                    'potential_content',
                    'potential_dir',
                    'potential_dir_content',
                    'load_file',
                    'load_content',
                    'load_style',
                    'family',
                    'load_options',
                    'symbols',
                    'box_parameters',
                   ],
                   [
                    'a_uvw',
                    'b_uvw',
                    'c_uvw',
                    'atomshift',
                    'sizemults',
                   ],
                   [
                    'pressure_xx',
                    'pressure_yy',
                    'pressure_zz',
                    'pressure_xy',
                    'pressure_xz',
                    'pressure_yz',
                    ],
                    [
                    'displacementkick',
                    'maxcycles',
                    'cycletolerance',
                    'energytolerance',
                    'forcetolerance',
                    'maxiterations',
                    'maxevaluations',
                    'maxatommotion',
                    ],
               ]