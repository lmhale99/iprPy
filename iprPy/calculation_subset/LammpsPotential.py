import atomman as am
import atomman.lammps as lmp

from datamodelbase import query


from DataModelDict import DataModelDict as DM

from . import CalculationSubset

from ..tools import dict_insert

class LammpsPotential(CalculationSubset):
    """Handles calculation terms for loading a LAMMPS-compatible potential"""

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

        self.__potential_key = None
        self.__potential_id = None
        self.__potential_LAMMPS_key = None
        self.__potential_LAMMPS_id = None
        self.__potential = None

############################## Class attributes ################################

    @property
    def potential_key(self):
        """str: UUID4 key assigned to the potential model"""
        return self.__potential_key
    
    @potential_key.setter
    def potential_key(self, value):
        self.__potential_key = str(value)

    @property
    def potential_id(self):
        """str: Unique id assigned to the potential model"""
        return self.__potential_id

    @potential_id.setter
    def potential_id(self, value):
        self.__potential_id = str(value)

    @property
    def potential_LAMMPS_key(self):
        """str: UUID4 key assigned to the LAMMPS implementation"""
        return self.__potential_LAMMPS_key

    @potential_LAMMPS_key.setter
    def potential_LAMMPS_key(self, value):
        self.__potential_LAMMPS_key = str(value)

    @property
    def potential_LAMMPS_id(self):
        """str: Unique id assigned to the LAMMPS implementation"""
        return self.__potential_LAMMPS_id

    @potential_LAMMPS_id.setter
    def potential_LAMMPS_id(self, value):
        self.__potential_LAMMPS_id = str(value)

    @property
    def potential(self):
        """potentials.PotentialLAMMPS: The record object for the LAMMPS implementation"""
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
    def potential(self, value):
        # Set metadata values
        self.potential_key = value.potkey
        self.potential_id = value.potid
        self.potential_LAMMPS_key = value.key
        self.potential_LAMMPS_id = value.id
        self.__potential = value
    
    def set_values(self, **kwargs):
        if 'potential' in kwargs:
            try:
                assert 'potential_key' not in kwargs
                assert 'potential_id' not in kwargs
                assert 'potential_LAMMPS_key' not in kwargs
                assert 'potential_LAMMPS_id' not in kwargs
            except:
                raise ValueError('potential cannot be given with other potential kwargs')
            self.potential = kwargs['potential']
        else:
            if 'potential_key' in kwargs:
                self.potential_key = kwargs['potential_key']
            if 'potential_id' in kwargs:
                self.potential_id = kwargs['potential_id']
            if 'potential_LAMMPS_key' in kwargs:
                self.potential_LAMMPS_key = kwargs['potential_LAMMPS_key']
            if 'potential_LAMMPS_id' in kwargs:
                self.potential_LAMMPS_id = kwargs['potential_LAMMPS_id']

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
            templateheader = 'Interatomic Potential'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the interatomic potential to use and the directory",
                "where any associated parameter files are located."])
        
        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self):
        """dict : The subset-specific input keys and their descriptions."""
        
        return  {
            'potential_file': ' '.join([
                "The path to the potential_LAMMPS or potential_LAMMPS_KIM record",
                "that defines the interatomic potential to use for LAMMPS",
                "calculations."]),
            'potential_kim_id': ' '.join([
                "If potential_file is a potential_LAMMPS_KIM record, this allows",
                "for the specification of which version of the KIM model to",
                "use by specifying a full kim model id.  If not given, the newest",
                "known version of the kim model will be assumed."]),
            'potential_dir': ' '.join([
                "The path to the directory containing any potential parameter files",
                "(eg. eam.alloy setfl files) that are needed for the potential. If",
                "not given, then any required files are expected to be in the",
                "working directory where the calculation is executed."]),
        }
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  list(self.templatekeys.keys()) + [
                    'potential_content',
                    'potential_dir_content',
                ]

    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'potential',
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
        potential_file = input_dict[keymap['potential_file']]
        potential_kim_id = input_dict.get(keymap['potential_kim_id'], None)
        potential_dir = input_dict.get(keymap['potential_dir'], None)
        potential_content = input_dict.get(keymap['potential_content'], None)

        # Use potential_content instead of potential_file if given
        if potential_content is not None:
            potential_file = potential_content
        
        # Read potential
        self.potential = lmp.Potential(potential_file, pot_dir=potential_dir,
                                       kim_id=potential_kim_id)

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        baseroot = 'potential-LAMMPS'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        sub = model[self.modelroot]

        self.potential_LAMMPS_key = sub['key']
        self.potential_LAMMPS_id = sub['id']
        self.potential_key = sub['potential']['key']
        self.potential_id = sub['potential']['id']

    def build_model(self, model, **kwargs):
        """
        Adds the subset model to the parent model.
        
        Parameters
        ----------
        model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        input_dict : dict
            Dictionary of all input parameter terms.
        results_dict : dict, optional
            Dictionary containing any results produced by the calculation.
        """

        # Check required parameters
        if (self.potential_key is None or self.potential_id is None
            or self.potential_LAMMPS_key is None
            or self.potential_LAMMPS_id is None):
            try:
                potential = self.potential
                assert potential is not None
            except:
                raise ValueError('potential information not set')

        pot = DM()

        pot['key'] = self.potential_LAMMPS_key
        pot['id'] = self.potential_LAMMPS_id
        pot['potential'] = DM()
        pot['potential']['key'] = self.potential_key
        pot['potential']['id'] = self.potential_id
        
        dict_insert(model, self.modelroot, pot, **kwargs)

