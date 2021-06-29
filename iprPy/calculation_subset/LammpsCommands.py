
# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

from datamodelbase import query

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from . import CalculationSubset
from ..tools import dict_insert


class LammpsCommands(CalculationSubset):
    """Handles calculation terms for LAMMPS executable commands"""

############################# Core properties #################################
     
    def __init__(self, parent, prefix=''):
        """
        Initializes a calculation record subset object.

        Parameters
        ----------
        parent : iprPy.calculation.Calculation
            The parent calculation object that the subset object is part of.
            This allows for the subset methods to access parameters set to the
            calculation itself or other subsets.
        prefix : str, optional
            An optional prefix to add to metadata field names to allow for
            differentiating between multiple subsets of the same style within
            a single record
        """
        super().__init__(parent, prefix=prefix)

        self.__lammps_command = None
        self.__mpi_command = None
        self.__lammps_version = None
        self.__lammps_date = None

############################## Class attributes ################################
    
    @property
    def lammps_command(self):
        return self.__lammps_command

    @lammps_command.setter
    def lammps_command(self, value):
        self.__lammps_command = str(value)
        if self.__lammps_version is not None:
            self.__lammps_version = None
            self.__lammps_date = None

    @property
    def mpi_command(self):
        return self.__mpi_command

    @mpi_command.setter
    def mpi_command(self, value):
        if value is None:
            self.__mpi_command = None
        else:
            self.__mpi_command = str(value)

    @property
    def lammps_version(self):
        if self.__lammps_version is None and self.lammps_command is not None:
            lammps_version = lmp.checkversion(self.lammps_command)
            self.__lammps_version = lammps_version['version']
            self.__lammps_date = lammps_version['date']
        return self.__lammps_version
    
    @property
    def lammps_date(self):
        if self.__lammps_version is None and self.lammps_command is not None:
            lammps_version = lmp.checkversion(self.lammps_command)
            self.__lammps_version = lammps_version['version']
            self.__lammps_date = lammps_version['date']
        return self.__lammps_date

    def set_values(self, **kwargs):
        
        if 'lammps_command' in kwargs:
            self.lammps_command = kwargs['lammps_command']
        if 'mpi_command' in kwargs:
            self.mpi_command = kwargs['mpi_command']

####################### Parameter file interactions ###########################

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return '# Command lines for LAMMPS and MPI'

    @property
    def templatekeys(self):
        """
        list : The default input keys used by the calculation.
        """
        return  [
                    'lammps_command',
                    'mpi_command',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The default input keys used by prepare.
        """
        return  self.templatekeys + []
        
    @property
    def interpretkeys(self):
        """
        list : The default input keys accessed when interpreting input files.
        """
        return  self.preparekeys + [
                    'lammps_version',
                    'lammps_date'
                ]
    
    def load_parameters(self, input_dict):
        """
        Interprets calculation parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary containing input parameter key-value pairs.
        """

        # Set default keynames
        keymap = self.keymap
        
        # Extract input values and assign default values
        self.lammps_command = input_dict[keymap['lammps_command']]
        self.mpi_command = input_dict.get(keymap['mpi_command'], None)
    
########################### Data model interactions ###########################

    @property
    def modelroot(self):
        baseroot = 'LAMMPS-version'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        self.__lammps_version = model['calculation'][self.modelroot]
    
    def build_model(self, model, **kwargs):
        # Check required parameters
        #if self.lammps_command is None:
        #    raise ValueError('lammps_command not set')
            
        dict_insert(model['calculation'], self.modelroot, self.lammps_version,
                    **kwargs)

    @staticmethod
    def mongoquery(modelroot, lammps_version=None):
        mquery = {}
        root = f'content.{modelroot}'
        query.str_match.mongo(mquery, f'{root}.calculation.LAMMPS-version', lammps_version)
        return mquery

    @staticmethod
    def cdcsquery(modelroot, lammps_version=None):
        mquery = {}
        root = modelroot
        query.str_match.mongo(mquery, f'{root}.calculation.LAMMPS-version', lammps_version)
        return mquery

########################## Metadata interactions ##############################

    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the interpreted content to
        """
        # Check required parameters
        #if self.lammps_command is None:
        #    raise ValueError('lammps_command not set')

        #meta[f'{self.prefix}lammps_command'] = self.lammps_command
        #meta[f'{self.prefix}mpi_command'] = self.mpi_command
        meta[f'{self.prefix}lammps_version'] = self.lammps_version
        
    @staticmethod
    def pandasfilter(dataframe, lammps_version=None):

        matches = (
            query.str_match.pandas(dataframe, 'lammps_version', lammps_version)
        )
        return matches

########################### Calculation interactions ##########################
    
    def calc_inputs(self, input_dict):
        
        if self.lammps_command is None:
            raise ValueError('lammps_command not set!')
            
        input_dict['lammps_command'] = self.lammps_command
        input_dict['mpi_command'] = self.mpi_command
        