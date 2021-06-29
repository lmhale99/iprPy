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
from ..input import termtodict, dicttoterm, boolean

class Dislocation(CalculationSubset):
    """Handles calculation terms for dislocation parameters"""

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

        self.param_file = None
        self.key = None
        self.id = None
        self.slip_hkl = None
        self.ξ_uvw = None
        self.burgers = None
        self.m = 'p'
        self.n = 'c'
        self.shift = None
        self.shiftscale = None
        self.shiftindex = 0
        self.sizemults = None
        self.amin = 0.0
        self.bmin = 0.0
        self.cmin = 0.0
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
    def slip_hkl(self):
        return self.__slip_hkl

    @slip_hkl.setter
    def slip_hkl(self, value):
        if value is None:
            self.__slip_hkl = None
        elif isinstance(value, str):
            value = np.array(value.strip().split(), dtype=float)
        else:
            value = np.asarray(value, dtype=float)
        assert value.shape == (3,) or value.shape == (4,)
        self.__slip_hkl = value.tolist()

    @property
    def ξ_uvw(self):
        return self.__ξ_uvw

    @ξ_uvw.setter
    def ξ_uvw(self, value):
        if value is None:
            self.__ξ_uvw = None
        elif isinstance(value, str):
            value = np.array(value.strip().split(), dtype=float)
        else:
            value = np.asarray(value, dtype=float)
        assert value.shape == (3,) or value.shape == (4,)
        self.__ξ_uvw = value.tolist()

    @property
    def burgers(self):
        return self.__burgers

    @burgers.setter
    def burgers(self, value):
        if value is None:
            self.__burgers = None
        elif isinstance(value, str):
            value = np.array(value.strip().split(), dtype=float)
        else:
            value = np.asarray(value, dtype=float)
        assert value.shape == (3,) or value.shape == (4,)
        self.__burgers = value.tolist()

    @property
    def m(self):
        return self.__m

    @m.setter
    def m(self, value):
        if value is None:
            self.__m = None
        elif isinstance(value, str):
            value = np.array(value.strip().split(), dtype=float)
        else:
            value = np.asarray(value, dtype=float)
        assert value.shape == (3,)
        assert np.isclose(value[0], 1.0) or np.isclose(value[1], 1.0) or np.isclose(value[2], 1.0)
        assert np.isclose(np.linalg.norm(value), 1.0)
        self.__m = value.tolist()

    @property
    def n(self):
        return self.__n

    @n.setter
    def n(self, value):
        if value is None:
            self.__n = None
        elif isinstance(value, str):
            value = np.array(value.strip().split(), dtype=float)
        else:
            value = np.asarray(value, dtype=float)
        assert value.shape == (3,)
        assert np.isclose(value[0], 1.0) or np.isclose(value[1], 1.0) or np.isclose(value[2], 1.0)
        assert np.isclose(np.linalg.norm(value), 1.0)
        self.__n = value.tolist()

    @property
    def shift(self):
        return self.__shift

    @shift.setter
    def shift(self, value):
        if value is None:
            self.__shift = None
        elif isinstance(value, str):
            value = np.array(value.strip().split(), dtype=float)
        else:
            value = np.asarray(value, dtype=float)
        assert value.shape == (3,)
        self.__shift = value.tolist()

    @property
    def shiftscale(self):
        return self.__shiftscale

    @shiftscale.setter
    def shiftscale(self, value):
        self.__shiftscale = boolean(value)

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
    def amin(self):
        return self.__amin

    @amin.setter
    def amin(self, value):
        self.__amin = float(value)

    @property
    def bmin(self):
        return self.__bmin

    @bmin.setter
    def bmin(self, value):
        self.__bmin = float(value)
    
    @property
    def cmin(self):
        return self.__cmin

    @cmin.setter
    def cmin(self, value):
        self.__cmin = float(value)

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
        if 'slip_hkl' in kwargs:
            self.slip_hkl = kwargs['slip_hkl']
        if 'ξ_uvw' in kwargs:
            self.ξ_uvw = kwargs['ξ_uvw']
        if 'burgers' in kwargs:
            self.burgers = kwargs['burgers']
        if 'm' in kwargs:
            self.m = kwargs['m']
        if 'n' in kwargs:
            self.n = kwargs['n']
        if 'shift' in kwargs:
            self.shift = kwargs['shift']
        if 'shiftscale' in kwargs:
            self.shiftscale = kwargs['shiftscale']
        if 'shiftindex' in kwargs:
            self.shiftindex = kwargs['shiftindex']
        if 'sizemults' in kwargs:
            self.sizemults = kwargs['sizemults']
        if 'amin' in kwargs:
            self.amin = kwargs['amin']
        if 'bmin' in kwargs:
            self.bmin = kwargs['bmin']
        if 'cmin' in kwargs:
            self.cmin = kwargs['cmin']        
        if 'family' in kwargs:
            self.family = kwargs['family']         
        

