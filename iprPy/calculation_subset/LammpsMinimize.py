# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from . import CalculationSubset
from ..input import value

class LammpsMinimize(CalculationSubset):
    """Handles calculation terms for performing a LAMMPS energy/force minimization"""
    
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

        self.energytolerance = 0.0
        self.forcetolerance = 0.0
        self.maxiterations = 100000
        self.maxevaluations = 1000000
        self.maxatommotion = uc.set_in_units(0.01, 'angstrom') 

############################## Class attributes ################################

    @property
    def energytolerance(self):
        return self.__energytolerance

    @energytolerance.setter
    def energytolerance(self, value):
        self.__energytolerance = float(value)

    @property
    def forcetolerance(self):
        return self.__forcetolerance

    @forcetolerance.setter
    def forcetolerance(self, value):
        if isinstance(value, str):
            self.__forcetolerance = uc.set_literal(value)
        else:
            self.__forcetolerance = float(value)

    @property
    def maxiterations(self):
        return self.__maxiterations

    @maxiterations.setter
    def maxiterations(self, value):
        self.__maxiterations = int(value)
    
    @property
    def maxevaluations(self):
        return self.__maxevaluations

    @maxevaluations.setter
    def maxevaluations(self, value):
        self.__maxevaluations = int(value)

    @property
    def maxatommotion(self):
        return self.__maxatommotion

    @maxatommotion.setter
    def maxatommotion(self, value):
        if isinstance(value, str):
            self.__maxatommotion = uc.set_literal(value)
        else:
            self.__maxatommotion = float(value)

    def set_values(self, **kwargs):
        """
        Allows for multiple class attribute values to be updated at once.

        Parameters
        ----------
        energytolerance : float, optional
            The energy tolerance to set for the minimization.
        forcetolerance : float or str, optional
            The force tolerance to set for the minimization.  Can be given as
            a str that specifies force units.
        maxiterations : int, optional
            The maximum number of minimization iterations to use.
        maxevaluations : int, optional
            The maximum number of minimization maxevaluations to use.
        maxatommotion : float or str, optional
            The maximum atomic relaxation distance to allow for each iteration.
            Can be given as a str that specifies length units.
        """
        if 'energytolerance' in kwargs:
            self.energytolerance = kwargs['energytolerance']
        if 'forcetolerance' in kwargs:
            self.forcetolerance = kwargs['forcetolerance']
        if 'maxiterations' in kwargs:
            self.maxiterations = kwargs['maxiterations']
        if 'maxevaluations' in kwargs:
            self.maxevaluations = kwargs['maxevaluations']
        if 'maxatommotion' in kwargs:
            self.maxatommotion = kwargs['maxatommotion']

####################### Parameter file interactions ###########################

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return '# Energy/force minimization parameters'

    @property
    def templatekeys(self):
        """
        list : The input keys (without prefix) that appear in the input file.
        """
        return  [
                    'energytolerance',
                    'forcetolerance',
                    'maxiterations',
                    'maxevaluations',
                    'maxatommotion',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return  self.templatekeys + []

    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return  self.preparekeys + [
                    'force_unit',
                    'length_unit',
                ]

    def load_parameters(self, input_dict, build=True):
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
        self.energytolerance = input_dict.get(keymap['energytolerance'], 0.0)
        self.forcetolerance = value(input_dict, keymap['forcetolerance'],
                                    default_unit=self.parent.units.force_unit,
                                    default_term='0.0')
        self.maxiterations = input_dict.get(keymap['maxiterations'], 100000)
        self.maxevaluations = input_dict.get(keymap['maxevaluations'], 1000000)
        self.maxatommotion = value(input_dict, keymap['maxatommotion'],
                                   default_unit=self.parent.units.length_unit,
                                   default_term='0.01 angstrom')
        
        # Check that one of the tolerances is set
        if self.energytolerance == 0.0 and self.forcetolerance == 0.0:
            raise ValueError('energytolerance and forcetolerance cannot both be 0.0')

########################### Data model interactions ###########################

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        run_params = model['calculation']['run-parameter']

        self.energytolerance = run_params[f'{self.modelprefix}energytolerance']
        self.forcetolerance = uc.value_unit(run_params[f'{self.modelprefix}forcetolerance'])
        self.maxiterations = run_params[f'{self.modelprefix}maxiterations']
        self.maxevaluations = run_params[f'{self.modelprefix}maxevaluations']
        self.maxatommotion = uc.value_unit(run_params[f'{self.modelprefix}maxatommotion'])

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

        # Check that one of the tolerances is set
        if self.energytolerance == 0.0 and self.forcetolerance == 0.0:
            raise ValueError('energytolerance and forcetolerance cannot both be 0.0')

        # Build paths if needed
        if 'calculation' not in model:
            model['calculation'] = DM()
        if 'run-parameter' not in model['calculation']:
            model['calculation']['run-parameter'] = DM()
        
        # Save values
        run_params = record_model['calculation']['run-parameter']
        run_params[f'{self.modelprefix}energytolerance'] = self.energytolerance
        run_params[f'{self.modelprefix}forcetolerance'] = uc.model(self.forcetolerance,
                                                              self.parent.units.force_unit)
        run_params[f'{self.modelprefix}maxiterations']  = self.maxiterations
        run_params[f'{self.modelprefix}maxevaluations'] = self.maxevaluations
        run_params[f'{self.modelprefix}maxatommotion']  = uc.model(self.maxatommotion,
                                                              self.parent.units.length_unit)

########################## Metadata interactions ##############################

    def metadata(self, meta):
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
        meta[f'{prefix}energytolerance'] = self.energytolerance
        meta[f'{prefix}forcetolerance'] = self.forcetolerance
        meta[f'{prefix}maxiterations'] = self.maxiterations
        meta[f'{prefix}maxevaluations'] = self.maxevaluations
        meta[f'{prefix}maxatommotion'] = self.maxatommotion
    
########################### Calculation interactions ##########################

    def calc_inputs(self, input_dict):
        
        # Check that one of the tolerances is set
        if self.energytolerance == 0.0 and self.forcetolerance == 0.0:
            raise ValueError('energytolerance and forcetolerance cannot both be 0.0')
        
        # Get ftol, dmax in LAMMPS units?
        input_dict['etol'] = self.energytolerance
        input_dict['ftol'] = self.forcetolerance
        input_dict['maxiter'] = self.maxiterations
        input_dict['maxeval'] = self.maxevaluations
        input_dict['dmax'] = self.maxatommotion