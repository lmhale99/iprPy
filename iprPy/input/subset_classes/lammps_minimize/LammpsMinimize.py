# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset
from ... import value

class LammpsMinimize(Subset):
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

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Energy/force minimization parameters'
        
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
        force_unit = input_dict.get(keymap['force_unit'], input_dict['force_unit'])
        length_unit = input_dict.get(keymap['length_unit'], input_dict['length_unit'])
        
        etol = float(input_dict.get(keymap['energytolerance'], 0.0))
        ftol = value(input_dict, keymap['forcetolerance'],
                    default_unit=force_unit, default_term='0.0')
        maxiter = int(input_dict.get(keymap['maxiterations'], 100000))
        maxeval = int(input_dict.get(keymap['maxevaluations'], 1000000))
        dmax = value(input_dict, keymap['maxatommotion'],
                    default_unit=length_unit, default_term='0.01 angstrom')
        
        if etol == 0.0 and ftol == 0.0:
            raise ValueError('energytolerance and forcetolerance cannot both be 0.0')
        
        # Save processed terms
        input_dict[keymap['energytolerance']] = etol
        input_dict[keymap['forcetolerance']] = ftol
        input_dict[keymap['maxiterations']] = maxiter
        input_dict[keymap['maxevaluations']] = maxeval
        input_dict[keymap['maxatommotion']] = dmax

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
        # Set prefixes
        prefix = self.prefix
        modelprefix = prefix.replace('_', '-')
        
        # Extract values
        keymap = self.keymap
        force_unit = input_dict.get(keymap['force_unit'], input_dict['force_unit'])
        length_unit = input_dict.get(keymap['length_unit'], input_dict['length_unit'])
        etol = input_dict[keymap['energytolerance']]
        ftol = input_dict[keymap['forcetolerance']]
        maxiter = input_dict[keymap['maxiterations']]
        maxeval = input_dict[keymap['maxevaluations']]
        dmax = input_dict[keymap['maxatommotion']]

        # Build paths if needed
        if 'calculation' not in record_model:
            record_model['calculation'] = DM()
        if 'run-parameter' not in record_model['calculation']:
            record_model['calculation']['run-parameter'] = DM()
        
        run_params = record_model['calculation']['run-parameter']
        
        # Save values
        run_params[f'{modelprefix}energytolerance'] = etol
        run_params[f'{modelprefix}forcetolerance'] = uc.model(ftol, f'{force_unit}')
        run_params[f'{modelprefix}maxiterations']  = maxiter
        run_params[f'{modelprefix}maxevaluations'] = maxeval
        run_params[f'{modelprefix}maxatommotion']  = uc.model(dmax, length_unit)
        
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
        run_params = record_model['calculation']['run-parameter']
        params[f'{prefix}energytolerance'] = run_params[f'{modelprefix}energytolerance']
        params[f'{prefix}forcetolerance'] = uc.value_unit(run_params[f'{modelprefix}forcetolerance'])
        params[f'{prefix}maxiterations'] = run_params[f'{modelprefix}maxiterations']
        params[f'{prefix}maxevaluations'] = run_params[f'{modelprefix}maxevaluations']
        params[f'{prefix}maxatommotion'] = uc.value_unit(run_params[f'{modelprefix}maxatommotion'])
        