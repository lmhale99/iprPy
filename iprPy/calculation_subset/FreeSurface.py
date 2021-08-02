# coding: utf-8

# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from datamodelbase import query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from . import CalculationSubset
from ..tools import dict_insert, aslist
from ..input import boolean, value

class FreeSurface(CalculationSubset):
    """Handles calculation terms for free surface parameters"""

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

        self.param_file = None
        self.key = None
        self.id = None
        self.hkl = None
        self.cellsetting = 'p'
        self.cutboxvector = 'c'
        self.shiftindex = 0
        self.sizemults = [1,1,1]
        self.minwidth = 0.0
        self.even = False
        self.family = None
        self.__content = None
        self.__model = None

############################## Class attributes ################################
    
    @property
    def param_file(self):
        return self.__param_file

    @param_file.setter
    def param_file(self, value):
        if value is None:
            self.__param_file = None
        else:
            self.__param_file = Path(value)

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        if value is None:
            self.__key = None
        else:
            self.__key = str(value)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if value is None:
            self.__id = None
        else:
            self.__id = str(value)

    @property
    def hkl(self):
        return self.__hkl

    @hkl.setter
    def hkl(self, value):
        if value is None:
            self.__hkl = None
        else:
            if isinstance(value, str):
                value = np.array(value.strip().split(), dtype=float)
            else:
                value = np.asarray(value, dtype=float)
            assert value.shape == (3,) or value.shape == (4,)
            self.__hkl = value.tolist()

    @property
    def cellsetting(self):
        return self.__cellsetting

    @cellsetting.setter
    def cellsetting(self, value):
        if value not in ['p', 'a', 'b', 'c', 'i', 'f']:
            raise ValueError('invalid surface cellsetting')
        self.__cellsetting = str(value)

    @property
    def cutboxvector(self):
        return self.__cutboxvector

    @cutboxvector.setter
    def cutboxvector(self, value):
        if value not in ['a', 'b', 'c']:
            raise ValueError('invalid surface cutboxvector')
        self.__cutboxvector = str(value)

    @property
    def shiftindex(self):
        return self.__shiftindex

    @shiftindex.setter
    def shiftindex(self, value):
        self.__shiftindex = int(value)

    @property
    def sizemults(self):
        return self.__sizemults

    @sizemults.setter
    def sizemults(self, value):
        if isinstance(value, str):
            value = np.array(value.strip().split(), dtype=int)
        else:
            value = np.asarray(value, dtype=int)
        if value.shape != (3,):
            raise ValueError('Invalid sizemults command: exactly 3 sizemults required for this calculation')
        self.__sizemults = value.tolist()

    @property
    def minwidth(self):
        return self.__minwidth

    @minwidth.setter
    def minwidth(self, value):
        self.__minwidth = float(value)

    @property
    def even(self):
        return self.__even

    @even.setter
    def even(self, value):
        self.__even = boolean(value)

    @property
    def family(self):
        return self.__family

    @family.setter
    def family(self, value):
        if value is None:
            self.__family = None
        else:
            self.__family = str(value)

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
        if 'param_file' in kwargs:
            self.param_file = kwargs['param_file']
        if 'key' in kwargs:
            self.key = kwargs['key']
        if 'id' in kwargs:
            self.id = kwargs['id']
        if 'hkl' in kwargs:
            self.hkl = kwargs['hkl']
        if 'cellsetting' in kwargs:
            self.cellsetting = kwargs['cellsetting']
        if 'cutboxvector' in kwargs:
            self.cutboxvector = kwargs['cutboxvector']
        if 'shiftindex' in kwargs:
            self.shiftindex = kwargs['shiftindex']
        if 'sizemults' in kwargs:
            self.sizemults = kwargs['sizemults']
        if 'minwidth' in kwargs:
            self.minwidth = kwargs['minwidth']
        if 'even' in kwargs:
            self.even = kwargs['even']
        if 'family' in kwargs:
            self.family = kwargs['family']           

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
            templateheader = 'Free Surface'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the parameter set that defines a free surface."])
        
        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self):
        """dict : The subset-specific input keys and their descriptions."""
        
        return {
            'surface_file': ' '.join([
                "The path to a free_surface record file that collects the",
                "parameters associated with a specific free surface."]),
            'surface_hkl': ' '.join([
                "The Miller (hkl) plane for the surface given as three",
                "space-delimited integers."]),
            'surface_cellsetting': ' '.join([
                "The conventional cell setting to take surface_hkl relative to",
                "if the loaded unit cell is a primitive cell.  Allowed values are 'p',",
                "'c', 'i', 'a', 'b' and 'c'."]),
            'surface_cutboxvector': ' '.join([
                "Indicates which of the three box vectors ('a', 'b', or 'c')",
                "that the surface plane will be made along.",
                "surface. Default value is 'c'."]),
            'surface_shiftindex': ' '.join([
                "A rigid body shift will be applied to the atoms such that the",
                "created surface plane will be halfway between two atomic planes.",
                "This is an integer value that changes which set of atomic planes",
                "that the plane is inserted between.  Changing this effectively",
                "changes the termination planes."]),
            'sizemults': ' '.join([
                "Multiplication parameters to construct a supercell from the rotated",
                "system.  Limited to three values for free surface generation."]),
            'surface_minwidth': ' '.join([
                "Specifies a mimimum width in length units that the system must be",
                "along the cutboxvector direction. The associated sizemult value",
                "will be increased if necessary to ensure this. Default value is 0.0."]),
            'surface_even': ' '.join([
                "If True, the number of replicas in the cutboxvector direction will"
                "be even. Default value is False."]),
        }
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return list(self.templatekeys.keys()) + [
            'surface_family',
            'surface_content'
        ]
    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return self.preparekeys + [
            'surface_model',
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
        self.param_file = input_dict.get(keymap['surface_file'], None)
        self.__content = input_dict.get(keymap['surface_content'], None)
        
        # Replace defect model with defect content if given
        param_file = self.param_file
        if self.__content is not None:
            param_file = self.__content

        # Extract parameters from a file
        if param_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('surface_hkl',
                        'surface_shiftindex',
                        'surface_cellsetting',
                        'surface_cutboxvector'):
                if keymap[key] in input_dict:
                    raise ValueError(f"{keymap[key]} and {keymap['surface_file']} cannot both be supplied")
            
            # Load defect model
            self.__model = model = DM(param_file).find('free-surface')
                
            # Extract parameter values from defect model
            self.key = model['key']
            self.id = model['id']
            self.family = model['system-family']
            self.hkl = model['calculation-parameter']['hkl']
            self.shiftindex = int(model['calculation-parameter'].get('shiftindex', 0))
            self.cutboxvector = model['calculation-parameter']['cutboxvector']
            self.cellsetting = model['calculation-parameter'].get('cellsetting', 'p')
        
        # Set parameter values directly
        else:
            self.__model = None
            self.key = None
            self.id = None
            self.family = self.parent.system.family
            self.hkl = input_dict[keymap['surface_hkl']]
            self.shiftindex = int(input_dict.get(keymap['surface_shiftindex'], 0))
            self.cutboxvector = input_dict.get(keymap['surface_cutboxvector'], 'c')
            self.cellsetting = input_dict.get(keymap['surface_cellsetting'], 'p')
    
        # Set default values for fault system manipulations
        self.sizemults = input_dict.get(keymap['sizemults'], '1 1 1')
        self.minwidth = value(input_dict, keymap['surface_minwidth'], default_term='0.0 angstrom',
                              default_unit=self.parent.units.length_unit)
        self.even = boolean(input_dict.get(keymap['surface_even'], False))


########################### Data model interactions ###########################

    @property
    def modelroot(self):
        baseroot = 'free-surface'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        surf = model[self.modelroot]

        self.__model = None
        self.__param_file = None
        self.key = surf['key']
        self.id = surf['id']
        self.family = surf['system-family']

        cp = surf['calculation-parameter']
        self.hkl = cp['hkl']
        self.shiftindex = int(cp['shiftindex'])
        self.cutboxvector = cp['cutboxvector']
        self.cellsetting = cp['cellsetting'] 

        run_params = model['calculation']['run-parameter']
        
        a_mult = run_params[f'{self.modelprefix}size-multipliers']['a'][1]
        b_mult = run_params[f'{self.modelprefix}size-multipliers']['b'][1]
        c_mult = run_params[f'{self.modelprefix}size-multipliers']['c'][1]
        self.sizemults = [a_mult, b_mult, c_mult]
        self.minwidth = uc.value_unit(run_params[f'{self.modelprefix}minimum-width'])

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
        # Save defect parameters
        model[self.modelroot] = surf = DM()
        surf['key'] = self.key
        surf['id'] = self.id
        surf['system-family'] = self.family
        surf['calculation-parameter'] = cp = DM()
        if len(self.hkl) == 3:
            cp['hkl'] = f'{self.hkl[0]} {self.hkl[1]} {self.hkl[2]}'
        else:
            cp['hkl'] = f'{self.hkl[0]} {self.hkl[1]} {self.hkl[2]} {self.hkl[3]}'
        cp['shiftindex'] = str(self.shiftindex)
        cp['cutboxvector'] = self.cutboxvector
        cp['cellsetting'] = self.cellsetting

        # Build paths if needed
        if 'calculation' not in model:
            model['calculation'] = DM()
        if 'run-parameter' not in model['calculation']:
            model['calculation']['run-parameter'] = DM()

        run_params = model['calculation']['run-parameter']
        
        run_params[f'{self.modelprefix}size-multipliers'] = DM()
        run_params[f'{self.modelprefix}size-multipliers']['a'] = sorted([0, self.sizemults[0]])
        run_params[f'{self.modelprefix}size-multipliers']['b'] = sorted([0, self.sizemults[1]])
        run_params[f'{self.modelprefix}size-multipliers']['c'] = sorted([0, self.sizemults[2]])
        run_params[f'{self.modelprefix}minimum-width'] = uc.model(self.minwidth,
                                                             self.parent.units.length_unit)
        
    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        prefix = self.prefix

        meta[f'{prefix}surface_key'] = self.key
        meta[f'{prefix}surface_id'] = self.id
        meta[f'{prefix}surface_family'] = self.family
        meta[f'{prefix}surface_hkl'] = self.hkl
        meta[f'{prefix}surface_shiftindex'] = self.shiftindex
        meta[f'{prefix}a_mult1'] = 0
        meta[f'{prefix}a_mult2'] = self.sizemults[0]
        meta[f'{prefix}b_mult1'] = 0
        meta[f'{prefix}b_mult2'] = self.sizemults[1]
        meta[f'{prefix}c_mult1'] = 0
        meta[f'{prefix}c_mult2'] = self.sizemults[2]

    @staticmethod
    def pandasfilter(dataframe, surface_key=None, surface_id=None):

        matches = (
            query.str_match.pandas(dataframe, 'surface_key', surface_key)
            &query.str_match.pandas(dataframe, 'surface_id', surface_id)
        )
        return matches

    @staticmethod
    def mongoquery(modelroot, surface_key=None, surface_id=None):
        mquery = {}
        root = f'content.{modelroot}'
        query.str_match.mongo(mquery, f'{root}.free-surface.key', surface_key)
        query.str_match.mongo(mquery, f'{root}.free-surface.id', surface_id)
        return mquery

    @staticmethod
    def cdcsquery(modelroot, surface_key=None, surface_id=None):
        mquery = {}
        root = modelroot
        query.str_match.mongo(mquery, f'{root}.free-surface.key', surface_key)
        query.str_match.mongo(mquery, f'{root}.free-surface.id', surface_id)
        return mquery      

########################### Calculation interactions ##########################

    def calc_inputs(self, input_dict):
        
        if self.hkl is None:
            raise ValueError('hkl not set')

        input_dict['hkl'] = self.hkl
        
        input_dict['sizemults'] = self.sizemults
        input_dict['minwidth'] = self.minwidth
        input_dict['even'] = self.even
        input_dict['conventional_setting'] = self.cellsetting
        input_dict['cutboxvector'] = self.cutboxvector
        input_dict['shiftindex'] = self.shiftindex