########################## Metadata interactions ##############################

    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        # Check required parameters
        if (self.potential_key is None or self.potential_id is None
            or self.potential_LAMMPS_key is None
            or self.potential_LAMMPS_id is None):
            try:
                potential = self.potential
                assert potential is not None
            except:
                raise ValueError('potential information not set')

        meta[f'{self.prefix}potential_LAMMPS_key'] = self.potential_LAMMPS_key
        meta[f'{self.prefix}potential_LAMMPS_id'] = self.potential_LAMMPS_id
        meta[f'{self.prefix}potential_key'] = self.potential_key
        meta[f'{self.prefix}potential_id'] = self.potential_id

    @staticmethod
    def pandasfilter(dataframe, potential_LAMMPS_key=None,
                     potential_LAMMPS_id=None, potential_key=None,
                     potential_id=None):

        matches = (
            query.str_match.pandas(dataframe, 'potential_LAMMPS_key', potential_LAMMPS_key)
            &query.str_match.pandas(dataframe, 'potential_LAMMPS_id', potential_LAMMPS_id)
            &query.str_match.pandas(dataframe, 'potential_key', potential_key)
            &query.str_match.pandas(dataframe, 'potential_id', potential_id)
        )
        return matches

    @staticmethod
    def mongoquery(modelroot, potential_LAMMPS_key=None,
                   potential_LAMMPS_id=None, potential_key=None,
                   potential_id=None):
        mquery = {}
        root = f'content.{modelroot}'
        query.str_match.mongo(mquery, f'{root}.potential-LAMMPS.key', potential_LAMMPS_key)
        query.str_match.mongo(mquery, f'{root}.potential-LAMMPS.id', potential_LAMMPS_id)
        query.str_match.mongo(mquery, f'{root}.potential-LAMMPS.potential.key', potential_key)
        query.str_match.mongo(mquery, f'{root}.potential-LAMMPS.potential.id', potential_id)
        return mquery

    @staticmethod
    def cdcsquery(modelroot, potential_LAMMPS_key=None,
                  potential_LAMMPS_id=None, potential_key=None,
                  potential_id=None):
        mquery = {}
        root = modelroot
        query.str_match.mongo(mquery, f'{root}.potential-LAMMPS.key', potential_LAMMPS_key)
        query.str_match.mongo(mquery, f'{root}.potential-LAMMPS.id', potential_LAMMPS_id)
        query.str_match.mongo(mquery, f'{root}.potential-LAMMPS.potential.key', potential_key)
        query.str_match.mongo(mquery, f'{root}.potential-LAMMPS.potential.id', potential_id)
        return mquery      

########################### Calculation interactions ##########################

    def calc_inputs(self, input_dict):
        
        if self.potential is None:
            raise ValueError('potential not set')
            
        input_dict['potential'] = self.potential