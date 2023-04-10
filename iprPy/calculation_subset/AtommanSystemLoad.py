# coding: utf-8

# Standard Python libraries
from pathlib import Path
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from yabadaba import load_query

from . import CalculationSubset
from ..tools import dict_insert, aslist
from ..input import termtodict, dicttoterm

class AtommanSystemLoad(CalculationSubset):
    """Handles calculation terms for loading atomic systems using atomman"""

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

        self.load_file = None
        self.load_style = 'system_model'
        self.__load_options = {}
        self.__load_content = None
        self.family = None
        self.symbols = None
        self.__ucell = None
        self.box_parameters = None
        self.composition = None

############################## Class attributes ################################

    @property
    def load_file(self) -> Optional[Path]:
        """Path or None: The path to the system load file"""
        return self.__load_file

    @load_file.setter
    def load_file(self, value: Union[str, Path, None]):
        if value is None:
            self.__load_file = None
        else:
            self.__load_file = Path(value)

    @property
    def load_style(self) -> str:
        """str: The load style, i.e. format, of the load file"""
        return self.__load_style

    @load_style.setter
    def load_style(self, value: Optional[str]):
        if value is None:
            self.__load_style = 'system_model'
        else:
            self.__load_style = str(value)

    @property
    def load_options(self) -> dict:
        """dict: The extra options to use when loading the file"""
        return self.__load_options

    @property
    def load_content(self) -> Optional[str]:
        """str or None: File contents to use instead of reading the file"""
        return self.__load_content

    @property
    def family(self) -> Optional[str]:
        """str or None: The family name for the load file, i.e. the original prototype or reference record"""
        return self.__family

    @family.setter
    def family(self, value: Optional[str]):
        if value is None:
            self.__family = None
        else:
            self.__family = str(value)

    @property
    def symbols(self) -> Optional[list]:
        """list: The potential symbols to use"""
        return self.__symbols

    @symbols.setter
    def symbols(self, value: Union[str, list, None]):
        if value is None:
            self.__symbols = None
        else:
            value = aslist(value)
            self.__symbols = value

    @property
    def box_parameters(self) -> Optional[list]:
        """list or None: The 3 or 6 box lattice parameters"""
        return self.__box_parameters

    @box_parameters.setter
    def box_parameters(self, value: Optional[list]):
        if value is None:
            self.__box_parameters = None
        else:
            value = aslist(value)
            assert len(value) == 3 or len(value) == 6
            self.__box_parameters = value
        if self.__ucell is not None:
            self.scale_ucell()

    @property
    def ucell(self) -> am.System:
        """atomman.System: The system as loaded from the file"""
        if self.__ucell is None:
            self.load_ucell()
        return self.__ucell

    @property
    def composition(self) -> Optional[str]:
        """str or None: The composition of the loaded system"""
        if self.__composition is None:
            try:
                comp = self.ucell.composition
            except:
                pass
            else:
                self.composition = comp
        return self.__composition

    @composition.setter
    def composition(self, value: Optional[str]):
        if value is None or isinstance(value, str):
            self.__composition = value
        else:
            raise TypeError('composition must be str or None')

    def load(self,
             style: str,
             *args: any,
             **kwargs: any):
        """
        Wrapper around atomman.load() for loading files that also saves the
        file loading options as class attributes.  Any parameters not given
        will use the values already set to the object.
        """

        # Load ucell
        self.__ucell = am.load(style, *args, **kwargs)
        self.ucell.wrap()

        # Check if first variable positional argument is a file
        try:
            load_file = Path(args[0])
        except:
            self.load_file = None
        else:
            if load_file.is_file():
                self.load_file = load_file
            else:
                self.load_file = None

        # Set load style
        if self.load_file is None:
            self.load_style = style
        else:
            self.load_style = 'system_model'

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

        # Check for file and contents
        if self.load_content is not None:
            load_file = self.load_content
        elif self.load_file is not None:
            load_file = self.load_file
        else:
            raise ValueError('load_file not set')

        # Change load symbols kwarg to None if symbols attribute is empty
        if self.symbols is None or len(self.symbols) == 0:
            symbols = None
        else:
            symbols = self.symbols

        # Load ucell
        self.__ucell = am.load(self.load_style, load_file,
                               symbols=symbols, **self.load_options)
        self.ucell.wrap()

        # Update object's symbols and composition
        self.symbols = self.ucell.symbols
        self.composition
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

    def set_values(self, **kwargs: any):
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
        load_content : str or DataModelDict, optional
            The contents of load_file.  Allows for ucell and symbols/family
            to be extracted without the file being accessible at the moment.
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
        if 'load_content' in kwargs:
            self.__load_content = kwargs['load_content']
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
        if 'composition' in kwargs:
            self.composition = kwargs['composition']

        if self.load_file is not None:
            if self.family is None or self.symbols is None:
                self.__extract_model_terms()

    def __extract_model_terms(self):
        """Extracts family and symbols values from load_file if needed"""

        # Check for file and contents
        if self.load_content is not None:
            load_file = self.load_content
        elif self.load_file is not None:
            load_file = self.load_file.as_posix()
        else:
            raise ValueError('load_file not set')

        # Try to extract info from system_model files
        if self.load_style == 'system_model':
            
            try:
                model = DM(load_file).finds(f'{self.modelprefix}system-info')[0]
            except:
                pass
            else:
                # Extract family value or set as load_file's name
                if self.family is None:
                    self.family = model.get('family', Path(self.load_file).stem)

                if self.symbols is None:
                    symbols = model.get('symbol', None)
                    if symbols is not None and len(symbols) > 0:
                        self.symbols = symbols

                if self.composition is None:
                    self.composition = model.get('composition', None)
        
        # Try to extract info from other files
        else:
            if self.family is None:
                self.family = Path(self.load_file).stem
            
            if self.symbols is None:
                symbols = self.ucell.symbols
            self.composition

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
            templateheader = 'Initial System Configuration'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the file and options to load for the initial",
                "atomic configuration."])

        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self) -> dict:
        """dict : The subset-specific input keys and their descriptions."""
        return  {
            'load_file': 
                "The path to the initial configuration file to load.",
            'load_style': 
                "The atomman.load() style indicating the format of the load_file.",
            'load_options': ' '.join([
                "A space-delimited list of key-value pairs for optional",
                "style-specific arguments used by atomman.load()."]),
            'family': ' '.join([
                "A metadata descriptor for relating the load_file back to the",
                "original crystal structure or prototype that the load_file was",
                "based on.  If not given, will use the family field in load_file",
                "if load_style is 'system_model', or the file's name otherwise."]),
            'symbols': ' '.join([
                "A space-delimited list of the potential's atom-model symbols to",
                "associate with the loaded system's atom types.  Required if",
                "load_file does not contain symbol/species information."]),
            'box_parameters': ' '.join([
                "Specifies new box parameters to scale the loaded configuration by.",
                "Can be given either as a list of three or six numbers: 'a b c' for",
                "orthogonal boxes, or 'a b c alpha beta gamma' for triclinic boxes.",
                "The a, b, c parameters are in units of length and the alpha, beta,",
                "gamma angles are in degrees."]),
        }

    @property
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  list(self.templatekeys.keys()) + [
                    'load_content',
                ]

    @property
    def interpretkeys(self) -> list:
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
        d['load_file'] = load_file

        if load_content is not None:
            d['load_content'] = load_content

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
    def modelroot(self) -> str:
        """str : The root element name for the subset terms."""
        baseroot = 'system-info'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model: DM):
        """Loads subset attributes from an existing model."""
        sub = model[self.modelroot]

        d = {}
        d['family'] = sub['family']

        if 'artifact' in sub:
            if  'initial-atomic-system' in sub:
                raise ValueError('found both load file and embedded content for the initial system')
            d['load_style'] = sub['artifact']['format']
            d['load_file'] = sub['artifact']['file']
            load_options = sub['artifact'].get('load_options', None)
        elif 'initial-atomic-system' in sub:
            d['ucell'] = am.load('system_model', sub, key='initial-atomic-system')
        else:
            raise ValueError('neither load file nor embedded content found for the initial system')

        d['symbols'] = sub['symbol']
        d['composition'] = sub.get('composition', None)

        if load_options is not None:
            d['load_options'] = {}
            load_options_keys = ['key', 'index', 'data_set', 'pbc', 'atom_style',
                                'units', 'prop_info']
            d['load_options'] = termtodict(load_options, load_options_keys)
            if 'index' in d['load_options']:
                d['load_options']['index'] = int(d['load_options']['index'])

        self.set_values(**d)

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
        # Check required parameters
        if self.load_file is None:
            raise ValueError('load_file not set')

        system = DM()

        system['family'] = self.family

        if self.load_file is not None:
            system['artifact'] = DM()
            system['artifact']['file'] = self.load_file.as_posix()
            system['artifact']['format'] = self.load_style
            if len(self.load_options) == 0:
                system['artifact']['load_options'] = None
            else:
                system['artifact']['load_options'] = dicttoterm(self.load_options)
        else:
            system['initial-atomic-system'] = self.ucell.model()['atomic-system']

        system['symbol'] = self.symbols
        if self.composition is not None:
            system['composition'] = self.composition

        dict_insert(model, self.modelroot, system, **kwargs)

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""

        root = f'{self.parent.modelroot}.{self.modelroot}'

        return {
            'load_file': load_query(
                style='str_match',
                name=f'{self.prefix}load_file',
                path=f'{root}.artifact.file',
                description='search by the filename for the initial configuration'),
            'family': load_query(
                style='str_match',
                name=f'{self.prefix}family',
                path=f'{root}.family',
                description='search by the configuration family: original prototype or crystal'),
            'symbol': load_query(
                style='str_match',
                name=f'{self.prefix}symbols',
                path=f'{root}.symbol',
                description='search by atomic symbols in the configuration'),
            'composition': load_query(
                style='str_match',
                name=f'{self.prefix}composition',
                path=f'{root}.composition',
                description='search by the composition of the initial configuration'),
        }

