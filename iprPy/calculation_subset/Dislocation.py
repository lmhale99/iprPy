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
from ..input import termtodict, dicttoterm, boolean, value

class Dislocation(CalculationSubset):
    """Handles calculation terms for dislocation parameters"""

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
        self.slip_hkl = None
        self.ξ_uvw = None
        self.burgers = None
        self.m = None
        self.n = None
        self.shift = None
        self.shiftscale = False
        self.shiftindex = 0
        self.sizemults = [1,1,1]
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
        else:
            if isinstance(value, str):
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
        else:
            if isinstance(value, str):
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
        else:
            if isinstance(value, str):
                value = np.array(value.strip().split(), dtype=float)
            else:
                value = np.asarray(value, dtype=float)
            assert value.shape == (3,) or value.shape == (4,)
            self.__burgers = value

    @property
    def m(self):
        return self.__m

    @m.setter
    def m(self, value):
        if value is None:
            self.__m = None
        else:
            if isinstance(value, str):
                value = np.array(value.strip().split(), dtype=float)
            else:
                value = np.asarray(value, dtype=float)
            assert value.shape == (3,)
            assert np.isclose(value[0], 1.0) or np.isclose(value[1], 1.0) or np.isclose(value[2], 1.0)
            assert np.isclose(np.linalg.norm(value), 1.0)
            self.__m = value

    @property
    def n(self):
        return self.__n

    @n.setter
    def n(self, value):
        if value is None:
            self.__n = None
        else:
            if isinstance(value, str):
                value = np.array(value.strip().split(), dtype=float)
            else:
                value = np.asarray(value, dtype=float)
            assert value.shape == (3,)
            assert np.isclose(value[0], 1.0) or np.isclose(value[1], 1.0) or np.isclose(value[2], 1.0)
            assert np.isclose(np.linalg.norm(value), 1.0)
            self.__n = value

    @property
    def shift(self):
        return self.__shift

    @shift.setter
    def shift(self, value):
        if value is None:
            self.__shift = None
        else:
            if isinstance(value, str):
                value = np.array(value.strip().split(), dtype=float)
            else:
                value = np.asarray(value, dtype=float)
            assert value.shape[0] == 3
            self.__shift = value

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
        if value is None:
            self.__shiftindex = None
        else:
            self.__shiftindex = int(value)

    @property
    def a_mults(self):
        """tuple: Size multipliers for the rotated a box vector"""
        return self.__a_mults

    @a_mults.setter
    def a_mults(self, value):
        value = aslist(value)
        
        if len(value) == 1:
            value[0] = int(value[0])
            if value[0] > 0:
                value = [0, value[0]]
            
            # Add 0 after if value is negative
            elif value[0] < 0:
                value = [value[0], 0]
            
            else:
                raise ValueError('a_mults values cannot both be 0')
        
        elif len(value) == 2:
            value[0] = int(value[0])
            value[1] = int(value[1])
            if value[0] > 0:
                raise ValueError('First a_mults value must be <= 0')
            if value[1] < 0:
                raise ValueError('Second a_mults value must be >= 0')
            if value[0] == value[1]:
                raise ValueError('a_mults values cannot both be 0')
        
        self.__a_mults = tuple(value)

    @property
    def b_mults(self):
        """tuple: Size multipliers for the rotated b box vector"""
        return self.__b_mults

    @b_mults.setter
    def b_mults(self, value):
        value = aslist(value)
        
        if len(value) == 1:
            value[0] = int(value[0])
            if value[0] > 0:
                value = [0, value[0]]
            
            # Add 0 after if value is negative
            elif value[0] < 0:
                value = [value[0], 0]
            
            else:
                raise ValueError('b_mults values cannot both be 0')
        
        elif len(value) == 2:
            value[0] = int(value[0])
            value[1] = int(value[1])
            if value[0] > 0:
                raise ValueError('First b_mults value must be <= 0')
            if value[1] < 0:
                raise ValueError('Second b_mults value must be >= 0')
            if value[0] == value[1]:
                raise ValueError('b_mults values cannot both be 0')
        
        self.__b_mults = tuple(value)
    
    @property
    def c_mults(self):
        """tuple: Size multipliers for the rotated c box vector"""
        return self.__c_mults

    @c_mults.setter
    def c_mults(self, value):
        value = aslist(value)
        
        if len(value) == 1:
            value[0] = int(value[0])
            if value[0] > 0:
                value = [0, value[0]]
            
            # Add 0 after if value is negative
            elif value[0] < 0:
                value = [value[0], 0]
            
            else:
                raise ValueError('c_mults values cannot both be 0')
        
        elif len(value) == 2:
            value[0] = int(value[0])
            value[1] = int(value[1])
            if value[0] > 0:
                raise ValueError('First c_mults value must be <= 0')
            if value[1] < 0:
                raise ValueError('Second c_mults value must be >= 0')
            if value[0] == value[1]:
                raise ValueError('c_mults values cannot both be 0')
        
        self.__c_mults = tuple(value)

    @property
    def sizemults(self):
        """tuple: All three sets of size multipliers"""
        return (self.a_mults, self.b_mults, self.c_mults)

    @sizemults.setter
    def sizemults(self, value):
        if len(value) == 3:
            self.a_mults = value[0]
            self.b_mults = value[1]
            self.c_mults = value[2]
        elif len(value) == 6:
            self.a_mults = value[0:2]
            self.b_mults = value[2:4]
            self.c_mults = value[4:6]
        else:
            raise ValueError('len of sizemults must be 3 or 6')

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
        param_file : str, optional
            The path to a file that fully defines the input parameters for
            a specific defect type.
        key : str, optional
            The UUID4 unique key associated with the defect parameter set.
        id : str, optional
            The unique id associated with the defect parameter set.
        slip_hkl : str or array-like object, optional
            The Miller (hkl) slip plane.
        ξ_uvw : str or array-like object, optional
            The Miller [uvw] line direction.
        burgers : str or array-like object, optional
            The Miller Burgers vector
        m : str or array-like object, optional
            The Cartesian unit vector to align with the dislocation solution's
            m coordinate vector (perpendicular to n and ξ).
        n : str or array-like object, optional
            The Cartesian unit vector to align with the dislocation solution's
            n coordinate vector (slip plane normal).
        shift : str or array-like object, optional
            A rigid body shift to apply to all atoms.
        shiftscale : bool, optional
            Indicates if shift is absolute Cartesian or scaled relative to the
            rotated cell's box parameters
        shiftindex : int, optional
            If given, the shift will automatically be selected to position the
            slip plane halfway between atomic planes.  Different values select
            different neighboring atomic planes.
        sizemults : str or array-like object, optional
            The system size multipliers.  
        amin : float, optional
            A minimum width for the box's a vector direction.  The sizemults
            will be modified to ensure this as needed.
        bmin :
            A minimum width for the box's b vector direction.  The sizemults
            will be modified to ensure this as needed.
        cmin :
            A minimum width for the box's c vector direction.  The sizemults
            will be modified to ensure this as needed.
        family : str or None, optional
            The system's family identifier that the defect is defined for.
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
            templateheader = 'Dislocation'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the parameter set that defines a dislocation type",
                "and how to orient it relative to the atomic system."])
        
        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self):
        """dict : The subset-specific input keys and their descriptions."""
        
        return {
            'dislocation_file': ' '.join([
                "The path to a dislocation record file that collects the",
                "parameters for a specific dislocation type."]),
            'dislocation_slip_hkl': ' '.join([
                "The Miller (hkl) slip plane for the dislocation given as three",
                "space-delimited integers."]),
            'dislocation_ξ_uvw': ' '.join([
                "The Miller [uvw] line vector direction for the dislocation given",
                "as three space-delimited integers. The angle between burgers and",
                "ξ_uvw determines the dislocation's character."]),
            'dislocation_burgers': ' '.join([
                "The Miller Burgers vector for the dislocation given as three",
                "space-delimited floats."]),
            'dislocation_m': ' '.join([
                "The Cartesian vector of the final system that the dislocation",
                "solution's m vector (in-plane, perpendicular to ξ) should align",
                "with. Given as three space-delimited numbers.  Limited to being"
                "parallel to one of the three Cartesian axes."]),
            'dislocation_n': ' '.join([
                "The Cartesian vector of the final system that the dislocation",
                "solution's n vector (slip plane normal) should align",
                "with. Given as three space-delimited numbers.  Limited to being"
                "parallel to one of the three Cartesian axes."]),
            'dislocation_shift': ' '.join([
                "A rigid body shift to apply to the atoms in the system after it",
                "has been rotated to the correct orientation.  This controls where",
                "the dislocation is placed relative to the atomic positions as the",
                "dislocation line is always inserted at coordinates (0,0) for the",
                "two Cartesian axes aligned with m and n.  Specified as three",
                "floating point numbers."]),
            'dislocation_shiftscale': ' '.join([
                "boolean indicating if the dislocation_shift value is a Cartesian",
                "vector (False, default) or if it is scaled relative to the rotated cell's",
                "box parameters prior to applying sizemults."]),
            'dislocation_shiftindex': ' '.join([
                "An integer that if given will result in a shift being automatically",
                "determined and used such that the dislocation's slip plane will be",
                "positioned halfway between two atomic planes.  Changing the integer",
                "value changes which set of planes the slip plane is positioned between.",
                "Note that shiftindex values only shift atoms in the slip plane normal",
                "direction and therefore may not be the ideal positions for some",
                "dislocation cores."]),
            'sizemults': ' '.join([
                "Multiplication parameters to construct a supercell from the rotated",
                "system.  Limited to three values for dislocation generation.",
                "Values must be even for the two box vectors not aligned with the",
                "dislocation line.  The system will be replicated equally in the",
                "positive and negative directions for those two box vectors."]),
            'amin': ' '.join([
                "Specifies a minimum width in length units that the resulting",
                "system's a box vector must have.  The associated sizemult value",
                "will be increased if necessary to ensure this. Default value is 0.0."]),
            'bmin': ' '.join([
                "Specifies a minimum width in length units that the resulting",
                "system's b box vector must have.  The associated sizemult value",
                "will be increased if necessary to ensure this. Default value is 0.0."]),
            'cmin': ' '.join([
                "Specifies a minimum width in length units that the resulting",
                "system's c box vector must have.  The associated sizemult value",
                "will be increased if necessary to ensure this. Default value is 0.0."]),
        }
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return list(self.templatekeys.keys()) + [
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

    @property
    def multikeys(self):
        """
        list: Calculation subset key sets that can have multiple values during prepare.
        """ 
        # Define key set for system size parameters
        sizekeys = ['sizemults', 'amin', 'bmin', 'cmin']
        
        # Define key set for defect parameters as the remainder
        defectkeys = []
        for key in self.preparekeys:
            if key not in sizekeys:
                defectkeys.append(key)

        # Add prefixes and return
        return [
            self._pre(sizekeys),
            self._pre(defectkeys)
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
        sizemults = input_dict.get(keymap['sizemults'], '1 1 1')
        self.sizemults = np.array(sizemults.strip().split(), dtype=int)
        
        self.amin = value(input_dict, keymap['amin'], default_term='0.0 angstrom',
                          default_unit=self.parent.units.length_unit)
        self.bmin = value(input_dict, keymap['bmin'], default_term='0.0 angstrom',
                          default_unit=self.parent.units.length_unit)
        self.cmin = value(input_dict, keymap['cmin'], default_term='0.0 angstrom',
                          default_unit=self.parent.units.length_unit)

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        """str : The root element name for the subset terms."""
        baseroot = 'stacking-fault'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        disl = model[self.modelroot]

        self.__model = None
        self.__param_file = None
        self.key = disl['key']
        self.id = disl['id']
        self.family = disl['system-family']

        cp = disl['calculation-parameter']
        self.slip_hkl = cp['slip_hkl']
        self.ξ_uvw = cp['ξ_uvw']
        self.burgers = cp['burgers']
        self.m = cp['m']
        self.n = cp['n']
        if 'shift' in cp:
            self.shift = cp['shift']
        if 'shiftindex' in cp:
            self.shiftindex = cp['shiftindex']
        self.shiftscale = cp['shiftscale']

        run_params = model['calculation']['run-parameter']
        
        self.a_mults = run_params[f'{self.modelprefix}size-multipliers']['a']
        self.b_mults = run_params[f'{self.modelprefix}size-multipliers']['b']
        self.c_mults = run_params[f'{self.modelprefix}size-multipliers']['c']

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
        run_params[f'{self.modelprefix}size-multipliers']['a'] = list(self.a_mults)
        run_params[f'{self.modelprefix}size-multipliers']['b'] = list(self.b_mults)
        run_params[f'{self.modelprefix}size-multipliers']['c'] = list(self.c_mults)

    def mongoquery(self, dislocation_key=None, dislocation_id=None,
                   dislocation_family=None, a_mult1=None, a_mult2=None,
                   b_mult1=None, b_mult2=None, c_mult1=None, c_mult2=None,
                   **kwargs):
        """
        Generate a query to parse records with the subset from a Mongo-style
        database.
        
        Parameters
        ----------
        dislocation_id : str
            The id associated with a dislocation parameter set.
        dislocation_key : str
            The key associated with a dislocation parameter set.
        dislocation_family : str
            The "family" crystal structure/prototype that the dislocation
            is defined for.
        a_mult1 : int
            The lower size multiplier for the a box direction.
        a_mult2 : int
            The upper size multiplier for the a box direction.
        b_mult1 : int
            The lower size multiplier for the b box direction.
        b_mult2 : int
            The upper size multiplier for the b box direction.
        c_mult1 : int
            The lower size multiplier for the c box direction.
        c_mult2 : int
            The upper size multiplier for the c box direction.
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
        root = f'{parentroot}.{self.modelroot}'
        runparam_prefix = f'{parentroot}.calculation.run-parameter.{self.modelprefix}'

        # Build query terms
        query.str_match.mongo(mquery, f'{root}.dislocation.key', dislocation_key)
        query.str_match.mongo(mquery, f'{root}.dislocation.id', dislocation_id)
        query.str_match.mongo(mquery, f'{root}.system-family', dislocation_family)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.a.0', a_mult1)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.a.1', a_mult2)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.b.0', b_mult1)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.b.1', b_mult2)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.c.0', c_mult1)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.c.1', c_mult2)

        # Return query dict
        return mquery

    def cdcsquery(self, dislocation_key=None, dislocation_id=None,
                  dislocation_family=None, a_mult1=None, a_mult2=None,
                  b_mult1=None, b_mult2=None, c_mult1=None, c_mult2=None,
                  **kwargs):
        """
        Generate a query to parse records with the subset from a CDCS-style
        database.
        
        Parameters
        ----------
        dislocation_id : str
            The id associated with a dislocation parameter set.
        dislocation_key : str
            The key associated with a dislocation parameter set.
        dislocation_family : str
            The "family" crystal structure/prototype that the dislocation
            is defined for.
        a_mult1 : int
            The lower size multiplier for the a box direction.
        a_mult2 : int
            The upper size multiplier for the a box direction.
        b_mult1 : int
            The lower size multiplier for the b box direction.
        b_mult2 : int
            The upper size multiplier for the b box direction.
        c_mult1 : int
            The lower size multiplier for the c box direction.
        c_mult2 : int
            The upper size multiplier for the c box direction.
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
        root = f'{parentroot}.{self.modelroot}'
        runparam_prefix = f'{parentroot}.calculation.run-parameter.{self.modelprefix}'
        
        # Build query terms
        query.str_match.mongo(mquery, f'{root}.dislocation.key', dislocation_key)
        query.str_match.mongo(mquery, f'{root}.dislocation.id', dislocation_id)
        query.str_match.mongo(mquery, f'{root}.system-family', dislocation_family)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.a.0', a_mult1)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.a.1', a_mult2)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.b.0', b_mult1)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.b.1', b_mult2)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.c.0', c_mult1)
        query.int_match.mongo(mquery, f'{runparam_prefix}size-multipliers.c.1', c_mult2)

        # Return query dict
        return mquery      

