# coding: utf-8

# Standard Python libraries
from typing import Optional, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

# Local imports
from . import CalculationSubset
from ..input import value

class LammpsNEB(CalculationSubset):
    """Handles calculation terms for performing a LAMMPS NEB calculation"""

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

        self.numreplicas = 11
        self.partition = None
        self.springconst = uc.set_in_units(5.0, 'eV/angstrom^2') 
        self.energytolerance = 0.0
        self.forcetolerance = 0.0
        self.minsteps = 10000
        self.climbsteps = 10000
        self.timestep = uc.set_in_units(0.01, 'ps')
        self.maxatommotion = uc.set_in_units(0.01, 'angstrom') 

############################## Class attributes ################################

    @property
    def numreplicas(self) -> int:
        """int: The number of NEB replicas"""
        return self.__numreplicas

    @numreplicas.setter
    def numreplicas(self, val: int):
        self.__numreplicas = int(val)

    @property
    def partition(self) -> Optional[str]:
        """str or None: The LAMMPS partition option to use"""
        return self.__partition

    @partition.setter
    def partition(self, val: Optional[str]):
        if val is not None:
            self.__partition = str(val)
        else:
            self.__partition = None

    @property
    def springconst(self) -> float:
        """float: The NEB force spring constant"""
        return self.__springconst
    
    @springconst.setter
    def springconst(self, val: Union[str, float]):
        if isinstance(val, str):
            self.__springconst = uc.set_literal(val)
        else:
            self.__springconst = float(val)

    @property
    def energytolerance(self) -> float:
        """float: The energy tolerance to use for NEB"""
        return self.__energytolerance

    @energytolerance.setter
    def energytolerance(self, val: float):
        self.__energytolerance = float(val)

    @property
    def forcetolerance(self) -> float:
        """float: The force tolerance to use for NEB"""
        return self.__forcetolerance

    @forcetolerance.setter
    def forcetolerance(self, val: Union[str, float]):
        if isinstance(val, str):
            self.__forcetolerance = uc.set_literal(val)
        else:
            self.__forcetolerance = float(val)

    @property
    def minsteps(self) -> int:
        """int: Max number of NEB minimization steps"""
        return self.__minsteps

    @minsteps.setter
    def minsteps(self, val: int):
        val = int(val)
        assert val >= 0, 'minsteps must be >= 0'
        self.__minsteps = val

    @property
    def climbsteps(self) -> int:
        """int: Max number of NEB climbing steps"""
        return self.__climbsteps

    @climbsteps.setter
    def climbsteps(self, val: int):
        val = int(val)
        assert val >= 0, 'climbsteps must be >= 0'
        self.__climbsteps = val

    @property
    def timestep(self) -> float:
        """float: The timestep to use with the quickmin minimization"""
        return self.__timestep

    @timestep.setter
    def timestep(self, val: Union[str, float]):
        if isinstance(val, str):
            self.__timestep = uc.set_literal(val)
        else:
            self.__timestep = float(val)

    @property
    def maxatommotion(self) -> float:
        """float: The max distance for atomic relaxations each iteration"""
        return self.__maxatommotion

    @maxatommotion.setter
    def maxatommotion(self, val: Union[str, float]):
        if isinstance(val, str):
            self.__maxatommotion = uc.set_literal(val)
        else:
            self.__maxatommotion = float(val)

    def set_values(self, **kwargs: any):
        """
        Allows for multiple class attribute values to be updated at once.

        Parameters
        ----------
        numreplicas : int, optional
            The number of NEB replicas.
        partition : str or None, optional
            The LAMMPS partition command line option value.  If set, should
            be of the form 'MxN' where M=numreplicas and N is the number of
            cores per replica to use.
        springconst : float or str, optional
            The NEB force spring constant.   Can be given as
            a str that specifies force/length units.
        energytolerance : float, optional
            The energy tolerance to use for NEB.
        forcetolerance : float or str, optional
            The force tolerance to use for NEB.  Can be given as
            a str that specifies force units.
        minsteps : int, optional
            The maximum number of NEB minimization steps to use.
        climbsteps : int, optional
            The maximum number of NEB climbing steps to use.
        timestep : float or str, optional
            The timestep to use with the quickmin minimization.  Can be given
            as a str that specifies time units.
        maxatommotion : float or str, optional
            The maximum atomic relaxation distance to allow for each iteration.
            Can be given as a str that specifies length units.
        """
        if 'numreplicas' in kwargs:
            self.numreplicas = kwargs['numreplicas']
        if 'partition' in kwargs:
            self.partition = kwargs['partition']
        if 'springconst' in kwargs:
            self.springconst = kwargs['springconst']
        if 'energytolerance' in kwargs:
            self.energytolerance = kwargs['energytolerance']
        if 'forcetolerance' in kwargs:
            self.forcetolerance = kwargs['forcetolerance']
        if 'minsteps' in kwargs:
            self.minsteps = kwargs['minsteps']
        if 'climbsteps' in kwargs:
            self.climbsteps = kwargs['climbsteps']
        if 'timestep' in kwargs:
            self.timestep = kwargs['timestep']
        if 'maxatommotion' in kwargs:
            self.maxatommotion = kwargs['maxatommotion']

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
            templateheader = 'LAMMPS NEB'

        # Set default template description
        if templatedescription is None:
            templatedescription = ' '.join([
                "Specifies the parameters and options associated with performing",
                "nudged elastic band (NEB) in LAMMPS."])

        super()._template_init(templateheader, templatedescription)

    @property
    def templatekeys(self) -> dict:
        """dict : The subset-specific input keys and their descriptions."""
        return  {
            'numreplicas': ' '.join([
                "The number of NEB replicas to use.  Default value is 11."]),
            'springconst': ' '.join([
                "The NEB force spring constant.  This value is in force per",
                "length units.  Default value is '5.0 eV/angstrom^2'"]),
            'energytolerance': ' '.join([
                "The energy tolerance to use for NEB. This value is",
                "unitless and corresponds to the etol term for the LAMMPS",
                "neb command. Default value is 0.0."]),
            'forcetolerance': ' '.join([
                "The force tolerance to use for NEB. This value is",
                "in force units and corresponds to the ftol term for the LAMMPS",
                "neb command. Default value is '0.0 eV/angstrom'."]),
            'minsteps': ' '.join([
                "The maximum number of NEB minimization steps to perform.",
                "This value corresponds to the N! term for the LAMMPS",
                "neb command. Default value is 10000."]),
            'climbsteps': ' '.join([
                "The maximum number of NEB climbing steps to perform.",
                "This value corresponds to the N2 term for the LAMMPS",
                "neb command. Default value is 10000."]),
            'timestep': ' '.join([
                "The timestep to use with the quickmin minimization algorithm",
                "used for the NEB relaxations.  This value is in units of time.",
                "Default value is '0.01 ps'."]),
            'maxatommotion': ' '.join([
                "The maximum distance that any atom can move during a minimization",
                "iteration. This value is in units length and corresponds to the",
                "dmax term for the LAMMPS min_modify command. Default value is",
                "'0.01 angstrom'."]),
        }

    @property
    def preparekeys(self) -> list:
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  list(self.templatekeys.keys()) + []

    @property
    def interpretkeys(self) -> list:
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'force_unit',
                    'length_unit',
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

        force_per_length_unit = f'{self.parent.units.force_unit}/{self.parent.units.length_unit}'
        
        # Extract input values and assign default values
        self.numreplicas = input_dict.get(keymap['numreplicas'], 11)
        self.springconst = value(input_dict, keymap['springconst'],
                                 default_unit=force_per_length_unit,
                                 default_term='5.0 eV/angstrom^2')
        self.energytolerance = input_dict.get(keymap['energytolerance'], 0.0)
        self.forcetolerance = value(input_dict, keymap['forcetolerance'],
                                    default_unit=self.parent.units.force_unit,
                                    default_term='0.0')
        self.minsteps = input_dict.get(keymap['minsteps'], 10000)
        self.climbsteps = input_dict.get(keymap['climbsteps'], 10000)
        self.timestep = value(input_dict, keymap['timestep'],
                              default_unit='ps',
                              default_term='0.01 ps')
        self.maxatommotion = value(input_dict, keymap['maxatommotion'],
                                   default_unit=self.parent.units.length_unit,
                                   default_term='0.01 angstrom')

        # Check that one of the tolerances is set
        if self.energytolerance == 0.0 and self.forcetolerance == 0.0:
            raise ValueError('energytolerance and forcetolerance cannot both be 0.0')

