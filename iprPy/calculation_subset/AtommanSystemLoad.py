# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from . import CalculationSubset
from ..tools import dict_insert, aslist
from ..input import termtodict, dicttoterm

class AtommanSystemLoad(CalculationSubset):
    """Handles calculation terms for loading atomic systems using atomman"""

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

        self.load_file = None
        self.load_style = 'system_model'
        self.__load_options = {}
        self.family = None
        self.symbols = []
        self.__ucell = None
        self.box_parameters = None
        

############################## Class attributes ################################
    
    @property
    def load_file(self):
        return self.__load_file

    @load_file.setter
    def load_file(self, value):
        if value is None:
            self.__load_file = None
        else:
            self.__load_file = Path(value)

            # Extract values for family and symbols from system_model
            if self.load_style == 'system_model':
                if self.family is None or len(self.symbols) == 0:
                    family, symbols = self.__extract_model_terms(value)
                    if self.family is None:
                        self.family = family
                    if len(self.symbols) == 0:
                        self.symbols = symbols
            elif self.family is None:
                self.family = Path(value).stem

    @property
    def load_style(self):
        return self.__load_style

    @load_style.setter
    def load_style(self, value):
        if value is None:
            self.__load_style = 'system_model'
        else:
            self.__load_style = str(value)

    @property
    def load_options(self):
        return self.__load_options

    @property
    def family(self):
        return self.__family

    @family.setter
    def family(self, value):
        if value is None:
            self.__family = None
        else:
            self.__family = str(value)

    @property
    def symbols(self):
        """The potential symbols to use"""
        return self.__symbols

    @symbols.setter
    def symbols(self, value):
        if value is None:
            self.__symbols = []
        else:
            value = aslist(value)
            self.__symbols = value

    @property
    def box_parameters(self):
        return self.__box_parameters

    @box_parameters.setter
    def box_parameters(self, value):
        if value is None:
            self.__box_parameters = None
        else:
            value = aslist(value)
            assert len(value) == 3 or len(value) == 6
            self.__box_parameters = value
        if self.__ucell is not None:
            self.scale_ucell()


    @property
    def ucell(self):
        if self.__ucell is None:
            self.load_ucell()
        return self.__ucell
    
    def load_ucell(self, **kwargs):
        """
        Wrapper around atomman.load() for loading files that also saves the
        file loading options as class attributes.  Any parameters not given
        will use the values already set to the object.

        Parameters
        ----------
        load_style : str, optional
            The style for atomman.load() to use.
        load_file : str, optional
            The path to the file to load.
        symbols : list or None, optional
            The list of interaction model symbols to associate with the atom
            types in the load file.  A value of None will default to the
            symbols listed in the load file if the style contains that
            information.
        load_options : dict, optional
            Any other atomman.load() keyword options to use when loading.
        box_parameters : list or None, optional
            A list of 3 orthorhombic box parameters or 6 trigonal box length
            and angle parameters to scale the loaded system by.  Setting a
            value of None will perform no scaling.
        family : str or None, optional
            The system's family identifier.  If None, then the family will be
            set according to the family value in the load file if it has one,
            or as the load file's name otherwise.
        """
        self.set_values(**kwargs)

        # Check for required attributes
        if self.load_file is None:
            raise ValueError('load_file not set')

        # Change load symbols kwarg to None if symbols attribute is empty
        if len(self.symbols) == 0:
            symbols = None
        else:
            symbols = self.symbols

        # Load ucell
        self.__ucell = am.load(self.load_style, self.load_file,
                               symbols=symbols, **self.load_options)
        
        # Check that ucell's symbols are set
        for symbol in self.ucell.symbols:
            if symbol is None:
                raise ValueError('symbols not found/assigned for all atypes')
        self.symbols = self.ucell.symbols

        self.scale_ucell()

        # Add model-specific charges if needed
        try:
            potential = self.parent.potential.potential
            if 'charge' not in self.ucell.atoms_prop():
                self.ucell.atoms.prop_atype('charge', potential.charges(self.ucell.symbols))
        except:
            pass

    def scale_ucell(self):
        """Scale ucell by box_parameters"""
        if self.box_parameters is not None:
                            
            # Three box_parameters means a, b, c
            if len(self.box_parameters) == 3:
                self.ucell.box_set(a=self.box_parameters[0],
                                   b=self.box_parameters[1],
                                   c=self.box_parameters[2], scale=True)
            
            # Six box_parameters means a, b, c, alpha, beta, gamma
            elif len(self.box_parameters) == 6:
                self.ucell.box_set(a=self.box_parameters[0],
                                   b=self.box_parameters[1],
                                   c=self.box_parameters[2],
                                   alpha=self.box_parameters[3],
                                   beta=self.box_parameters[4],
                                   gamma=self.box_parameters[5], scale=True) 


    def set_values(self, **kwargs):
        """
        Allows for multiple class attribute values to be updated at once.

        Parameters
        ----------
        load_style : str, optional
            The style for atomman.load() to use.
        load_file : str, optional
            The path to the file to load.
        symbols : list or None, optional
            The list of interaction model symbols to associate with the atom
            types in the load file.  A value of None will default to the
            symbols listed in the load file if the style contains that
            information.
        load_options : dict, optional
            Any other atomman.load() keyword options to use when loading.
        box_parameters : list or None, optional
            A list of 3 orthorhombic box parameters or 6 trigonal box length
            and angle parameters to scale the loaded system by.  Setting a
            value of None will perform no scaling.
        family : str or None, optional
            The system's family identifier.  If None, then the family will be
            set according to the family value in the load file if it has one,
            or as the load file's name otherwise.
        """
        if 'load_style' in kwargs:
            self.load_style = kwargs['load_style']
        if 'load_file' in kwargs:
            self.load_file = kwargs['load_file']
        if 'load_options' in kwargs:
            assert isinstance(kwargs['load_options'], dict)
            self.__load_options = kwargs['load_options']
        if 'family' in kwargs:
            self.family = kwargs['family']
        if 'symbols' in kwargs:
            self.symbols = kwargs['symbols']
        if 'box_parameters' in kwargs:
            self.box_parameters = kwargs['box_parameters']

    def __extract_model_terms(self, load_file):
        """
        Searches data model files and extracts family and symbols values
        without loading.
        """
        symbols = None
        family = None
        models = DM(load_file).finds(f'{self.modelprefix}system-info')
        
        # Extract values from first instance only (allow index later?)
        for model in models:
            family = model.get('family', Path(load_file).stem)
            symbols = model.get('symbol', None)
            if symbols is not None and len(symbols) == 0:
                symbols = None
            break
        
        return family, symbols

