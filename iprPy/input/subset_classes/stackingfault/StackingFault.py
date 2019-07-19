# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset

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
            'stackingfault_cutboxvector',
            'stackingfault_faultpos',
            'stackingfault_shiftvector1',
            'stackingfault_shiftvector2',
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
            'a_uvw', 
            'b_uvw',
            'c_uvw',
            'atomshift',
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
            'ucell',
            'uvws',
            'faultpos',
            'shiftvector1',
            'shiftvector2',
            'transformationmatrix',
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
            for key in ('atomshift', 'a_uvw', 'b_uvw', 'c_uvw',
                        'stackingfault_cutboxvector', 'stackingfault_faultpos',
                        'stackingfault_shiftvector1',
                        'stackingfault_shiftvector2'):
                assert keymap[key] not in input_dict, (keymap[key] + ' and '
                                                    + keymap['dislocation_model']
                                                    + ' cannot both be supplied')
            
            # Load defect model
            stackingfault_model = DM(stackingfault_file).find('stacking-fault')
            
            
            # Extract parameter values from defect model
            input_dict[keymap['stackingfault_family']] = stackingfault_model['system-family']
            input_dict[keymap['a_uvw']] = stackingfault_model['calculation-parameter']['a_uvw']
            input_dict[keymap['b_uvw']] = stackingfault_model['calculation-parameter']['b_uvw']
            input_dict[keymap['c_uvw']] = stackingfault_model['calculation-parameter']['c_uvw']
            input_dict[keymap['atomshift']] = stackingfault_model['calculation-parameter']['atomshift']
            input_dict[keymap['stackingfault_cutboxvector']] = stackingfault_model['calculation-parameter']['cutboxvector']
            input_dict[keymap['stackingfault_faultpos']] = float(stackingfault_model['calculation-parameter']['faultpos'])
            input_dict[keymap['stackingfault_shiftvector1']] = stackingfault_model['calculation-parameter']['shiftvector1']
            input_dict[keymap['stackingfault_shiftvector2']] = stackingfault_model['calculation-parameter']['shiftvector2']
        
        # Set default parameter values if defect model not given
        else:
            stackingfault_model = None
            input_dict[keymap['stackingfault_cutboxvector']] = input_dict.get(keymap['stackingfault_cutboxvector'], 'c')
            input_dict[keymap['stackingfault_faultpos']] = float(input_dict.get(keymap['stackingfault_faultpos'], 0.5))
            assert input_dict[keymap['stackingfault_cutboxvector']] in ['a', 'b', 'c'], 'invalid stackingfault_cutboxvector'
        
        input_dict[keymap['stackingfault_model']] = stackingfault_model
    
    def interpret2(self, input_dict, build=True):
        """
        Interprets calculation parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary containing input parameter key-value pairs.
        """

        # Set default keynames
        keymap = self.keymap
        
        if build is True:
        
            # Extract input values and assign default values
            stackingfault_faultpos = input_dict[keymap['stackingfault_faultpos']]
            stackingfault_shiftvector1 = input_dict[keymap['stackingfault_shiftvector1']]
            stackingfault_shiftvector2 = input_dict[keymap['stackingfault_shiftvector2']]
            stackingfault_cutboxvector = input_dict[keymap['stackingfault_cutboxvector']]
            sizemults = input_dict['sizemults']
            
            # Convert string terms to arrays
            shiftvector1 = np.array(stackingfault_shiftvector1.strip().split(), dtype=float)
            shiftvector2 = np.array(stackingfault_shiftvector2.strip().split(), dtype=float)
            
            # Identify number of size multiples, m, along cutboxvector
            if   stackingfault_cutboxvector == 'a': 
                m = sizemults[0]
            elif stackingfault_cutboxvector == 'b': 
                m = sizemults[1]
            elif stackingfault_cutboxvector == 'c': 
                m = sizemults[2]
            if isinstance(m, (list, tuple)):
                m = m[1] - m[0]
            
            # For odd m, initial position of 0.5 goes to 0.5
            if m % 2 == 1:
                faultpos = (stackingfault_faultpos + (m-1) * 0.5) / m
            # For even m, initial position of 0.0 goes to 0.5
            else:
                faultpos = (2 * stackingfault_faultpos + m) / (2 * m)
        
        else:
            faultpos = None
            shiftvector1 = None
            shiftvector2 = None
        
        # Save processed terms
        input_dict[keymap['faultpos']] = faultpos
        input_dict[keymap['shiftvector1']] = shiftvector1
        input_dict[keymap['shiftvector2']] = shiftvector2

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
        a_uvw = input_dict[keymap['a_uvw']]
        b_uvw = input_dict[keymap['b_uvw']]
        c_uvw = input_dict[keymap['c_uvw']]
        atomshift = input_dict[keymap['atomshift']]
        stackingfault_cutboxvector = input_dict[keymap['stackingfault_cutboxvector']]
        stackingfault_faultpos = input_dict[keymap['stackingfault_faultpos']]
        stackingfault_shiftvector1 = input_dict[keymap['stackingfault_shiftvector1']]
        stackingfault_shiftvector2 = input_dict[keymap['stackingfault_shiftvector2']]

        #Save defect model information
        record_model[f'{modelprefix}stacking-fault'] = sf = DM()
        
        if stackingfault_model is not None:
            sf['key'] = stackingfault_model['key']
            sf['id'] =  stackingfault_model['id']
        else:
            sf['key'] = None
            sf['id'] =  None
        sf['system-family'] = stackingfault_family
        sf['calculation-parameter'] = cp = DM()
        cp['a_uvw'] = a_uvw
        cp['b_uvw'] = b_uvw
        cp['c_uvw'] = c_uvw
        cp['atomshift'] = atomshift
        cp['cutboxvector'] = stackingfault_cutboxvector
        cp['faultpos'] = stackingfault_faultpos
        cp['shiftvector1'] = stackingfault_shiftvector1
        cp['shiftvector2'] = stackingfault_shiftvector2
        
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
        params['stackingfault_key'] = sf['key']
        params['stackingfault_id'] = sf['id']