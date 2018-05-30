# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

from .. import Calculation

raise NotImplementedError('Needs updating')
class DislocationSDVPN(Calculation):
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
                    'load_file',
                    'load_content',
                    'load_style',
                    'family',
                    'load_options',
                    'symbols',
                    'box_parameters',
                    'gammasurface_file',
                    'gammasurface_content',
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
                    'a_uvw',
                    'b_uvw',
                    'c_uvw',
                    'atomshift',
                    'sizemults',
                   ],
                   [
                    'dislocation_file',
                    'dislocation_content',
                    'dislocation_family',
                    'dislocation_burgersvector',
                    'dislocation_boundarywidth',
                    'dislocation_boundaryshape',
                    'x_axis',
                    'y_axis',
                    'z_axis',
                    ],
                    [
                    'xmax',
                    'xstep',
                    'xnum',
                    'minimize_style',
                    'minimize_options',
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
                    'cdiffgradient',
                    'cdiffstress',
                    'halfwidth',
                    'normalizedisreg',
                    'fullstress',
                    ],
               ]