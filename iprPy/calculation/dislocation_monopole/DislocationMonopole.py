# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

from .calc_dislocation_monopole import dislocationmonopole
from .. import Calculation

class DislocationMonopole(Calculation):
    """
    Class for handling different calculation styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.calculations submodule.
    """

    def __init__(self):
        self.calc = dislocationmonopole

        Calculation.__init__(self)

    @property
    def files(self):
        """
        iter of str: Path to each file required by the calculation.
        """
        files = [
                 'calc_' + self.style + '.py',
                 'disl_relax.template',
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
                    'load_file',
                    'load_content',
                    'load_style',
                    'family',
                    'load_options',
                    'symbols',
                    'box_parameters',
                    'elasticconstants_file',
                    'elasticconstants_content',
                    'C11',
                    'C12',
                    'C13',
                    'C14',
                    'C15',
                    'C16',
                    'C22',
                    'C23',
                    'C24',
                    'C25',
                    'C26',
                    'C33',
                    'C34',
                    'C35',
                    'C36',
                    'C44',
                    'C45',
                    'C46',
                    'C55',
                    'C56',
                    'C66',
                   ],
                   [
                    'sizemults',
                   ],
                   [
                    'dislocation_file',
                    'dislocation_content',
                    'dislocation_family',
                    'dislocation_burgersvector',
                    'dislocation_boundarywidth',
                    'dislocation_boundaryshape',
                    'dislocation_stroh_m',
                    'dislocation_stroh_n',
                    'dislocation_lineboxvector',
                    'a_uvw',
                    'b_uvw',
                    'c_uvw',
                    'atomshift',
                    ],
                    [
                    'randomseed',
                    'annealtemperature',
                    'energytolerance',
                    'forcetolerance',
                    'maxiterations',
                    'maxevaluations',
                    'maxatommotion',
                    ],
               ]