########################## Metadata interactions ##############################

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
        meta[f'{prefix}a_mult1'] = self.a_mults[0]
        meta[f'{prefix}a_mult2'] = self.a_mults[1]
        meta[f'{prefix}b_mult1'] = self.b_mults[0]
        meta[f'{prefix}b_mult2'] = self.b_mults[1]
        meta[f'{prefix}c_mult1'] = self.c_mults[0]
        meta[f'{prefix}c_mult2'] = self.c_mults[1]

    def pandasfilter(self, dataframe, dislocation_key=None, dislocation_id=None,
                     dislocation_family=None, a_mult1=None, a_mult2=None,
                     b_mult1=None, b_mult2=None, c_mult1=None, c_mult2=None,
                     **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
        dislocation_id : str
            The id associated with a dislocation parameter set.
        dislocation_key : str
            The key associated with a dislocation parameter set.
        dislocation_family : str
            The "family" crystal structure/prototype that the dislocation
            is defined for.
        a_mult1 : int
            The lower size multiplier for the a box direction.
        a_mult2 : int
            The upper size multiplier for the a box direction.
        b_mult1 : int
            The lower size multiplier for the b box direction.
        b_mult2 : int
            The upper size multiplier for the b box direction.
        c_mult1 : int
            The lower size multiplier for the c box direction.
        c_mult2 : int
            The upper size multiplier for the c box direction.
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
            query.str_match.pandas(dataframe, f'{prefix}dislocation_key',
                                   dislocation_key)
            &query.str_match.pandas(dataframe, f'{prefix}dislocation_id',
                                    dislocation_id)
            &query.str_match.pandas(dataframe, f'{prefix}dislocation_family',
                                    dislocation_family)
            &query.int_match.pandas(dataframe, f'{prefix}a_mult1', a_mult1)
            &query.int_match.pandas(dataframe, f'{prefix}a_mult2', a_mult2)
            &query.int_match.pandas(dataframe, f'{prefix}b_mult1', b_mult1)
            &query.int_match.pandas(dataframe, f'{prefix}b_mult2', b_mult2)
            &query.int_match.pandas(dataframe, f'{prefix}c_mult1', c_mult1)
            &query.int_match.pandas(dataframe, f'{prefix}c_mult2', c_mult2) 
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
        input_dict['burgers'] = self.burgers
        input_dict['ξ_uvw'] = self.ξ_uvw
        input_dict['slip_hkl'] = self.slip_hkl
        input_dict['m'] = self.m
        input_dict['n'] = self.n
        a_mult = self.a_mults[1] - self.a_mults[0]
        b_mult = self.b_mults[1] - self.b_mults[0]
        c_mult = self.c_mults[1] - self.c_mults[0]
        input_dict['sizemults'] = [a_mult, b_mult, c_mult]
        input_dict['amin'] = self.amin
        input_dict['bmin'] = self.bmin
        input_dict['cmin'] = self.cmin
        input_dict['shift'] = self.shift
        input_dict['shiftscale'] = self.shiftscale
        input_dict['shiftindex'] = self.shiftindex
