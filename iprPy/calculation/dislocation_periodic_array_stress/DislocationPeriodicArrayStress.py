# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

from .calc_dislocation_periodic_array_stress import dislocationarraystress
from .. import Calculation

class DislocationPeriodicArrayStress(Calculation):
    """
    Class for handling different calculation styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.calculations submodule.
    """

    def __init__(self):
        self.calc = dislocationarraystress

        Calculation.__init__(self)

    @property
    def files(self):
        """
        iter of str: Path to each file required by the calculation.
        """
        files = [
                 'calc_' + self.style + '.py',
                 'dislarray_rigid_stress.template',
                 'dislarray_free_stress.template',
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
                'boundarywidth',
                'rigidboundaries',
               ]
    
    @property
    def multikeys(self):
        """list: Calculation keys that can have multiple values during prepare."""
        return [
                   [
                    'potential_file',
                    'potential_content',
                    'potential_dir',
                    'load_file',
                    'load_content',
                    'load_style',
                    'family',
                    'load_options',
                    'symbols',
                    'box_parameters',
                   ],
                   [
                    'temperature',
                   ],
                   [
                    'runsteps',
                    'thermosteps',
                    'dumpsteps',
                    'randomseed',
                    ],
                    [
                    'sigma_xz',
                    'sigma_yz',
                    ],
               ]