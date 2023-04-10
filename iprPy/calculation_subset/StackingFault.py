# coding: utf-8

# Standard Python libraries
from pathlib import Path
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from yabadaba import load_query

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

from . import CalculationSubset
from ..input import boolean

class StackingFault(CalculationSubset):
    """Handles calculation terms for stacking fault parameters"""

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

        self.param_file = None
        self.key = None
        self.id = None
        self.hkl = None
        self.a1vect_uvw = None
        self.a2vect_uvw = None
        self.cellsetting = 'p'
        self.cutboxvector = 'c'
        self.shiftindex = 0
        self.faultpos_rel = 0.5
        self.sizemults = [1,1,1]
        self.minwidth = 0.0
        self.even = False
        self.family = None
        self.__content = None
        self.__model = None

############################## Class attributes ################################

    @property
    def param_file(self) -> Optional[Path]:
        """Path or None: The path to the stacking fault parameter file"""
        return self.__param_file

    @param_file.setter
    def param_file(self, val: Union[str, Path, None]):
        if val is None:
            self.__param_file = None
        else:
            self.__param_file = Path(val)

    @property
    def key(self) -> Optional[str]:
        """str or None: UUID key of the stacking fault parameter set"""
        return self.__key

    @key.setter
    def key(self, val: Optional[str]):
        if val is None:
            self.__key = None
        else:
            self.__key = str(val)

    @property
    def id(self) -> Optional[str]:
        """str or None: id of the stacking fault parameter set"""
        return self.__id

    @id.setter
    def id(self, val: Optional[str]):
        if val is None:
            self.__id = None
        else:
            self.__id = str(val)

    @property
    def hkl(self) -> Optional[np.ndarray]:
        """numpy.ndarray or None: The crystallographic (hkl) or (hkil) cut plane"""
        return self.__hkl

    @hkl.setter
    def hkl(self, val: Optional[npt.ArrayLike]):
        if val is None:
            self.__hkl = None
        else:
            if isinstance(val, str):
                val = np.array(val.strip().split(), dtype=float)
            else:
                val = np.asarray(val, dtype=float)
            assert val.shape == (3,) or val.shape == (4,)
            self.__hkl = val.tolist()

    @property
    def a1vect_uvw(self) -> Optional[np.ndarray]:
        """numpy.ndarray or None: The crystallographic [uvw] or [uvtw] a1 fault shift vector"""
        return self.__a1vect_uvw

    @a1vect_uvw.setter
    def a1vect_uvw(self, val: Optional[npt.ArrayLike]):
        if val is None:
            self.__a1vect_uvw = None
        else:
            if isinstance(val, str):
                val = np.array(val.strip().split(), dtype=float)
            else:
                val = np.asarray(val, dtype=float)
            assert val.shape == (3,) or val.shape == (4,)
            self.__a1vect_uvw = val.tolist()

    @property
    def a2vect_uvw(self) -> Optional[np.ndarray]:
        """numpy.ndarray or None: The crystallographic [uvw] or [uvtw] a1 fault shift vector"""
        return self.__a2vect_uvw

    @a2vect_uvw.setter
    def a2vect_uvw(self, val: Optional[npt.ArrayLike]):
        if val is None:
            self.__a2vect_uvw = None
        else:
            if isinstance(val, str):
                val = np.array(val.strip().split(), dtype=float)
            else:
                val = np.asarray(val, dtype=float)
            assert val.shape == (3,) or val.shape == (4,)
            self.__a2vect_uvw = val.tolist()

    @property
    def cellsetting(self) -> str:
        """str: The reference unit cell setting"""
        return self.__cellsetting

    @cellsetting.setter
    def cellsetting(self, val: str):
        if val not in ['p', 'a', 'b', 'c', 'i', 'f']:
            raise ValueError('invalid surface cellsetting')
        self.__cellsetting = str(val)

    @property
    def cutboxvector(self) -> str:
        """str: The cell box vector that the cut occurs along"""
        return self.__cutboxvector

    @cutboxvector.setter
    def cutboxvector(self, val: str):
        if val not in ['a', 'b', 'c']:
            raise ValueError('invalid surface cutboxvector')
        self.__cutboxvector = str(val)

    @property
    def shiftindex(self) -> int:
        """int: The index of the pre-determined shifts values to use for shift"""
        return self.__shiftindex

    @shiftindex.setter
    def shiftindex(self, val: int):
        self.__shiftindex = int(val)

    @property
    def sizemults(self) -> list:
        """list: The three size multipliers of rcell used"""
        return self.__sizemults

    @sizemults.setter
    def sizemults(self, val: Union[str, list, tuple]):
        if isinstance(val, str):
            val = np.array(val.strip().split(), dtype=int)
        else:
            val = np.asarray(val, dtype=int)
        if val.shape != (3,):
            raise ValueError('Invalid sizemults command: exactly 3 sizemults required for this calculation')
        self.__sizemults = val.tolist()

    @property
    def minwidth(self) -> float:
        """float: The minimum width allowed perpendicular to the cut"""
        return self.__minwidth

    @minwidth.setter
    def minwidth(self, val: float):
        self.__minwidth = float(val)

    @property
    def faultpos_rel(self) -> float:
        """float: The relative position along the cutboxvector where the fault plane is located"""
        return self.__faultpos_rel

    @faultpos_rel.setter
    def faultpos_rel(self, val: float):
        self.__faultpos_rel = float(val)

    @property
    def even(self) -> bool:
        """bool: If True, the number of replicas along the cutboxvector will be kept even"""
        return self.__even

    @even.setter
    def even(self, val: bool):
        self.__even = boolean(val)

    @property
    def family(self) -> Optional[str]:
        """str or None: The prototype or reference crystal the stacking fault parameter set is for"""
        return self.__family

    @family.setter
    def family(self, val: Optional[str]):
        if val is None:
            self.__family = None
        else:
            self.__family = str(val)

    def set_values(self, **kwargs: any):
        """
        Allows for multiple class attribute values to be updated at once.

        Parameters
        ----------
        param_file : str, optional
            The path to a file that fully defines the input parameters for
            a specific defect type
        key : str, optional
            The UUID4 unique key associated with the defect parameter set.
        id : str, optional
            The unique id associated with the defect parameter set.
        hkl : str or array-like object, optional
            The Miller (hkl) fault plane.
        cellsetting : str, optional
            Indicates the setting of the unit cell, if it is not primitive.
            This allows for the proper identification of the shortest lattice
            vectors for applying the stacking fault shifts.
        cutboxvector : str, optional
            Indicates which box vector will be made non-periodic to allow for
            the defect to be created.
        shiftindex : int, optional
            A rigid shift will be applied to position the cutboxvector's
            boundary halfway between two atomic planes.  Changing this value
            changes the termination planes.
        sizemults : str or array-like object, optional
            The system size multipliers.  
        minwidth : float, optional
            A minimum width for the box's cutboxvector direction.  The sizemults
            will be modified to ensure this as needed.
        even : bool, optional
            If True, the sizemult for the cutboxvector direction will be
            constrained to be even.  This will ensure that the free surfaces
            and fault plane surface will have identical neighboring atomic
            planes.
        family : str or None, optional
            The system's family identifier that the defect is defined for.
        a1vect_uvw : str or array-like object, optional
            The in-plane a1 shift vector that indicates a full shift from one
            lattice site to another.
        a2vect_uvw : str or array-like object, optional
            The in-plane a2 shift vector that indicates a full shift from one
            lattice site to another.
        faultpos_rel : float, optional
            The relative position along the cutboxvector where the fault plane
            is to be located.  Default value is 0.5 (middle).
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
        if 'a1vect_uvw' in kwargs:
            self.a1vect_uvw = kwargs['a1vect_uvw']
        if 'a2vect_uvw' in kwargs:
            self.a2vect_uvw = kwargs['a2vect_uvw']
        if 'faultpos_rel' in kwargs:
            self.faultpos_rel = kwargs['faultpos_rel']

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
            templateheader = 'Stacking Fault'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the parameter set that defines a stacking fault."])

        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self) -> dict:
        """dict : The subset-specific input keys and their descriptions."""
        return {
            'stackingfault_file': ' '.join([
                "The path to a stacking_fault record file that collects the",
                "parameters associated with a specific stacking fault."]),
            'stackingfault_hkl': ' '.join([
                "The Miller (hkl) plane for the fault plane given as three",
                "space-delimited integers."]),
            'stackingfault_a1vect_uvw': ' '.join([
                "The Miller [uvw] vector to use for the a1 shift vector",
                "given as three space-delimited floats."]),
            'stackingfault_a2vect_uvw': ' '.join([
                "The Miller [uvw] vector to use for the a2 shift vector",
                "given as three space-delimited floats."]),
            'stackingfault_cellsetting': ' '.join([
                "The conventional cell setting to take stackingfault_hkl relative to",
                "if the loaded unit cell is a primitive cell.  Allowed values are 'p',",
                "'c', 'i', 'a', 'b' and 'c'."]),
            'stackingfault_cutboxvector': ' '.join([
                "Indicates which of the three box vectors ('a', 'b', or 'c')",
                "that the surface and fault planes will be made along.",
                "Default value is 'c'."]),
            'stackingfault_shiftindex': ' '.join([
                "A rigid body shift will be applied to the atoms such that the",
                "created surface plane will be halfway between two atomic planes.",
                "This is an integer value that changes which set of atomic planes",
                "that the plane is inserted between.  Changing this effectively",
                "changes the termination planes."]),
            'stackingfault_faultpos_rel': ' '.join([
                "A fractional coordinate from 0 to 1 indicating where along the",
                "cutboxvector to position the fault plane. Default value is 0.5,",
                "which if stackingfault_even is True will result in the same",
                "termination planes at the free surface and the stacking fault."]),
            'sizemults': ' '.join([
                "Multiplication parameters to construct a supercell from the rotated",
                "system.  Limited to three values for stacking fault generation."]),
            'stackingfault_minwidth': ' '.join([
                "Specifies a mimimum width in length units that the system must be",
                "along the cutboxvector direction. The associated sizemult value",
                "will be increased if necessary to ensure this. Default value is 0.0."]),
            'stackingfault_even': ' '.join([
                "If True, the number of replicas in the cutboxvector direction will"
                "be even. Default value is False."]),
        }

    @property
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return list(self.templatekeys.keys()) + [
            'stackingfault_family',
            'stackingfault_content',
        ]

    @property
    def interpretkeys(self) -> list:
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return self.preparekeys + [
            'stackingfault_model',
        ]

    @property
    def multikeys(self) -> list:
        """
        list: Calculation subset key sets that can have multiple values during prepare.
        """
        # Define key set for system size parameters
        sizekeys = ['sizemults', 'stackingfault_minwidth', 'stackingfault_even']

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
        self.param_file = input_dict.get(keymap['stackingfault_file'], None)
        self.__content = input_dict.get(keymap['stackingfault_content'], None)

        # Replace defect model with defect content if given
        param_file = self.param_file
        if self.__content is not None:
            param_file = self.__content

        # Extract parameters from a file
        if param_file is not None:

            # Verify competing parameters are not defined
            for key in ('stackingfault_hkl',
                        'stackingfault_shiftindex',
                        'stackingfault_a1vect_uvw',
                        'stackingfault_a2vect_uvw',
                        'stackingfault_cellsetting',
                        'stackingfault_cutboxvector',
                        'stackingfault_faultpos_rel'):
                if keymap[key] in input_dict:
                    raise ValueError(f"{keymap[key]} and {keymap['stackingfault_file']} cannot both be supplied")

            # Load defect model
            self.__model = model = DM(param_file).find('stacking-fault')

            # Extract parameter values from defect model
            self.key = model['key']
            self.id = model['id']
            self.family = model['system-family']
            self.hkl = model['calculation-parameter']['hkl']
            self.a1vect_uvw = model['calculation-parameter']['a1vect_uvw']
            self.a2vect_uvw = model['calculation-parameter']['a2vect_uvw']
            self.shiftindex = int(model['calculation-parameter'].get('shiftindex', 0))
            self.cutboxvector = model['calculation-parameter']['cutboxvector']
            self.faultpos_rel = float(model['calculation-parameter'].get('faultpos_rel', 0.5))
            self.cellsetting = model['calculation-parameter'].get('cellsetting', 'p')

        # Set parameter values directly
        else:
            self.__model = None
            self.key = None
            self.id = None
            self.family = self.parent.system.family
            self.hkl = input_dict[keymap['stackingfault_hkl']]
            self.a1vect_uvw = input_dict.get(keymap['stackingfault_a1vect_uvw'], None)
            self.a2vect_uvw = input_dict.get(keymap['stackingfault_a2vect_uvw'], None)
            self.shiftindex = int(input_dict.get(keymap['stackingfault_shiftindex'], 0))
            self.cutboxvector = input_dict.get(keymap['stackingfault_cutboxvector'], 'c')
            self.faultpos_rel = float(input_dict.get(keymap['stackingfault_faultpos_rel'], 0.5))
            self.cellsetting = input_dict.get(keymap['stackingfault_cellsetting'], 'p')

        # Set default values for fault system manipulations
        self.sizemults = input_dict.get(keymap['sizemults'], '1 1 1')
        self.minwidth = float(input_dict.get(keymap['stackingfault_minwidth'], 0.0))
        self.even = boolean(input_dict.get(keymap['stackingfault_even'], False))

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str : The root element name for the subset terms."""
        baseroot = 'stacking-fault'
        return f'{self.modelprefix}{baseroot}'

    def load_model(self, model: DM):
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
        if len(self.a1vect_uvw) == 3:
            cp['a1vect_uvw'] = f'{self.a1vect_uvw[0]} {self.a1vect_uvw[1]} {self.a1vect_uvw[2]}'
        else:
            cp['a1vect_uvw'] = f'{self.a1vect_uvw[0]} {self.a1vect_uvw[1]} {self.a1vect_uvw[2]} {self.a1vect_uvw[3]}'
        if len(self.a2vect_uvw) == 3:
            cp['a2vect_uvw'] = f'{self.a2vect_uvw[0]} {self.a2vect_uvw[1]} {self.a2vect_uvw[2]}'
        else:
            cp['a2vect_uvw'] = f'{self.a2vect_uvw[0]} {self.a2vect_uvw[1]} {self.a2vect_uvw[2]} {self.a2vect_uvw[3]}'
        cp['cutboxvector'] = self.cutboxvector
        cp['faultpos_rel'] = str(self.faultpos_rel)
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

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""

        root = f'{self.parent.modelroot}.{self.modelroot}'
        runparampath = f'{self.parent.modelroot}.calculation.run-parameter.{self.modelprefix}'

        return {
            'stackingfault_id': load_query(
                style='str_match',
                name=f'{self.prefix}stackingfault_id',
                path=f'{root}.id',
                description='search by stacking fault parameter set id'),
            'stackingfault_key': load_query(
                style='str_match',
                name=f'{self.prefix}stackingfault_key',
                path=f'{root}.key',
                description='search by stacking fault parameter set UUID key'),
            'stackingfault_family': load_query(
                style='str_match',
                name=f'{self.prefix}dislocation_family',
                path=f'{root}.system-family',
                description='search by crystal prototype that the stacking fault parameter set is for'),
            'a_mult1': load_query(
                style='int_match',
                name=f'{self.prefix}a_mult1',
                path=f'{runparampath}size-multipliers.a.0',
                description='search by lower a_mult value'),
            'a_mult2': load_query(
                style='int_match',
                name=f'{self.prefix}a_mult2',
                path=f'{runparampath}size-multipliers.a.1',
                description='search by upper a_mult value'),
            'b_mult1': load_query(
                style='int_match',
                name=f'{self.prefix}b_mult1',
                path=f'{runparampath}size-multipliers.b.0',
                description='search by lower b_mult value'),
            'b_mult2': load_query(
                style='int_match',
                name=f'{self.prefix}b_mult2',
                path=f'{runparampath}size-multipliers.b.1',
                description='search by upper b_mult value'),
            'c_mult1': load_query(
                style='int_match',
                name=f'{self.prefix}c_mult1',
                path=f'{runparampath}size-multipliers.c.0',
                description='search by lower c_mult value'),
            'c_mult2': load_query(
                style='int_match',
                name=f'{self.prefix}c_mult2',
                path=f'{runparampath}size-multipliers.c.1',
                description='search by upper c_mult value'),
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
        prefix = self.prefix

        meta[f'{prefix}stackingfault_key'] = self.key
        meta[f'{prefix}stackingfault_id'] = self.id
        meta[f'{prefix}stackingfault_family'] = self.family
        meta[f'{prefix}stackingfault_hkl'] = self.hkl
        meta[f'{prefix}stackingfault_shiftindex'] = self.shiftindex
        meta[f'{prefix}stackingfault_a1vect_uvw'] = self.a1vect_uvw
        meta[f'{prefix}stackingfault_a2vect_uvw'] = self.a2vect_uvw
        meta[f'{prefix}a_mult1'] = 0
        meta[f'{prefix}a_mult2'] = self.sizemults[0]
        meta[f'{prefix}b_mult1'] = 0
        meta[f'{prefix}b_mult2'] = self.sizemults[1]
        meta[f'{prefix}c_mult1'] = 0
        meta[f'{prefix}c_mult2'] = self.sizemults[2]

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
        if self.hkl is None:
            raise ValueError('hkl not set')

        input_dict['hkl'] = self.hkl

        input_dict['sizemults'] = self.sizemults
        input_dict['minwidth'] = self.minwidth
        input_dict['even'] = self.even
        input_dict['a1vect_uvw'] = self.a1vect_uvw
        input_dict['a2vect_uvw'] = self.a2vect_uvw
        input_dict['conventional_setting'] = self.cellsetting
        input_dict['cutboxvector'] = self.cutboxvector
        input_dict['faultpos_rel'] = self.faultpos_rel
        input_dict['shiftindex'] = self.shiftindex