####################### Parameter file interactions ###########################

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return '# Dislocation defect parameters'

    @property
    def templatekeys(self):
        """
        list : The input keys (without prefix) that appear in the input file.
        """
        return [
            'dislocation_file',
            'dislocation_slip_hkl',
            'dislocation_ξ_uvw',
            'dislocation_burgers',
            'dislocation_m',
            'dislocation_n',
            'dislocation_shift',
            'dislocation_shiftscale',
            'dislocation_shiftindex',
            'sizemults',
            'amin',
            'bmin',
            'cmin',
        ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return self.templatekeys + [
            'dislocation_family',
            'dislocation_content',
        ]

    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return self.preparekeys + [
            'dislocation_model', 
        ]

    #@property
    #def keyset(self):
    #    """
    #    list : The input keyset for preparing.
    #    """
    #    keys = self.preparekeys
    #    keys.pop(keys.index('sizemults'))
    #    keys.pop(keys.index('amin'))
    #    keys.pop(keys.index('bmin'))
    #    keys.pop(keys.index('cmin'))
    #    return self._pre(keys)

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
        self.param_file = input_dict.get(keymap['dislocation_file'], None)
        self.__content = input_dict.get(keymap['dislocation_content'], None)
        
        # Replace defect model with defect content if given
        param_file = self.param_file
        if self.__content is not None:
            param_file = self.__content
        
        # Extract parameters from a file
        if param_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('dislocation_slip_hkl',
                        'dislocation_ξ_uvw',
                        'dislocation_burgers',
                        'dislocation_m',
                        'dislocation_n',
                        'dislocation_shift',
                        'dislocation_shiftscale',
                        'dislocation_shiftindex'):
                if keymap[key] in input_dict:
                    raise ValueError(f"{keymap[key]} and {keymap['dislocation_file']} cannot both be supplied")
            
            # Load defect model
            self.__model = model = DM(param_file).find('dislocation')
            
            # Extract parameter values from defect model
            self.key = model['key']
            self.id = model['id']
            self.family = model['system-family']
            self.slip_hkl = model['calculation-parameter']['slip_hkl']
            self.ξ_uvw = model['calculation-parameter']['ξ_uvw']
            self.burgers = model['calculation-parameter']['burgers']
            self.m = model['calculation-parameter']['m']
            self.n = model['calculation-parameter']['n']
            self.shift = model['calculation-parameter'].get('shift', None)
            self.shiftindex = model['calculation-parameter'].get('shiftindex', None)
            self.shiftscale = boolean(model['calculation-parameter'].get('shiftscale', False))
        
        # Set parameter values directly
        else: 
            self.__model = None
            self.key = None
            self.id = None
            self.family = self.parent.system.family
            self.slip_hkl = input_dict[keymap['dislocation_slip_hkl']]
            self.ξ_uvw = input_dict[keymap['dislocation_ξ_uvw']]
            self.burgers = input_dict[keymap['dislocation_burgers']]
            self.m = input_dict.get(keymap['dislocation_m'], '0 1 0')
            self.n = input_dict.get(keymap['dislocation_n'], '0 0 1')
            self.shift = input_dict.get(keymap['dislocation_shift'], None)
            self.shiftscale = boolean(input_dict.get(keymap['dislocation_shiftscale'], False))
            self.shiftindex = input_dict.get(keymap['dislocation_shiftindex'], None)
                    
        # Check defect parameters
        if not np.isclose(self.m.dot(self.n), 0.0):
            raise ValueError("dislocation_m and dislocation_n must be orthogonal")

        # Set default values for fault system manipulations
        self.sizemults = input_dict.get(keymap['sizemults'], '1 1 1')
        self.amin = float(input_dict.get(keymap['amin'], 0.0))
        self.bmin = float(input_dict.get(keymap['bmin'], 0.0))
        self.cmin = float(input_dict.get(keymap['cmin'], 0.0))

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        baseroot = 'stacking-fault'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        sf = model[self.modelroot]

        self.__model = None
        self.__param_file = None
        self.key = sf['key']
        self.id = sf['id']
        self.family = sf['system-family']

        cp = sf['calculation-parameter']
        self.hkl = cp['hkl']
        self.a1vect_uvw = cp['a1vect_uvw']
        self.a2vect_uvw = cp['a2vect_uvw']
        self.shiftindex = int(cp['shiftindex'])
        self.cutboxvector = cp['cutboxvector']
        self.faultpos_rel = float(cp['faultpos_rel'])
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
        model[self.modelroot] = disl = DM()
        disl['key'] = self.key
        disl['id'] = self.id
        if self.__model is not None:
            disl['character'] = self.__model['character']
            disl['Burgers-vector'] = self.__model['Burgers-vector']
            disl['slip-plane'] = self.__model['slip-plane']
            disl['line-direction'] = self.__model['line-direction']
        disl['system-family'] = self.family
        disl['calculation-parameter'] = cp = DM()
        cp['slip_hkl'] = f'{self.slip_hkl[0]} {self.slip_hkl[1]} {self.slip_hkl[2]}'
        cp['ξ_uvw'] = f'{self.ξ_uvw[0]} {self.ξ_uvw[1]} {self.ξ_uvw[2]}'
        cp['burgers'] = f'{self.burgers[0]} {self.burgers[1]} {self.burgers[2]}'
        cp['m'] = f'{self.m[0]} {self.m[1]} {self.m[2]}'
        cp['n'] = f'{self.n[0]} {self.n[1]} {self.n[2]}'
        if self.shift is not None:
            cp['shift'] = f'{self.shift[0]} {self.shift[1]} {self.shift[2]}'
        if self.shiftindex is not None:
            cp['shiftindex'] = str(self.shiftindex)
        cp['shiftscale'] = str(self.shiftscale)

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
        
    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        prefix = self.prefix

        meta[f'{prefix}dislocation_key'] = self.key
        meta[f'{prefix}dislocation_id'] = self.id
        meta[f'{prefix}stackingfault_family'] = self.family
        meta[f'{prefix}dislocation_slip_hkl'] = self.slip_hkl
        meta[f'{prefix}dislocation_ξ_uvw'] = self.ξ_uvw
        meta[f'{prefix}dislocation_burgers'] = self.burgers
        meta[f'{prefix}dislocation_m'] = self.m
        meta[f'{prefix}dislocation_n'] = self.n
        meta[f'{prefix}dislocation_shift'] = self.shift
        meta[f'{prefix}dislocation_shiftscale'] = self.shiftscale
        meta[f'{prefix}dislocation_shiftindex'] = self.shiftindex
        meta[f'{prefix}a_mult1'] = 0
        meta[f'{prefix}a_mult2'] = self.sizemults[0]
        meta[f'{prefix}b_mult1'] = 0
        meta[f'{prefix}b_mult2'] = self.sizemults[1]
        meta[f'{prefix}c_mult1'] = 0
        meta[f'{prefix}c_mult2'] = self.sizemults[2]

########################### Calculation interactions ##########################

    def calc_inputs(self, input_dict):

        input_dict['dislocation_burgers'] = self.burgers
        input_dict['dislocation_ξ_uvw'] = self.ξ_uvw
        input_dict['dislocation_slip_hkl'] = self.slip_hkl
        input_dict['dislocation_m'] = self.m
        input_dict['dislocation_n'] = self.n
        input_dict['sizemults'] = self.sizemults
        input_dict['amin'] = self.amin
        input_dict['bmin'] = self.bmin
        input_dict['cmin'] = self.cmin
        input_dict['dislocation_shift'] = self.shift
        input_dict['dislocation_shiftscale'] = self.shiftscale
        input_dict['dislocation_shiftindex'] = self.shiftindex
