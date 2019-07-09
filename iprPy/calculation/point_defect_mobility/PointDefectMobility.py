# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

from .. import Calculation

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
                 'min.template',
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
                    'potential_dir',
                    'load_file',
                    'load_style',
                    'family',
                    'load_options',
                    'symbols',
                    'box_parameters',
                    'allSymbols',
                   ],
                   [
                    'a_uvw',
                    'b_uvw',
                    'c_uvw',
                    'atomshift',
                    'sizemults',
                   ],
                   [
                    'pointdefect_file',
                    'pointdefect_type',
                    'pointdefect_atype',
                    'pointdefect_pos',
                    'pointdefect_dumbbell_vect',
                    'pointdefect_scale',
                    'pointdefect_file_1',
                    'pointdefect_type_1',
                    'pointdefect_atype_1',
                    'pointdefect_pos_1',
                    'pointdefect_dumbbell_vect_1',
                    'pointdefect_scale_1',
                    'pointdefect_file_2',
                    'pointdefect_type_2',
                    'pointdefect_atype_2',
                    'pointdefect_pos_2',
                    'pointdefect_dumbbell_vect_2',
                    'pointdefect_scale_2',
                    'pointdefect_file_3',
                    'pointdefect_type_3',
                    'pointdefect_atype_3',
                    'pointdefect_pos_3',
                    'pointdefect_dumbbell_vect_3',
                    'pointdefect_scale_3',
                    'pointdefect_file_4',
                    'pointdefect_type_4',
                    'pointdefect_atype_4',
                    'pointdefect_pos_4',
                    'pointdefect_dumbbell_vect_4',
                    'pointdefect_scale_4',
                    'pointdefect_file_5',
                    'pointdefect_type_5',
                    'pointdefect_atype_5',
                    'pointdefect_pos_5',
                    'pointdefect_dumbbell_vect_5',
                    'pointdefect_scale_5',
                    'pointdefect_file_6',
                    'pointdefect_type_6',
                    'pointdefect_atype_6',
                    'pointdefect_pos_6',
                    'pointdefect_dumbbell_vect_6',
                    'pointdefect_scale_6',
                    'pointdefect_number',
                    'defectpair_number',
                    'defectpair_1',
                    'defectpair_2',
                    'defectpair_3',
                    ],
                    [
                    'energytolerance',
                    'forcetolerance',
                    'maxatommotion',
                    'numberreplicas',
                    'springconstant',
                    'thermosteps',
                    'dumpsteps',
                    'timestep',
                    'minimumsteps',
                    'climbsteps',
                    ],
               ]