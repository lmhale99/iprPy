# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset
from ... import boolean

class FreeSurface(Subset):
    """
    Defines interactions for input keys associated with specifying input/output
    units.
    """
    @property
    def templatekeys(self):
        """
        list : The input keys (without prefix) that appear in the input file.
        """
        return [
            'surface_file',
            'surface_hkl',
            'surface_cellsetting',
            'surface_cutboxvector',
            'surface_shiftindex',
            'sizemults',
            'surface_minwidth',
            'surface_even',
        ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return self.templatekeys + [
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
    
    @property
    def keyset(self):
        """
        list : The input keyset for preparing.
        """
        keys = self.preparekeys
        keys.pop(keys.index('sizemults'))
        return self._pre(keys)

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Free surface defect parameters'
        
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
        surface_file = input_dict.get(keymap['surface_file'], None)
        surface_content = input_dict.get(keymap['surface_content'], None)
        
        # Replace defect model with defect content if given
        if surface_content is not None:
            surface_file = surface_content

        # If defect model is given
        if surface_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('surface_hkl',
                        'surface_shiftindex',
                        'surface_cellsetting',
                        'surface_cutboxvector'):
                assert keymap[key] not in input_dict, (keymap[key] + ' and '
                                                    + keymap['surface_model']
                                                    + ' cannot both be supplied')
            
            # Load defect model
            surface_model = DM(surface_file).find('free-surface')
                
            # Extract parameter values from defect model
            input_dict[keymap['surface_family']] = surface_model['system-family']
            input_dict[keymap['surface_hkl']] = surface_model['calculation-parameter']['hkl']
            input_dict[keymap['surface_shiftindex']] = int(surface_model['calculation-parameter'].get('shiftindex', 0))
            input_dict[keymap['surface_cutboxvector']] = surface_model['calculation-parameter']['cutboxvector']
            input_dict[keymap['surface_cellsetting']] = surface_model['calculation-parameter'].get('cellsetting', 'p')
        
        # Set default parameter values if defect model not given
        else:
            surface_model = None
            input_dict[keymap['surface_shiftindex']] = int(input_dict.get(keymap['surface_shiftindex'], 0))
            input_dict[keymap['surface_cutboxvector']] = input_dict.get(keymap['surface_cutboxvector'], 'c')
            input_dict[keymap['surface_cellsetting']] = input_dict.get(keymap['surface_cellsetting'], 'p')
            
        # Process defect parameters values
        input_dict[keymap['surface_model']] = surface_model
        input_dict[keymap['surface_hkl']] = np.array(input_dict[keymap['surface_hkl']].strip().split(), dtype=int)
        assert input_dict[keymap['surface_cutboxvector']] in ['a', 'b', 'c'], 'invalid surface_cutboxvector'
        assert input_dict[keymap['surface_cellsetting']] in ['p', 'a', 'b', 'c', 'i', 'f'], 'invalid surface_cellsetting'
        
        # Set default values for fault system manipulations
        sizemults = input_dict.get(keymap['sizemults'], '1 1 1')
        input_dict[keymap['surface_minwidth']] = float(input_dict.get(keymap['surface_minwidth'], 0.0))
        input_dict[keymap['surface_even']] = boolean(input_dict.get(keymap['surface_even'], False))

        # Convert string values to lists of numbers
        sizemults = sizemults.strip().split()
        for i in range(len(sizemults)):
            sizemults[i] = int(sizemults[i])
        assert len(sizemults) == 3, 'Invalid sizemults command: only 3 sizemults allowed for this calculation'
        
        input_dict[keymap['sizemults']] = sizemults

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

        # Extract values
        keymap = self.keymap
        surface_model = input_dict[keymap['surface_model']]
        surface_family = input_dict.get(keymap['surface_family'],
                                        input_dict['family'])
        sizemults = input_dict[keymap['sizemults']]
        surface_hkl = input_dict[keymap['surface_hkl']]
        surface_shiftindex = input_dict[keymap['surface_shiftindex']]
        surface_cutboxvector = input_dict[keymap['surface_cutboxvector']]
        surface_cellsetting = input_dict[keymap['surface_cellsetting']]
        surface_minwidth = input_dict[keymap['surface_minwidth']]

        #Save defect parameters
        record_model[f'{modelprefix}free-surface'] = surf = DM()

        # Build paths if needed
        if 'calculation' not in record_model:
            record_model['calculation'] = DM()
        if 'run-parameter' not in record_model['calculation']:
            record_model['calculation']['run-parameter'] = DM()

        run_params = record_model['calculation']['run-parameter']
        
        run_params[f'{modelprefix}size-multipliers'] = DM()
        run_params[f'{modelprefix}size-multipliers']['a'] = sorted([0, sizemults[0]])
        run_params[f'{modelprefix}size-multipliers']['b'] = sorted([0, sizemults[1]])
        run_params[f'{modelprefix}size-multipliers']['c'] = sorted([0, sizemults[2]])
        run_params[f'{modelprefix}minimum-width'] = uc.model(surface_minwidth,
                                                             units=input_dict['length_unit'])

        if surface_model is not None:
            surf['key'] = surface_model['key']
            surf['id'] = surface_model['id']
        else:
            surf['key'] = None
            surf['id'] = None
        surf['system-family'] = surface_family
        surf['calculation-parameter'] = cp = DM()
        if len(surface_hkl) == 3:
            cp['hkl'] = f'{surface_hkl[0]} {surface_hkl[1]} {surface_hkl[2]}'
        else:
            cp['hkl'] = f'{surface_hkl[0]} {surface_hkl[1]} {surface_hkl[2]} {surface_hkl[3]}'
        cp['shiftindex'] = str(surface_shiftindex)
        cp['cutboxvector'] = surface_cutboxvector
        cp['cellsetting'] = surface_cellsetting
        
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

        fs = record_model[f'{modelprefix}free-surface']
        params[f'{prefix}surface_key'] = fs['key']
        params[f'{prefix}surface_id'] = fs['id']
        params[f'{prefix}surface_hkl'] = fs['calculation-parameter']['hkl']
        params[f'{prefix}surface_shiftindex'] = fs['calculation-parameter']['shiftindex']

        sizemults = record_model['calculation']['run-parameter'][f'{modelprefix}size-multipliers']

        if flat is True:
            params[f'{prefix}a_mult1'] = sizemults['a'][0]
            params[f'{prefix}a_mult2'] = sizemults['a'][1]
            params[f'{prefix}b_mult1'] = sizemults['b'][0]
            params[f'{prefix}b_mult2'] = sizemults['b'][1]
            params[f'{prefix}c_mult1'] = sizemults['c'][0]
            params[f'{prefix}c_mult2'] = sizemults['c'][1]
        else:
            params[f'{prefix}sizemults'] = np.array([sizemults['a'], sizemults['b'], sizemults['c']])