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

class GrainBoundary(CalculationSubset):
    """Handles calculation terms for grain boundary parameters"""

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

        self.uvws1 = None
        self.uvws2 = None
        self.cellsetting = 'p'
        self.cutboxvector = 'c'
        self.minwidth = 0.0
        self.num_a1 = 8
        self.num_a2 = 8
        self.deletefrom = 'top'
        self.min_deleter = 0.30
        self.max_deleter = 0.99
        self.num_deleter = 100
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
    def uvws1(self) -> Optional[np.ndarray]:
        """numpy.ndarray or None: The crystallographic rotation vectors for grain 1"""
        return self.__uvws1

    @uvws1.setter
    def uvws1(self, val: Optional[npt.ArrayLike]):
        if val is None:
            self.__uvws1 = None
        else:
            val = np.asarray(val, dtype=float)
            assert val.shape == (3,3) or val.shape == (3,4)
            self.__uvws1 = val

    @property
    def uvws2(self) -> Optional[np.ndarray]:
        """numpy.ndarray or None: The crystallographic rotation vectors for grain 2"""
        return self.__uvws2

    @uvws2.setter
    def uvws2(self, val: Optional[npt.ArrayLike]):
        if val is None:
            self.__uvws2 = None
        else:
            val = np.asarray(val, dtype=float)
            assert val.shape == (3,3) or val.shape == (3,4)
            self.__uvws2 = val

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
        """str: The cell box vector that the boundary occurs along"""
        return self.__cutboxvector

    @cutboxvector.setter
    def cutboxvector(self, val: str):
        if val not in ['a', 'b', 'c']:
            raise ValueError('invalid cutboxvector')
        self.__cutboxvector = str(val)

    @property
    def minwidth(self) -> float:
        """float: The minimum width allowed perpendicular to the boundary"""
        return self.__minwidth

    @minwidth.setter
    def minwidth(self, val: float):
        self.__minwidth = float(val)

    @property
    def num_a1(self) -> int:
        """int: The number of in-plane shifts along the first in-plane vector to explore."""
        return self.__num_a1

    @num_a1.setter
    def num_a1(self, val: int):
        self.__num_a1 = int(val)

    @property
    def num_a2(self) -> int:
        """int: The number of in-plane shifts along the second in-plane vector to explore."""
        return self.__num_a2

    @num_a2.setter
    def num_a2(self, val: int):
        self.__num_a2 = int(val)

    @property
    def deletefrom(self) -> str:
        """str: Indicates which grain 'top', 'bottom', or 'both' close atoms will be deleted from"""
        return self.__deletefrom
    
    @deletefrom.setter
    def deletefrom(self, val: str):
        if val not in ['top', 'bottom', 'both']:
            raise ValueError('invalid deletefrom')
        self.__deletefrom = val
    
    @property
    def min_deleter(self) -> float:
        """float: The minimum interatomic spacing for atom deletion at the boundary"""
        return self.__min_deleter

    @min_deleter.setter
    def min_deleter(self, val: float):
        self.__min_deleter = float(val)

    @property
    def max_deleter(self) -> float:
        """float: The minimum interatomic spacing for atom deletion at the boundary"""
        return self.__max_deleter

    @max_deleter.setter
    def max_deleter(self, val: float):
        self.__max_deleter = float(val)

    @property
    def num_deleter(self) -> int:
        """int: The number of interatomic spacing thresholds for atom deletion at the boundary"""
        return self.__num_deleter

    @num_deleter.setter
    def num_deleter(self, val: int):
        self.__num_deleter = int(val)

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

    def set_uvws(self,
                 grain: int,
                 auvw: Union[str, npt.ArrayLike],
                 buvw: Union[str, npt.ArrayLike],
                 cuvw: Union[str, npt.ArrayLike]):
        """
        Utility function for setting either uvws1 or uvws2 from separate
        rotation vectors for each box direction.  uvws1 and uvws2 can
        alternatively be directly set with an array combining all three
        rotation vectors.
        
        Parameters
        ----------
        grain : int
            The grain number (1 or 2) that the values are being set for.
        auvw : str or array-like object
            The Miller(-Bravais) rotation vector for the grain's a box vector.
            Can be given as an array-like object or a space-delimited string.
        buvw : str or array-like object
            The Miller(-Bravais) rotation vector for the grain's b box vector.
            Can be given as an array-like object or a space-delimited string.
        cuvw : str or array-like object
            The Miller(-Bravais) rotation vector for the grain's c box vector.
            Can be given as an array-like object or a space-delimited string.
        """
        # Convert values to arrays as needed
        if isinstance(auvw, str):
            auvw = np.array(auvw.strip().split(), dtype=float)
        else:
            auvw = np.asarray(auvw, dtype=float)
        if isinstance(buvw, str):
            buvw = np.array(buvw.strip().split(), dtype=float)
        else:
            buvw = np.asarray(buvw, dtype=float)
        if isinstance(cuvw, str):
            cuvw = np.array(cuvw.strip().split(), dtype=float)
        else:
            cuvw = np.asarray(cuvw, dtype=float)

        uvws = np.array([auvw, buvw, cuvw])

        if grain == 1:
            self.uvws1 = uvws
        elif grain == 2:
            self.uvws2 = uvws
        else:
            raise ValueError('invalid grain number: should be 1 or 2')

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
        uvws1 : array-like object, optional
            The crystallographic rotation vectors for grain 1.  Cannot be
            given with auvw1, buvw1, or cuvw1.
        uvws2 : array-like object, optional
            The crystallographic rotation vectors for grain 2.  Cannot be
            given with auvw2, buvw2, or cuvw2.
        auvw1 : str or array-like object, optional
            The crystallographic rotation vector for grain 1's a box vector.
            auvw1, buvw1 and cuvw1 must be given together, and cannot be given
            with uvws1.
        buvw1 : str or array-like object, optional
            The crystallographic rotation vector for grain 1's b box vector.
            auvw1, buvw1 and cuvw1 must be given together, and cannot be given
            with uvws1.
        cuvw1 : str or array-like object, optional
            The crystallographic rotation vector for grain 1's c box vector.
            auvw1, buvw1 and cuvw1 must be given together, and cannot be given
            with uvws1.
        auvw2 : str or array-like object, optional
            The crystallographic rotation vector for grain 2's a box vector.
            auvw2, buvw2 and cuvw2 must be given together, and cannot be given
            with uvws2.
        buvw2 : str or array-like object, optional
            The crystallographic rotation vector for grain 2's b box vector.
            auvw2, buvw2 and cuvw2 must be given together, and cannot be given
            with uvws2.
        cuvw2 : str or array-like object, optional
            The crystallographic rotation vector for grain 2's c box vector.
            auvw2, buvw2 and cuvw2 must be given together, and cannot be given
            with uvws2.
        cellsetting : str, optional
            Indicates the setting of the unit cell, if it is not primitive.
            This allows for the proper identification of the shortest lattice
            vectors for applying the stacking fault shifts.
        cutboxvector : str, optional
            Indicates which box vector will be made non-periodic to allow for
            the defect to be created.
        minwidth : float, optional
            A minimum width for the box's cutboxvector direction.  The sizemults
            will be modified to ensure this as needed.
        num_a1 : int, optional
            The number of in-plane shifts along the first in-plane vector to
            explore.
        num_a2 : int, optional
            The number of in-plane shifts along the second in-plane vector to
            explore.
        deletefrom : str
            Indicates which grain 'top', 'bottom', or 'both' close atoms will
            be deleted from.
        min_deleter : float
            The minimum interatomic spacing for atom deletion at the boundary.
        max_deleter : float
            The minimum interatomic spacing for atom deletion at the boundary.
        num_deleter : int
            The number of interatomic spacing thresholds for atom deletion at
            the boundary.
        family : str or None, optional
            The system's family identifier that the defect is defined for.
        
        """
        if 'param_file' in kwargs:
            self.param_file = kwargs['param_file']
        if 'key' in kwargs:
            self.key = kwargs['key']
        
        if 'auvw1' in kwargs or 'buvw1' in kwargs or 'cuvw1' in kwargs:
            if 'uvws1' in kwargs:
                raise ValueError('uvws1 cannot be given with auvw1, buvw1, cuvw1')
            if 'auvw1' not in kwargs or 'buvw1' not in kwargs or 'cuvw1' not in kwargs:
                raise KeyError('All auvw1, buvw1, cuvw1 must be given if one is given')
            self.set_uvws(1, kwargs['auvw1'], kwargs['buvw1'], kwargs['cuvw1'])
        elif 'uvws1' in kwargs:
            self.uvws1 = kwargs['uvws1']
        
        if 'auvw2' in kwargs or 'buvw2' in kwargs or 'cuvw2' in kwargs:
            if 'uvws2' in kwargs:
                raise ValueError('uvws2 cannot be given with auvw2, buvw2, cuvw2')
            if 'auvw2' not in kwargs or 'buvw2' not in kwargs or 'cuvw2' not in kwargs:
                raise KeyError('All auvw2, buvw2, cuvw2 must be given if one is given')
            self.set_uvws(2, kwargs['auvw2'], kwargs['buvw2'], kwargs['cuvw2'])
        elif 'uvws2' in kwargs:
            self.uvws2 = kwargs['uvws2']

        if 'cellsetting' in kwargs:
            self.cellsetting = kwargs['cellsetting']
        if 'cutboxvector' in kwargs:
            self.cutboxvector = kwargs['cutboxvector']
        if 'minwidth' in kwargs:
            self.minwidth = kwargs['minwidth']
        if 'num_a1' in kwargs:
            self.num_a1 = kwargs['num_a1']
        if 'num_a2' in kwargs:
            self.num_a2 = kwargs['num_a2']
        if 'deletefrom' in kwargs:
            self.deletefrom = kwargs['deletefrom']
        if 'min_deleter' in kwargs:
            self.min_deleter = kwargs['min_deleter']
        if 'max_deleter' in kwargs:
            self.max_deleter = kwargs['max_deleter']
        if 'num_deleter' in kwargs:
            self.num_deleter = kwargs['num_deleter']
        if 'family' in kwargs:
            self.family = kwargs['family']
        

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
            templateheader = 'Grain Boundary'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the parameter set that defines a grain boundary."])

        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self) -> dict:
        """dict : The subset-specific input keys and their descriptions."""
        return {
            'grainboundary_file': ' '.join([
                "The path to a grain_boundary record file that collects the",
                "parameters associated with a specific grain boundary."]),
            'grainboundary_auvw1': ' '.join([
                "The Miller [uvw] vector to align with the a box vector of"
                "grain 1. Given as 3 (or 4) space-delimited floats."]),
            'grainboundary_buvw1': ' '.join([
                "The Miller [uvw] vector to align with the b box vector of"
                "grain 1. Given as 3 (or 4) space-delimited floats."]),
            'grainboundary_cuvw1': ' '.join([
                "The Miller [uvw] vector to align with the c box vector of"
                "grain 1. Given as 3 (or 4) space-delimited floats."]),
            'grainboundary_auvw2': ' '.join([
                "The Miller [uvw] vector to align with the a box vector of"
                "grain 2. Given as 3 (or 4) space-delimited floats."]),
            'grainboundary_buvw2': ' '.join([
                "The Miller [uvw] vector to align with the b box vector of"
                "grain 2. Given as 3 (or 4) space-delimited floats."]),
            'grainboundary_cuvw2': ' '.join([
                "The Miller [uvw] vector to align with the c box vector of"
                "grain 2. Given as 3 (or 4) space-delimited floats."]),
            'grainboundary_cellsetting': ' '.join([
                "The conventional cell setting to take the uvw values relative to",
                "if the loaded unit cell is a primitive cell.  Allowed values are 'p',",
                "'c', 'i', 'a', 'b' and 'c'."]),
            'grainboundary_cutboxvector': ' '.join([
                "Indicates which of the three box vectors ('a', 'b', or 'c')",
                "that the grain boundary planes will be made along.",
                "Default value is 'c'."]),
            'grainboundary_minwidth': ' '.join([
                "Specifies a mimimum width in length units that the system must be",
                "along the cutboxvector direction. The associated sizemult value",
                "will be increased if necessary to ensure this. Default value is 0.0."]),
            'grainboundary_num_a1': ' '.join([
                "The number of boundary grid shifts to explore along the first",
                "identified in-plane vector.  Default value is 8."]),
            'grainboundary_num_a2': ' '.join([
                "The number of boundary grid shifts to explore along the second",
                "identified in-plane vector.  Default value is 8."]),
            'grainboundary_deletefrom': ' '.join([
                "Indicates which grain ('top', 'bottom' or 'both') that atoms",
                "close to each other across the boundary will be deleted from.",
                "Default value is 'top'."]),
            'grainboundary_min_deleter': ' '.join([
                "The smallest interatomic spacing (relative to the unit cell's r0)",
                "to include in the iterative deletion search of atoms close to",
                "each other across the boundary.  Default value is 0.3"]),
            'grainboundary_max_deleter': ' '.join([
                "The largest interatomic spacing (relative to the unit cell's r0)",
                "to include in the iterative deletion search of atoms close to",
                "each other across the boundary.  Default value is 0.99"]),
            'grainboundary_num_deleter': ' '.join([
                "The number of interatomic spacings ranging from min_deleter",
                "to max_deleter that are to be used for the boundary atom deletion",
                "threshold.  Note that only unique configurations will be minimized",
                "so this is the max number of configurations that can be explored",
                "for each a1,a2 shift set.  Default value is 100"]),
        }

    @property
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return list(self.templatekeys.keys()) + [
            'grainboundary_family',
            'grainboundary_content',
        ]

    @property
    def interpretkeys(self) -> list:
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return self.preparekeys + [
            'grainboundary_model',
        ]

    @property
    def multikeys(self) -> list:
        """
        list: Calculation subset key sets that can have multiple values during prepare.
        """
        # Define key set for system size parameters
        sizekeys = ['grainboundary_num_a1',
                    'grainboundary_num_a2',
                    'grainboundary_deletefrom',
                    'grainboundary_min_deleter',
                    'grainboundary_max_deleter',
                    'grainboundary_num_deleter']

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
        self.param_file = input_dict.get(keymap['grainboundary_file'], None)
        self.__content = input_dict.get(keymap['grainboundary_content'], None)

        # Replace defect model with defect content if given
        param_file = self.param_file
        if self.__content is not None:
            param_file = self.__content

        # Extract parameters from a file
        if param_file is not None:

            # Verify competing parameters are not defined
            for key in ('grainboundary_auvw1',
                        'grainboundary_buvw1',
                        'grainboundary_cuvw1',
                        'grainboundary_auvw1',
                        'grainboundary_buvw1',
                        'grainboundary_cuvw1',
                        'grainboundary_cellsetting',
                        'grainboundary_cutboxvector'):
                if keymap[key] in input_dict:
                    raise ValueError(f"{keymap[key]} and {keymap['grainboundary_file']} cannot both be supplied")

            # Load defect model
            self.__model = model = DM(param_file).find('grain-boundary')

            # Extract parameter values from defect model
            self.key = model['key']
            self.id = model['id']
            self.family = model['system-family']
            self.set_uvws(1, 
                          model['calculation-parameter']['auvw1'], 
                          model['calculation-parameter']['buvw1'], 
                          model['calculation-parameter']['cuvw1'])
            self.set_uvws(2, 
                          model['calculation-parameter']['auvw2'], 
                          model['calculation-parameter']['buvw2'], 
                          model['calculation-parameter']['cuvw2'])
            self.cutboxvector = model['calculation-parameter']['cutboxvector']
            self.cellsetting = model['calculation-parameter'].get('cellsetting', 'p')

        # Set parameter values directly
        else:
            self.__model = None
            self.key = None
            self.id = None
            self.family = self.parent.system.family
            self.set_uvws(1,
                          input_dict[keymap['grainboundary_auvw1']],
                          input_dict[keymap['grainboundary_buvw1']],
                          input_dict[keymap['grainboundary_cuvw1']])
            self.set_uvws(2,
                          input_dict[keymap['grainboundary_auvw2']],
                          input_dict[keymap['grainboundary_buvw2']],
                          input_dict[keymap['grainboundary_cuvw2']])
            self.cutboxvector = input_dict.get(keymap['grainboundary_cutboxvector'], 'c')
            self.cellsetting = input_dict.get(keymap['grainboundary_cellsetting'], 'p')

        # Set default values for fault system manipulations
        self.minwidth = float(input_dict.get(keymap['grainboundary_minwidth'], 0.0))
        self.num_a1 = int(input_dict.get(keymap['grainboundary_num_a1'], 8))
        self.num_a2 = int(input_dict.get(keymap['grainboundary_num_a2'], 8))
        self.deletefrom = input_dict.get(keymap['grainboundary_deletefrom'], 'top')
        self.min_deleter = float(input_dict.get(keymap['grainboundary_min_deleter'], 0.30))
        self.max_deleter = float(input_dict.get(keymap['grainboundary_max_deleter'], 0.99))
        self.num_deleter = int(input_dict.get(keymap['grainboundary_num_deleter'], 100))

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str : The root element name for the subset terms."""
        baseroot = 'grain-boundary'
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
        self.set_uvws(1, cp['auvw1'], cp['buvw1'], cp['cuvw1'])
        self.set_uvws(2, cp['auvw2'], cp['buvw2'], cp['cuvw2'])
        self.cutboxvector = cp['cutboxvector']
        self.cellsetting = cp['cellsetting'] 

        run_params = model['calculation']['run-parameter']

        self.minwidth = uc.value_unit(run_params[f'{self.modelprefix}minimum-width'])
        self.num_a1 = run_params['grainboundary_num_a1']
        self.num_a2 = run_params['grainboundary_num_a2']
        self.deletefrom = run_params['grainboundary_deletefrom']
        self.min_deleter = run_params['grainboundary_min_deleter']
        self.max_deleter = run_params['grainboundary_max_deleter']
        self.num_deleter = run_params['grainboundary_num_deleter']


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
        model[self.modelroot] = gb = DM()
        gb['key'] = self.key
        gb['id'] = self.id
        gb['system-family'] = self.family
        gb['calculation-parameter'] = cp = DM()
        
        cp['auvw1'] = ' '.join([f'{v}' for v in self.uvws1[0]])
        cp['buvw1'] = ' '.join([f'{v}' for v in self.uvws1[1]])
        cp['cuvw1'] = ' '.join([f'{v}' for v in self.uvws1[2]])
        cp['auvw2'] = ' '.join([f'{v}' for v in self.uvws2[0]])
        cp['buvw2'] = ' '.join([f'{v}' for v in self.uvws2[1]])
        cp['cuvw2'] = ' '.join([f'{v}' for v in self.uvws2[2]])
        cp['cutboxvector'] = self.cutboxvector
        cp['cellsetting'] = self.cellsetting

        # Build paths if needed
        if 'calculation' not in model:
            model['calculation'] = DM()
        if 'run-parameter' not in model['calculation']:
            model['calculation']['run-parameter'] = DM()

        run_params = model['calculation']['run-parameter']

        run_params[f'{self.modelprefix}minimum-width'] = uc.model(self.minwidth,
                                                             self.parent.units.length_unit)
        run_params['grainboundary_num_a1'] = self.num_a1
        run_params['grainboundary_num_a2'] = self.num_a2
        run_params['grainboundary_deletefrom'] = self.deletefrom
        run_params['grainboundary_min_deleter'] = self.min_deleter
        run_params['grainboundary_max_deleter'] = self.max_deleter
        run_params['grainboundary_num_deleter'] = self.num_deleter

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""

        root = f'{self.parent.modelroot}.{self.modelroot}'
        runparampath = f'{self.parent.modelroot}.calculation.run-parameter.{self.modelprefix}'

        return {
            'grainboundary_id': load_query(
                style='str_match',
                name=f'{self.prefix}grainboundary_id',
                path=f'{root}.id',
                description='search by grain boundary parameter set id'),
            'grainboundary_key': load_query(
                style='str_match',
                name=f'{self.prefix}grainboundary_key',
                path=f'{root}.key',
                description='search by grain boundary parameter set UUID key'),
            'grainboundary_family': load_query(
                style='str_match',
                name=f'{self.prefix}grainboundary_family',
                path=f'{root}.system-family',
                description='search by crystal prototype that the grain boundary parameter set is for'),
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

        meta[f'{prefix}grainboundary_key'] = self.key
        meta[f'{prefix}grainboundary_id'] = self.id
        meta[f'{prefix}grainboundary_family'] = self.family
        meta[f'{prefix}grainboundary_uvws1'] = self.uvws1
        meta[f'{prefix}grainboundary_uvws2'] = self.uvws2

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
        if self.uvws1 is None:
            raise ValueError('uvws1 not set')
        if self.uvws2 is None:
            raise ValueError('uvws2 not set')

        input_dict['uvws1'] = self.uvws1
        input_dict['uvws2'] = self.uvws2

        #input_dict['conventional_setting'] = self.cellsetting
        input_dict['minwidth'] = self.minwidth
        input_dict['num_a1'] = self.num_a1
        input_dict['num_a2'] = self.num_a2
        input_dict['deletefrom'] = self.deletefrom
        input_dict['min_deleter'] = self.min_deleter
        input_dict['max_deleter'] = self.max_deleter
        input_dict['num_deleter'] = self.num_deleter
        input_dict['cutboxvector'] = self.cutboxvector
