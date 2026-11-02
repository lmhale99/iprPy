from atomman.lammps import LAMMPS, LAMMPSobj

from yabadabado.value import InputValue
from .. import load_query

# PLACEHOLDER for mpi4py code
comm = None

__all__ = ['LammpsValue']

class LammpsValue(InputValue):

    """
    Value for a LAMMPS interactive object.  Passes in the object for running calculations. Manages metadata between transformations.
    """

    @property
    def version(self) -> str | None:
        """str or None: The lammps version associated with the value"""
        try:
            self.__version
        except:
            self.__version = None
        return self.__version

    def set_value_mod(self, val):
        
        # Default None value
        if val is None:
            return None
        
        # Pass LAMMPS objects through
        elif isinstance(val, LAMMPSobj):
            self.__version = val.versionstr
            return val

        # Build LAMMPS objects based on str lammps_command values
        elif isinstance(val, str):

            if val == 'LAMMPSLIB':
                lmp = LAMMPS(cmdargs=['-l', 'none', '-screen', 'none'], comm=comm)
            else:
                lmp = LAMMPS(lammps_command=val)
            self.__version = lmp.versionstr
            return lmp

        else:
            raise TypeError('Must be None, a LAMMPS object or an exe path')
        
    @property
    def _default_queries(self) -> dict:
        """dict: Default query operations to associate with the Parameter style"""
        return {
            'lammps_version': load_query(
                style='str_match',
                name=f'lammps_version', 
                path=f'{self.record.modelroot}.{self.modelpath}.lammps_version',
                description='search by LAMMPS version')
        }
    
    def build_model_value(self):
        """Function to modify how values are represented in the model"""
        return self.version
        
    def load_model_value(self, val):
        """Function to modify how values are interpreted from the model"""
        self.__version = str(val)
        return None
        
    def metadata_value(self):
        """Function to modify how values are represented in the metadata"""
        return self.version

    def load_parameters_value(self, val):
        return val

    def calc_inputs_value(self):
        return super().calc_inputs_value()