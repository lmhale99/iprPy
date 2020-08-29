# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset
from ... import boolean

class StackingFault(Subset):
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
            'stackingfault_file',
            'stackingfault_hkl',
            'stackingfault_a1vect_uvw',
            'stackingfault_a2vect_uvw',
            'stackingfault_cellsetting',
            'stackingfault_cutboxvector',
            'stackingfault_shiftindex',
            'stackingfault_faultpos_rel',
            'sizemults',
            'stackingfault_minwidth',
            'stackingfault_even',
        ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return self.templatekeys + [
            'stackingfault_family',
            'stackingfault_content',
        ]
    
    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return self.preparekeys + [
            'stackingfault_model',
        ]

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Stacking fault defect parameters'
        
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
        stackingfault_file = input_dict.get(keymap['stackingfault_file'], None)
        stackingfault_content = input_dict.get(keymap['stackingfault_content'],
                                            None)
        
        # Replace defect model with defect content if given
        if stackingfault_content is not None:
            stackingfault_file = stackingfault_content
        
        # If defect model is given
        if stackingfault_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('stackingfault_hkl',
                        'stackingfault_shiftindex',
                        'stackingfault_a1vect_uvw',
                        'stackingfault_a2vect_uvw',
                        'stackingfault_cellsetting',
                        'stackingfault_cutboxvector',
                        'stackingfault_faultpos_rel'):
                assert keymap[key] not in input_dict, (keymap[key] + ' and '
                                                    + keymap['stackingfault_file']
                                                    + ' cannot both be supplied')
            
            # Load defect model
            stackingfault_model = DM(stackingfault_file).find('stacking-fault')
            
            # Extract parameter values from defect model
            input_dict[keymap['stackingfault_family']] = stackingfault_model['system-family']
            input_dict[keymap['stackingfault_hkl']] = stackingfault_model['calculation-parameter']['hkl']
            input_dict[keymap['stackingfault_a1vect_uvw']] = stackingfault_model['calculation-parameter']['a1vect_uvw']
            input_dict[keymap['stackingfault_a2vect_uvw']] = stackingfault_model['calculation-parameter']['a2vect_uvw']
            input_dict[keymap['stackingfault_shiftindex']] = int(stackingfault_model['calculation-parameter'].get('shiftindex', 0))
            input_dict[keymap['stackingfault_cutboxvector']] = stackingfault_model['calculation-parameter']['cutboxvector']
            input_dict[keymap['stackingfault_faultpos_rel']] = float(stackingfault_model['calculation-parameter'].get('faultpos_rel', 0.5))
            input_dict[keymap['stackingfault_cellsetting']] = stackingfault_model['calculation-parameter'].get('cellsetting', 'p')
        
        # Set default parameter values if defect model not given
        else:
            stackingfault_model = None
            input_dict[keymap['stackingfault_a1vect_uvw']] = input_dict.get(keymap['stackingfault_a1vect_uvw'], None)
            input_dict[keymap['stackingfault_a2vect_uvw']] = input_dict.get(keymap['stackingfault_a2vect_uvw'], None)
            input_dict[keymap['stackingfault_shiftindex']] = int(input_dict.get(keymap['stackingfault_shiftindex'], 0))
            input_dict[keymap['stackingfault_cutboxvector']] = input_dict.get(keymap['stackingfault_cutboxvector'], 'c')
            input_dict[keymap['stackingfault_faultpos_rel']] = float(input_dict.get(keymap['stackingfault_faultpos_rel'], 0.5))
            input_dict[keymap['stackingfault_cellsetting']] = input_dict.get(keymap['stackingfault_cellsetting'], 'p')
            
        # Process defect parameters values
        input_dict[keymap['stackingfault_model']] = stackingfault_model
        input_dict[keymap['stackingfault_hkl']] = np.array(input_dict[keymap['stackingfault_hkl']].strip().split(), dtype=int)
        if input_dict[keymap['stackingfault_a1vect_uvw']] is not None:
            input_dict[keymap['stackingfault_a1vect_uvw']] = np.array(input_dict[keymap['stackingfault_a1vect_uvw']].strip().split(), dtype=float)
        if input_dict[keymap['stackingfault_a2vect_uvw']] is not None:
            input_dict[keymap['stackingfault_a2vect_uvw']] = np.array(input_dict[keymap['stackingfault_a2vect_uvw']].strip().split(), dtype=float)
        assert input_dict[keymap['stackingfault_cutboxvector']] in ['a', 'b', 'c'], 'invalid stackingfault_cutboxvector'
        assert input_dict[keymap['stackingfault_faultpos_rel']] > 0 and input_dict[keymap['stackingfault_faultpos_rel']] < 1, 'invalid stackingfault_faultpos_rel'
        assert input_dict[keymap['stackingfault_cellsetting']] in ['p', 'a', 'b', 'c', 'i', 'f'], 'invalid stackingfault_cellsetting'
        
        # Set default values for fault system manipulations
        sizemults = input_dict.get(keymap['sizemults'], '1 1 1')
        input_dict[keymap['stackingfault_minwidth']] = float(input_dict.get(keymap['stackingfault_minwidth'], 0.0))
        input_dict[keymap['stackingfault_even']] = boolean(input_dict.get(keymap['stackingfault_even'], False))

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
        stackingfault_model = input_dict[keymap['stackingfault_model']]
        stackingfault_family = input_dict.get(keymap['stackingfault_family'],
                                              input_dict['family'])
        sizemults = input_dict[keymap['sizemults']]
        stackingfault_hkl = input_dict[keymap['stackingfault_hkl']]
        stackingfault_a1vect_uvw = input_dict[keymap['stackingfault_a1vect_uvw']]
        stackingfault_a2vect_uvw = input_dict[keymap['stackingfault_a2vect_uvw']]
        stackingfault_shiftindex = input_dict[keymap['stackingfault_shiftindex']]
        stackingfault_cutboxvector = input_dict[keymap['stackingfault_cutboxvector']]
        stackingfault_faultpos_rel = input_dict[keymap['stackingfault_faultpos_rel']]
        stackingfault_cellsetting = input_dict[keymap['stackingfault_cellsetting']]
        stackingfault_minwidth = input_dict[keymap['stackingfault_minwidth']]

        # Save defect model information
        record_model[f'{modelprefix}stacking-fault'] = sf = DM()
        
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
        run_params[f'{modelprefix}minimum-width'] = uc.model(stackingfault_minwidth,
                                                             units=input_dict['length_unit'])

        if stackingfault_model is not None:
            sf['key'] = stackingfault_model['key']
            sf['id'] =  stackingfault_model['id']
        else:
            sf['key'] = None
            sf['id'] =  None
        sf['system-family'] = stackingfault_family
        sf['calculation-parameter'] = cp = DM()
        if len(stackingfault_hkl) == 3:
            cp['hkl'] = f'{stackingfault_hkl[0]} {stackingfault_hkl[1]} {stackingfault_hkl[2]}'
        else:
            cp['hkl'] = f'{stackingfault_hkl[0]} {stackingfault_hkl[1]} {stackingfault_hkl[2]} {stackingfault_hkl[3]}'
        cp['a1vect_uvw'] = f'{stackingfault_a1vect_uvw[0]} {stackingfault_a1vect_uvw[1]} {stackingfault_a1vect_uvw[2]}'
        cp['a2vect_uvw'] = f'{stackingfault_a2vect_uvw[0]} {stackingfault_a2vect_uvw[1]} {stackingfault_a2vect_uvw[2]}'
        cp['shiftindex'] = str(stackingfault_shiftindex)
        cp['cutboxvector'] = stackingfault_cutboxvector
        cp['faultpos_rel'] = str(stackingfault_faultpos_rel)
        cp['cellsetting'] = stackingfault_cellsetting
        
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

        sf = record_model[f'{modelprefix}stacking-fault']
        params[f'{prefix}stackingfault_key'] = sf['key']
        params[f'{prefix}stackingfault_id'] = sf['id']
        params[f'{prefix}stackingfault_hkl'] = sf['calculation-parameter']['hkl']
        params[f'{prefix}stackingfault_a1vect_uvw'] = sf['calculation-parameter']['a1vect_uvw']
        params[f'{prefix}stackingfault_a2vect_uvw'] = sf['calculation-parameter']['a2vect_uvw']
        params[f'{prefix}stackingfault_shiftindex'] = sf['calculation-parameter']['shiftindex']

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