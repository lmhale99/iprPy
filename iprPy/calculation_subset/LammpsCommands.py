
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
     
    def __init__(self, parent, prefix='', templateheader=None,
                 templatedescription=None):
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
        templateheader : str, optional
            An alternate header to use in the template file for the subset.
        templatedescription : str, optional
            An alternate description of the subset for the templatedoc.
        """
        super().__init__(parent, prefix=prefix, templateheader=templateheader,
                         templatedescription=templatedescription)

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

    def _template_init(self, templateheader=None, templatedescription=None):
        """
        Sets the template header and description values.

        Parameters
        ----------
        templateheader : str, optional
            An alternate header to use in the template file for the subset.
        templatedescription : str, optional
            An alternate description of the subset for the templatedoc.
        """
        # Set default template header
        if templateheader is None:
            templateheader = 'LAMMPS and MPI Commands'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the external commands for running LAMMPS and MPI."])
        
        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self):
        """dict : The subset-specific input keys and their descriptions."""
        
        return  {
            'lammps_command': ' '.join([
                "The path to the executable for running LAMMPS on your system.",
                "Don't include command line options."]),
            'mpi_command': ' '.join([
                "The path to the MPI executable and any command line options to",
                "use for calling LAMMPS to run in parallel on your system. LAMMPS",
                "will run as a serial process if not given."]),
        }
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return list(self.templatekeys.keys()) + []
        
    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
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
        """str : The root element name for the subset terms."""
        baseroot = 'LAMMPS-version'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        self.__lammps_version = model['calculation'][self.modelroot]
    
    def build_model(self, model, **kwargs):
        """
        Adds the subset model to the parent model.
        
        Parameters
        ----------
        model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        kwargs : any
            Any options to pass on to dict_insert that specify where the subset
            content gets added to in the parent model.
        """
        dict_insert(model['calculation'], self.modelroot, self.lammps_version,
                    **kwargs)

    def mongoquery(self, lammps_version=None, **kwargs):
        """
        Generate a query to parse records with the subset from a Mongo-style
        database.
        
        Parameters
        ----------
        lammps_version : str
            The version of LAMMPS used.
        kwargs : any
            The parent query terms and values ignored by the subset.

        Returns
        -------
        dict
            The Mongo-style find query terms.
        """
        # Init query and set root paths
        mquery = {}
        parentroot = f'content.{self.parent.modelroot}'
        root = f'{parentroot}.calculation.{self.modelroot}'
        
        # Build query terms
        query.str_match.mongo(mquery, root, lammps_version)
        
        # Return query dict
        return mquery

    def cdcsquery(self, lammps_version=None, **kwargs):
        """
        Generate a query to parse records with the subset from a CDCS-style
        database.
        
        Parameters
        ----------
        lammps_version : str
            The version of LAMMPS used.
        kwargs : any
            The parent query terms and values ignored by the subset.
        
        Returns
        -------
        dict
            The CDCS-style find query terms.
        """
        # Init query and set root paths
        mquery = {}
        parentroot = self.parent.modelroot
        root = f'{parentroot}.calculation.{self.modelroot}'
        
        # Build query terms
        query.str_match.mongo(mquery, root, lammps_version)
        
        # Return query dict
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
        meta[f'{self.prefix}lammps_version'] = self.lammps_version
        
    def pandasfilter(self, dataframe, lammps_version=None, **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
        lammps_version : str
            The version of LAMMPS used.
        kwargs : any
            The parent query terms and values ignored by the subset.

        Returns
        -------
        pandas.Series of bool
            True for each entry where all filter terms+values match, False for
            all other entries.
        """
        prefix = self.prefix
        matches = (
            query.str_match.pandas(dataframe, f'{prefix}lammps_version',
                                   lammps_version)
        )
        return matches

########################### Calculation interactions ##########################
    
    def calc_inputs(self, input_dict):
        """
        Generates calculation function input parameters based on the values
        assigned to attributes of the subset.

        Parameters
        ----------
        input_dict : dict
            The dictionary of input parameters to add subset terms to.
        """
        if self.lammps_command is None:
            raise ValueError('lammps_command not set!')
            
        input_dict['lammps_command'] = self.lammps_command
        input_dict['mpi_command'] = self.mpi_command
        