####################### Parameter file interactions ###########################

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return '# Initial system configuration to load'

    @property
    def templatekeys(self):
        """
        list : The input keys (without prefix) that appear in the input file.
        """
        return  [
                    'load_file',
                    'load_style',
                    'load_options',
                    'family',
                    'symbols',
                    'box_parameters',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  self.templatekeys + [
                    'load_content',
                ]
    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'ucell',
                    'potential',
                    'elasticconstants_content',
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
        load_style = input_dict.get(keymap['load_style'], 'system_model')
        load_file = input_dict[keymap['load_file']]
        load_options = input_dict.get(keymap['load_options'], None)
        load_content = input_dict.get(keymap['load_content'], None)
        family = input_dict.get(keymap['family'], None)
        symbols = input_dict.get(keymap['symbols'], None)
        box_parameters = input_dict.get(keymap['box_parameters'], None)
    
        # Build dict for set_values()
        d = {}
        d['load_style'] = load_style

        # Use load_content over load_file
        if load_content is not None:
            d['load_file'] = load_content
        else:
            d['load_file'] = load_file
        
        # Set family
        if family is not None:
            d['family'] = family

        # Process load_options into load_options
        if load_options is not None:
            d['load_options'] = {}
            load_options_keys = ['key', 'index', 'data_set', 'pbc', 'atom_style',
                                'units', 'prop_info']
            d['load_options'] = termtodict(load_options, load_options_keys)
            if 'index' in d['load_options']:
                d['load_options']['index'] = int(d['load_options']['index'])
        
        # Process symbols
        if symbols is not None:
            d['symbols'] = symbols.strip().split()

        # Process box_parameters
        if box_parameters is not None:
            box_params = box_parameters.split()
            
            # Pull out unit value
            if len(box_params) == 4 or len(box_params) == 7:
                unit = box_params[-1]
                box_params = box_params[:-1]
            
            # Use calculation's length_unit if unit not given in box_parameters
            else:
                unit = self.parent.units.length_unit

            # Convert box lengths to the specified units
            box_params = np.array(box_params, dtype=float)
            box_params[:3] = uc.set_in_units(box_params[:3], unit)

            d['box_parameters'] = box_params.tolist()

        # Set values
        self.set_values(**d)

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        baseroot = 'system-info'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        sub = model[self.modelroot]

        d = {}
        d['family'] = sub['family']
        d['load_style'] = sub['artifact']['format']
        d['load_file'] = sub['artifact']['file']
        load_options = sub['load_options']
        d['symbols'] = sub['symbols']

        if load_options is not None:
            d['load_options'] = {}
            load_options_keys = ['key', 'index', 'data_set', 'pbc', 'atom_style',
                                'units', 'prop_info']
            d['load_options'] = termtodict(load_options, load_options_keys)
            if 'index' in d['load_options']:
                d['load_options']['index'] = int(d['load_options']['index'])

        self.set_values(**d)

    def build_model(self, model, **kwargs):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        record_model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        input_dict : dict
            Dictionary of all input parameter terms.
        results_dict : dict, optional
            Dictionary containing any results produced by the calculation.
        """
        # Check required parameters
        if self.load_file is None:
            raise ValueError('load_file not set')
        if len(self.symbols) == 0:
            self.load_ucell()

        system = DM()

        system['family'] = self.family
        system['artifact'] = DM()
        system['artifact']['file'] = self.load_file.as_posix()
        system['artifact']['format'] = self.load_style
        if len(self.load_options) == 0:
            system['artifact']['load_options'] = None
        else:
            system['artifact']['load_options'] = dicttoterm(self.load_options)
        system['symbol'] = self.symbols

        dict_insert(model, self.modelroot, system, **kwargs)

    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        # Check required parameters
        if self.load_file is None:
            raise ValueError('load_file not set')
        if len(self.symbols) == 0:
            self.load_ucell()

        meta[f'{self.prefix}load_file'] = self.load_file.as_posix()
        meta[f'{self.prefix}load_style'] = self.load_style
        meta[f'{self.prefix}load_options'] = dicttoterm(self.load_options)
        meta[f'{self.prefix}family'] = self.family
        meta[f'{self.prefix}symbols'] = ' '.join(self.symbols)
        
        parent_file = Path(self.load_file)
        if parent_file.parent.as_posix() == '.':
            parent = parent_file.stem
        else:
            parent = parent_file.parent.name
        meta[f'{self.prefix}parent_key'] = parent

########################### Calculation interactions ##########################

    def calc_inputs(self, input_dict):
        
        if self.ucell is None:
            raise ValueError('ucell not loaded')

        input_dict['ucell'] = self.ucell