########################## Metadata interactions ##############################

    def metadata(self, meta: dict):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        # Check required parameters
        if self.load_file is None:
            meta[f'{self.prefix}load_file'] = None
            meta[f'{self.prefix}load_style'] = None
            meta[f'{self.prefix}load_options'] = None
            meta[f'{self.prefix}parent_key'] = None
        else:
            meta[f'{self.prefix}load_file'] = self.load_file.as_posix()
            meta[f'{self.prefix}load_style'] = self.load_style
            meta[f'{self.prefix}load_options'] = dicttoterm(self.load_options)
            if self.load_file.parent.as_posix() == '.':
                parent = self.load_file.stem
            else:
                parent = self.load_file.parent.name
            meta[f'{self.prefix}parent_key'] = parent

        meta[f'{self.prefix}family'] = self.family
        if self.symbols is None:
            symbolstr = ''
        else:
            symbolstr = ''
            for s in self.symbols:
                if s is not None:
                    symbolstr += f'{s} '
            symbolstr = symbolstr.strip()
        meta[f'{self.prefix}symbols'] = symbolstr

        if self.composition is not None:
            meta[f'{self.prefix}composition'] = self.composition

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
        if self.ucell is None:
            raise ValueError('ucell not loaded')

        input_dict['ucell'] = self.ucell
