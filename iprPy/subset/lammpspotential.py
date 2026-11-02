# Standard Python libraries
from typing import Optional, Union
from io import IOBase

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
from atomman.typing import lammpspotential


# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# Local imports
from yabadabado.calculation import CalculationSubset

__all__ = ['LammpsPotential']

class LammpsPotential(CalculationSubset):
    """Handles calculation terms for loading a LAMMPS-compatible potential"""

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 noname: bool = True,
                 extensible: Optional[bool] = None,
                 **kwargs):
        """
        Initializes a CalculationSubset object for a given style.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Record content in data model format to read in.  Cannot be given
            with params.
        name : str, optional
            The name to use for saving the record.  By default, this should be
            the calculation's key.
        database : yabadaba.Database, optional
            A default Database to associate with the Record, typically the
            Database that the Record was obtained from.  Can allow for Record
            methods to perform Database operations without needing to specify
            which Database to use.
        params : str, file-like object or dict, optional
            Calculation input parameters or input parameter file.  Cannot be
            given with model.
        **kwargs : any
            Any other core Calculation record attributes to set according to 
            :class:`atomman.library.record.Record`.  Cannot be
            given with model.
        """
        # Initialize style-specific non-value terms
        self.__potential = None

        # Call CalculationSubset's init
        super().__init__(model=model, name=name, database=database,
                         noname=noname, extensible=extensible, **kwargs)
            

    def _init_values(self):

        self._add_value('str', 'potential_LAMMPS_key',
                        modelpath = 'key',
                        description = 'The UUID4 key for the potential implementation')

        self._add_value('str', 'potential_LAMMPS_id',
                        modelpath = 'id',
                        description = 'The unique ID for the potential implementation')

        self._add_value('str', 'potential_LAMMPS_url',
                        modelpath = 'URL',
                        description = 'A URL where the potential implementation can be found')   
         
        self._add_value('str', 'potential_key',
                        modelpath = 'potential.key',
                        description = 'The UUID4 key for the potential model')

        self._add_value('str', 'potential_id',
                        modelpath = 'potential.id',
                        description = 'The unique ID for the potential model')

        self._add_value('str', 'potential_url',
                        modelpath = 'potential.URL',
                        description = 'A URL where the potential model can be found')


############################## Class attributes ################################

    @property
    def potential(self) -> lammpspotential:
        """BasePotentialLAMMPS: The record object for the LAMMPS implementation"""
        if (self.__potential is None and (
                self.potential_LAMMPS_id is not None
                or self.potential_LAMMPS_key is not None)):

            self.potential = am.load_lammps_potential(
                id = self.potential_LAMMPS_id,
                key = self.potential_LAMMPS_key,
                pot_dir_style = 'local',
                database = self.parent.database
            )
        return self.__potential

    @potential.setter
    def potential(self, val: lammpspotential):
        # Set metadata values
        self.potential_key = val.potkey
        self.potential_id = val.potid
        self.potential_url = val.poturl
        self.potential_LAMMPS_key = val.key
        self.potential_LAMMPS_id = val.id
        self.potential_LAMMPS_url = val.url
        self.__potential = val

####################### Parameter file interactions ###########################

    @property
    def template_header(self) -> str:
        return '# Interatomic Potential'

    @property
    def templatekeys(self) -> list:
        """list : The calculation-specific input keys."""
        return [
            'potential_file',
            'potential_kim_id',
            'potential_kim_potid',
            'potential_dir'
        ]

    @property
    def templatedoc(self) -> str:
        """str : The subset-specific input keys and their descriptions."""

        return '\n'.join([
            '#' + self.template_header,
            f'- __potential_file__: The path to the potential_LAMMPS or potential_LAMMPS_KIM record that defines the interatomic potential to use for LAMMPS calculations.',
            f'- __potential_kim_id__: If potential_file is a potential_LAMMPS_KIM record, this allows for the specification of which version of the KIM model to use by specifying a full kim model id.  If not given, the newest known version of the kim model will be assumed.',
            f'- __potential_kim_potid__: Some potential_LAMMPS_KIM records are associated with multiple potential entries.  This allows for the clear specification of which potential (by potid) to associate with those kim models. This will affect the list of available symbols for the calculation.',
            f'- __potential_dir__: The path to the directory containing any potential parameter files (eg. eam.alloy setfl files) that are needed for the potential. If not given, then any required files are expected to be in the working directory where the calculation is executed.',
            '',
        ])


    @property
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return self.templatekeys + [
                    'potential_content',
                    'potential_dir_content',
                ]

    @property
    def interpretkeys(self) -> list:
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'potential',
                ]

    def load_parameters(self, input_dict: dict):
        """
        Interprets calculation parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary containing input parameter key-value pairs.
        """

        # Extract input values and assign default values
        potential_file = input_dict['potential_file']
        potential_kim_id = input_dict.get('potential_kim_id', None)
        potential_kim_potid = input_dict.get('potential_kim_potid', None)
        potential_dir = input_dict.get('potential_dir', None)
        potential_content = input_dict.get('potential_content', None)

        # Use potential_content instead of potential_file if given
        if potential_content is not None:
            potential_file = potential_content

        # Load potential and add it to input_dict
        self.potential = lmp.Potential(potential_file, pot_dir=potential_dir, 
                                       kim_id=potential_kim_id, potid=potential_kim_potid)
        input_dict['potential'] = self.potential

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str : The root element name for the subset terms."""
        return 'potential-LAMMPS'

    def load_model(self, model: DM):
        """Loads subset attributes from an existing model."""
        sub = model[self.modelroot]

        self.potential_LAMMPS_key = sub['key']
        self.potential_LAMMPS_id = sub['id']
        self.potential_LAMMPS_url = sub.get('URL', None)
        self.potential_key = sub['potential']['key']
        self.potential_id = sub['potential']['id']
        self.potential_url = sub['potential'].get('URL', None)

########################### Calculation interactions ##########################

    def calc_inputs(self):
        """
        Generates calculation function input parameters based on the values
        assigned to attributes of the subset.

        Parameters
        ----------
        input_dict : dict
            The dictionary of input parameters to add subset terms to.
        """
        if self.potential is None:
            raise ValueError('potential not set')
        input_dict = {}
        input_dict['potential'] = self.potential
        return input_dict
