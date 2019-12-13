# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset
from ... import termtodict
from ....tools import aslist

class AtommanSystemLoad(Subset):
    """
    Defines interactions for input keys associated with specifying input/output
    units.
    """
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

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Initial system configuration to load'
        
        return super().template(header=header)

    def interpret(self, input_dict, build=True):
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
        load_file = input_dict[keymap['load_file']]
        load_style = input_dict.get(keymap['load_style'], 'system_model')
        load_options = input_dict.get(keymap['load_options'], None)
        load_content = input_dict.get(keymap['load_content'], None)
        family = input_dict.get(keymap['family'], None)
        symbols = input_dict.get(keymap['symbols'], None)
        box_parameters = input_dict.get(keymap['box_parameters'], None)
        elastic_file = input_dict.get(keymap['elasticconstants_content'], None)
    
        # Use load_content instead of load_file if given
        if load_content is not None:
            load_file = load_content
        
        # Separate load_options terms
        load_options_kwargs= {}
        if load_options is not None:
            load_options_keys = ['key', 'index', 'data_set', 'pbc', 'atom_style',
                                'units', 'prop_info']
            load_options_kwargs = termtodict(load_options, load_options_keys)
            if 'index' in load_options_kwargs:
                load_options_kwargs['index'] = int(load_options_kwargs['index'])
        
        # Build ucell
        if build is True:
            
            # Load ucell
            ucell = am.load(load_style, load_file, **load_options_kwargs)
            
            # Replace symbols if given
            if symbols is not None:
                ucell.symbols = symbols.split()
            symbols = list(ucell.symbols)
            
            # Scale ucell by box_parameters
            if box_parameters is not None:
                box_params = box_parameters.split()
                
                # len of 4 or 7 indicates that last term is a length unit
                if len(box_params) == 4 or len(box_params) == 7:
                    unit = box_params[-1]
                    box_params = box_params[:-1]
                
                # Use calculation's length_unit if unit not given in box_parameters
                else:
                    unit = input_dict['length_unit']
                
                # Convert to the specified units
                box_params = np.array(box_params, dtype=float)
                box_params[:3] = uc.set_in_units(box_params[:3], unit)
                
                # Three box_parameters means a, b, c
                if len(box_params) == 3:
                    ucell.box_set(a=box_params[0], b=box_params[1],
                                c=box_params[2], scale=True)
                
                # Six box_parameters means a, b, c, alpha, beta, gamma
                elif len(box_params) == 6:
                    ucell.box_set(a=box_params[0], b=box_params[1], c=box_params[2],
                                alpha=box_params[3], beta=box_params[4],
                                gamma=box_params[5], scale=True) 
                
                # Other options are invalid
                else:
                    ValueError('Invalid box_parameters command')

            # Add model-specific charges if needed
            if (keymap['potential'] in input_dict
                and 'charge' not in ucell.atoms_prop()):
                potential = input_dict[keymap['potential']]
                ucell.atoms.prop_atype('charge', potential.charges(ucell.symbols))
        
        # Don't build
        else:
            # Try to get symbols by loading file
            if symbols is None:
                try:
                    ucell = am.load(load_style, load_file, **load_options_kwargs)
                except:
                    pass
                else:
                    symbols = list(ucell.symbols)
            ucell = None
        
        # Extract system_family (and possibly symbols) from parent model
        if elastic_file is not None:
            model = DM(elastic_file)
        elif load_style == 'system_model':
            model = DM(load_file)
        else:
            model = None
        
        if model is not None:    
            # Check if family in model
            if family is None:
                try:
                    family = model.find('system-info')['family']
                except:
                    family = None
            
            # Extract symbols if needed
            if symbols is None or symbols[0] is None:
                try:
                    symbols = model.find('system-info')['symbol']
                except:
                    pass
                else:
                    if ucell is not None:
                        ucell.symbols = symbols
                        symbols = list(ucell.symbols)
        
        # Pull single symbols out of the list
        if len(symbols) == 1:
            symbols = symbols[0]
        
        # If no family given/found, use load_file's stem
        if family is None:
            family = Path(input_dict[keymap['load_file']]).stem
        
        # Save processed terms
        input_dict[keymap['load_style']] = load_style
        input_dict[keymap['load_options']] = load_options
        input_dict[keymap['box_parameters']] = box_parameters
        input_dict[keymap['family']] = family
        input_dict[keymap['ucell']] = ucell
        input_dict[keymap['symbols']] = symbols

    def buildcontent(self, record_model, input_dict, results_dict=None):
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
        
        prefix = self.prefix
        modelprefix = prefix.replace('_', '-')

        # Save info on system file loaded
        record_model[f'{modelprefix}system-info'] = system = DM()
        system['family'] = input_dict[f'{prefix}family']
        system['artifact'] = DM()
        system['artifact']['file'] = input_dict[f'{prefix}load_file']
        system['artifact']['format'] = input_dict[f'{prefix}load_style']
        system['artifact']['load_options'] = input_dict[f'{prefix}load_options']
        system['symbol'] = input_dict[f'{prefix}symbols']
        
    def todict(self, record_model, params, full=True, flat=False):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        record_model : DataModelDict.DataModelDict
            The record content (after root element) to interpret.
        params : dict
            The dictionary to add the interpreted content to
        full : bool, optional
            Flag used by the calculation records.  A True value will include
            terms for both the calculation's input and results, while a value
            of False will only include input terms (Default is True).
        flat : bool, optional
            Flag affecting the format of the dictionary terms.  If True, the
            dictionary terms are limited to having only str, int, and float
            values, which is useful for comparisons.  If False, the term
            values can be of any data type, which is convenient for analysis.
            (Default is False).
        """
        prefix = self.prefix
        modelprefix = prefix.replace('_', '-')

        system = record_model[f'{modelprefix}system-info']
        
        params[f'{prefix}load_file'] = system['artifact']['file']
        params[f'{prefix}load_style'] = system['artifact']['format']
        params[f'{prefix}load_options'] = system['artifact']['load_options']
        params[f'{prefix}family'] = system['family']
        symbols = aslist(system['symbol'])
        
        parent_file = Path(system['artifact']['file'])
        if parent_file.parent.as_posix() == '.':
            parent = parent_file.stem
        else:
            parent = parent_file.parent.as_posix()
        params[f'{prefix}parent_key'] = parent

        if flat is True:
            try:
                params[f'{prefix}symbols'] = ' '.join(symbols)
            except:
                params[f'{prefix}symbols'] = np.nan
        else:
            params[f'{prefix}symbols'] = symbols