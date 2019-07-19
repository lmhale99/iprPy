# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset

class AtommanSystemManipulate(Subset):
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
            'a_uvw',
            'b_uvw',
            'c_uvw',
            'atomshift',
            'sizemults',
        ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return self.templatekeys + []
    @property
    def interpretkeys(self):
        """
        list : The input keys (without prefix) accessed when interpreting the 
        calculation input file.  Typically, this is preparekeys plus any extra
        keys used or generated when processing the inputs.
        """
        return self.preparekeys + [
            'ucell',
            'uvws',
            'transformationmatrix',
            'initialsystem',
        ]

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# System manipulations'
        
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
        a_uvw = input_dict.get(keymap['a_uvw'], None)
        b_uvw = input_dict.get(keymap['b_uvw'], None)
        c_uvw = input_dict.get(keymap['c_uvw'], None)
        atomshift = input_dict.get(keymap['atomshift'], '0 0 0')
        sizemults = input_dict.get(keymap['sizemults'], '1 1 1')
        
        # Assign default uvws only if all are None
        if a_uvw is None and b_uvw is None and c_uvw is None:
            a_uvw = '1 0 0'
            b_uvw = '0 1 0'
            c_uvw = '0 0 1'
        
        # Issue error for incomplete uvws set
        elif a_uvw is None or b_uvw is None or c_uvw is None:
            raise TypeError('incomplete set of uvws terms')
            
        # Convert string values to lists of numbers
        sizemults = sizemults.strip().split()
        for i in range(len(sizemults)):
            sizemults[i] = int(sizemults[i])
        
        # Build uvws from a_uvw, b_uvw and c_uvw
        a = np.array(a_uvw.strip().split(), dtype=float)
        b = np.array(b_uvw.strip().split(), dtype=float)
        c = np.array(c_uvw.strip().split(), dtype=float)
        uvws = np.array([a, b, c])
        
        # Properly divide up sizemults if 6 terms given
        if len(sizemults) == 6:
            if (sizemults[0] <= 0 
                and sizemults[0] < sizemults[1]
                and sizemults[1] >= 0
                and sizemults[2] <= 0
                and sizemults[2] < sizemults[3]
                and sizemults[3] >= 0
                and sizemults[4] <= 0
                and sizemults[4] < sizemults[5]
                and sizemults[5] >= 0):
                
                sizemults =  [[sizemults[0], sizemults[1]],
                            [sizemults[2], sizemults[3]],
                            [sizemults[4], sizemults[5]]]
            
            else:
                raise ValueError('Invalid sizemults command')
        
        # Properly divide up sizemults if 3 terms given
        elif len(sizemults) == 3:
            for i in range(3):
                
                # Add 0 before if value is positive
                if sizemults[i] > 0:
                    sizemults[i] = [0, sizemults[i]]
                
                # Add 0 after if value is negative
                elif sizemults[i] < 0:
                    sizemults[i] = [sizemults[i], 0]
                
                else:
                    raise ValueError('Invalid sizemults command')
            
        else:
            raise ValueError('Invalid sizemults command')
        
        # Build initialsystem
        if build is True:
            # Extract ucell
            ucell = input_dict[keymap['ucell']]
            
            # Rotate to specified uvws
            initialsystem, transform = ucell.rotate(uvws, return_transform=True)
            
            # Shift atoms by atomshift
            shift = list(np.array(atomshift.strip().split(), dtype=float))
            initialsystem.atoms.pos += np.dot(shift, initialsystem.box.vects)
            
            # Apply sizemults
            initialsystem = initialsystem.supersize(tuple(sizemults[0]),
                                                    tuple(sizemults[1]),
                                                    tuple(sizemults[2]))
            initialsystem.wrap()
        
        else:
            initialsystem = None
            transform = None
        
        # Save processed terms
        input_dict[keymap['a_uvw']] = a_uvw
        input_dict[keymap['b_uvw']] = b_uvw
        input_dict[keymap['c_uvw']] = c_uvw
        input_dict[keymap['atomshift']] = atomshift
        input_dict[keymap['sizemults']] = sizemults
        input_dict[keymap['uvws']] = uvws
        input_dict[keymap['transformationmatrix']] = transform
        input_dict[keymap['initialsystem']] = initialsystem

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
        sizemults = input_dict[keymap['sizemults']]
        #atomshift = input_dict[keymap['atomshift']]
        #a_uvw = input_dict[keymap['a_uvw']]
        #b_uvw = input_dict[keymap['b_uvw']]
        #c_uvw = input_dict[keymap['c_uvw']]

        # Build paths if needed
        if 'calculation' not in record_model:
            record_model['calculation'] = DM()
        if 'run-parameter' not in record_model['calculation']:
            record_model['calculation']['run-parameter'] = DM()

        run_params = record_model['calculation']['run-parameter']
        
        run_params[f'{modelprefix}size-multipliers'] = DM()
        run_params[f'{modelprefix}size-multipliers']['a'] = list(sizemults[0])
        run_params[f'{modelprefix}size-multipliers']['b'] = list(sizemults[1])
        run_params[f'{modelprefix}size-multipliers']['c'] = list(sizemults[2])
        #run_params[f'{modelprefix}atom-shift'] = atomshift
        #run_params[f'{modelprefix}rotation-vector'] = DM()
        #run_params[f'{modelprefix}rotation-vector']['a'] = a_uvw
        #run_params[f'{modelprefix}rotation-vector']['b'] = b_uvw
        #run_params[f'{modelprefix}rotation-vector']['c'] = c_uvw
        
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