########################### Data model interactions ###########################

    def load_model(self, model: DM):
        """Loads subset attributes from an existing model."""
        run_params = model['calculation']['run-parameter']

        self.numreplicas = run_params[f'{self.modelprefix}numreplicas']
        self.springconst = uc.value_unit(run_params[f'{self.modelprefix}springconst'])
        self.energytolerance = run_params[f'{self.modelprefix}energytolerance']
        self.forcetolerance = uc.value_unit(run_params[f'{self.modelprefix}forcetolerance'])
        self.minsteps = run_params[f'{self.modelprefix}minsteps']
        self.climbsteps = run_params[f'{self.modelprefix}climbsteps']
        self.timestep = uc.value_unit(run_params[f'{self.modelprefix}timestep'])
        self.maxatommotion = uc.value_unit(run_params[f'{self.modelprefix}maxatommotion'])

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

        # Check that one of the tolerances is set
        if self.energytolerance == 0.0 and self.forcetolerance == 0.0:
            raise ValueError('energytolerance and forcetolerance cannot both be 0.0')

        # Build paths if needed
        if 'calculation' not in model:
            model['calculation'] = DM()
        if 'run-parameter' not in model['calculation']:
            model['calculation']['run-parameter'] = DM()

        force_per_length_unit = f'{self.parent.units.force_unit}/{self.parent.units.length_unit}'
    
        # Save values
        run_params = model['calculation']['run-parameter']
        run_params[f'{self.modelprefix}numreplicas'] = self.numreplicas
        run_params[f'{self.modelprefix}springconst'] = uc.model(self.springconst,
                                                              force_per_length_unit)
        run_params[f'{self.modelprefix}energytolerance'] = self.energytolerance
        run_params[f'{self.modelprefix}forcetolerance'] = uc.model(self.forcetolerance,
                                                              self.parent.units.force_unit)
        run_params[f'{self.modelprefix}minsteps']  = self.minsteps
        run_params[f'{self.modelprefix}climbsteps'] = self.climbsteps
        run_params[f'{self.modelprefix}timestep']  = uc.model(self.timestep, 'ps')
        run_params[f'{self.modelprefix}maxatommotion']  = uc.model(self.maxatommotion,
                                                              self.parent.units.length_unit)

