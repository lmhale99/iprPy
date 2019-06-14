# Standard Python libraries
from pathlib import Path

# iprPy imports
from .. import Calculation

class DiatomScan(Calculation):
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
        self.calc = self.script.diatom

    @property
    def files(self):
        """
        iter of str: Path to each file required by the calculation.
        """
        files = [
                 f'calc_{self.style}.py',
                 'run0.template',
                ]
        for i in range(len(files)):
            files[i] = Path(self.directory, files[i])
        
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
                    'symbols',
                   ],
                   [
                    'minimum_r',
                    'maximum_r',
                    'number_of_steps_r',
                   ],
               ]