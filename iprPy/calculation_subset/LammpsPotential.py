import atomman as am
import atomman.lammps as lmp

from datamodelbase import query


from DataModelDict import DataModelDict as DM

from . import CalculationSubset

from ..tools import dict_insert

class LammpsPotential(CalculationSubset):
    """Handles calculation terms for loading a LAMMPS-compatible potential"""

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
                self.__potential_LAMMPS_id is not None
                or self.__potential_LAMMPS_key is not None)):
            
            self.potential = am.load_lammps_potential(
                id=self.__potential_LAMMPS_id,
                key=self.__potential_LAMMPS_key,
                pot_dir_style = 'local'
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

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return '# Potential definition and directory containing associated files'

    @property
    def templatekeys(self):
        """
        list : The default input keys used by the calculation.
        """
        return  [
                    'potential_file',
                    'potential_dir',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The default input keys used by prepare.
        """
        return  self.templatekeys + [
                    'potential_content',
                    'potential_dir_content',
                ]

    @property
    def interpretkeys(self):
        """
        list : The default input keys accessed when interpreting input files.
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
        potential_dir = input_dict.get(keymap['potential_dir'], '')
        potential_content = input_dict.get(keymap['potential_content'], None)

        # Use potential_content instead of potential_file if given
        if potential_content is not None:
            potential_file = potential_content
        
        # Read potential
        self.potential = lmp.Potential(potential_file, pot_dir=potential_dir)

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
        if self.potential is None:
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
        if self.potential is None:
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