########################## Metadata interactions ##############################

    def metadata(self, meta: dict):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        # Check that one of the tolerances is set
        if self.energytolerance == 0.0 and self.forcetolerance == 0.0:
            raise ValueError('energytolerance and forcetolerance cannot both be 0.0')

        prefix = self.prefix
        meta[f'{prefix}numreplicas'] = self.numreplicas
        meta[f'{prefix}springconst'] = self.springconst
        meta[f'{prefix}energytolerance'] = self.energytolerance
        meta[f'{prefix}forcetolerance'] = self.forcetolerance
        meta[f'{prefix}minsteps'] = self.minsteps
        meta[f'{prefix}climbsteps'] = self.climbsteps
        meta[f'{prefix}timestep'] = self.timestep
        meta[f'{prefix}maxatommotion'] = self.maxatommotion

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
        # Check that one of the tolerances is set
        if self.energytolerance == 0.0 and self.forcetolerance == 0.0:
            raise ValueError('energytolerance and forcetolerance cannot both be 0.0')

        # Get ftol, dmax in LAMMPS units?
        input_dict['numreplicas'] = self.numreplicas
        input_dict['springconst'] = self.springconst
        input_dict['etol'] = self.energytolerance
        input_dict['ftol'] = self.forcetolerance
        input_dict['minsteps'] = self.minsteps
        input_dict['climbsteps'] = self.climbsteps
        input_dict['timestep'] = self.timestep
        input_dict['dmax'] = self.maxatommotion
