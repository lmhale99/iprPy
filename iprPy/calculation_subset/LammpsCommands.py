# coding: utf-8
import datetime
from pathlib import Path

# Standard Python libraries
from typing import Optional

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

from yabadaba import load_query

# iprPy imports
from . import CalculationSubset
from ..tools import dict_insert

class LammpsCommands(CalculationSubset):
    """Handles calculation terms for LAMMPS executable commands"""

############################# Core properties #################################

    def __init__(self,
                 parent,
                 prefix: str = '',
                 templateheader: Optional[str] = None,
                 templatedescription: Optional[str] = None):
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
    def lammps_command(self) -> str:
        """str: The LAMMPS executable to use"""
        return self.__lammps_command

    @lammps_command.setter
    def lammps_command(self, val: str):
        self.__lammps_command = Path(val).as_posix()
        if self.__lammps_version is not None:
            self.__lammps_version = None
            self.__lammps_date = None

    @property
    def mpi_command(self) -> Optional[str]:
        """str: The MPI executable and options to use when running LAMMPS"""
        return self.__mpi_command

    @mpi_command.setter
    def mpi_command(self, val: Optional[str]):
        if val is None:
            self.__mpi_command = None
        else:
            self.__mpi_command = str(val)

    @property
    def lammps_version(self) -> str:
        """str: The LAMMPS version str"""
        if self.__lammps_version is None and self.lammps_command is not None:
            lammps_version = lmp.checkversion(self.lammps_command)
            self.__lammps_version = lammps_version['version']
            self.__lammps_date = lammps_version['date']
        return self.__lammps_version

    @property
    def lammps_date(self) -> datetime.date:
        """datetime.date: The LAMMPS version date"""
        if self.__lammps_version is None and self.lammps_command is not None:
            lammps_version = lmp.checkversion(self.lammps_command)
            self.__lammps_version = lammps_version['version']
            self.__lammps_date = lammps_version['date']
        return self.__lammps_date

    def set_values(self, **kwargs: any):
        """
        Allows for multiple class attribute values to be updated at once.

        Parameters
        ----------
        lammps_command: str, optional
            The LAMMPS executable to use
        mpi_command: str or None, optional
            The MPI executable and options to use when running LAMMPS
        """
        if 'lammps_command' in kwargs:
            self.lammps_command = kwargs['lammps_command']
        if 'mpi_command' in kwargs:
            self.mpi_command = kwargs['mpi_command']

####################### Parameter file interactions ###########################

    def _template_init(self,
                       templateheader: Optional[str] = None,
                       templatedescription: Optional[str] = None):
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
    def templatekeys(self) -> dict:
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
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return list(self.templatekeys.keys()) + []

    @property
    def interpretkeys(self) -> list:
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'lammps_version',
                    'lammps_date'
                ]

    def load_parameters(self, input_dict: dict):
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
    def modelroot(self) -> str:
        """str : The root element name for the subset terms."""
        baseroot = 'LAMMPS-version'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model: DM):
        """Loads subset attributes from an existing model."""
        self.__lammps_version = model['calculation'][self.modelroot]

    def build_model(self,
                    model: DM,
                    **kwargs: any):
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

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        return {
            'lammps_version': load_query(
                style='str_match',
                name=f'{self.prefix}lammps_version', 
                path=f'{self.parent.modelroot}.calculation.{self.modelroot}',
                description='search by LAMMPS version'),
        }

########################## Metadata interactions ##############################

    def metadata(self, meta: dict):
        """
        Converts the structured content to a simpler dictionary.

        Parameters
        ----------
        meta : dict
            The dictionary to add the interpreted content to
        """
        meta[f'{self.prefix}lammps_version'] = self.lammps_version

########################### Calculation interactions ##########################

    def calc_inputs(self, input_dict: dict):
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
