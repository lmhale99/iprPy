# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

from ..Subset import Subset
from ...boolean import boolean

class Dislocation(Subset):
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
            'dislocation_file',
            'dislocation_stroh_m',
            'dislocation_stroh_n',
            'dislocation_lineboxvector',
            'dislocation_burgersvector',
        ]
    
    @property
    def preparekeys(self):
        """
        list : The input keys (without prefix) used when preparing a calculation.
        Typically, this is templatekeys plus *_content keys so prepare can access
        content before it exists in the calc folders being prepared.
        """
        return self.templatekeys + [
            'dislocation_family',
            'dislocation_content',
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
            'dislocation_model',  
            'stroh_m',
            'stroh_n',
            'ucell',
            'burgersvector',
        ]

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Dislocation defect parameters'
        
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
        dislocation_file = input_dict.get(keymap['dislocation_file'], None)
        dislocation_content = input_dict.get(keymap['dislocation_content'], None)
        ucell = input_dict.get(keymap['ucell'], None)
        
        # Replace defect model with defect content if given
        if dislocation_content is not None:
            dislocation_file = dislocation_content
        
        # If defect model is given
        if dislocation_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('atomshift', 'a_uvw', 'b_uvw', 'c_uvw', 'dislocation_lineboxvector',
                        'dislocation_stroh_m', 'dislocation_stroh_n', 'dislocation_burgersvector'):
                assert keymap[key] not in input_dict, (keymap[key] + ' and '
                                                    + keymap['dislocation_file']
                                                    + ' cannot both be supplied')
            
            # Load defect model
            dislocation_model = DM(dislocation_file).find('dislocation')
            
            # Extract parameter values from defect model
            input_dict[keymap['dislocation_family']] = dislocation_model['system-family']
            input_dict[keymap['dislocation_stroh_m']] = dislocation_model['calculation-parameter']['stroh_m']
            input_dict[keymap['dislocation_stroh_n']] = dislocation_model['calculation-parameter']['stroh_n']
            input_dict[keymap['dislocation_lineboxvector']] = dislocation_model['calculation-parameter']['lineboxvector']
            input_dict[keymap['a_uvw']] = dislocation_model['calculation-parameter']['a_uvw']
            input_dict[keymap['b_uvw']] = dislocation_model['calculation-parameter']['b_uvw']
            input_dict[keymap['c_uvw']] = dislocation_model['calculation-parameter']['c_uvw']
            input_dict[keymap['atomshift']] = dislocation_model['calculation-parameter']['atomshift']
            input_dict[keymap['dislocation_burgersvector']] = dislocation_model['calculation-parameter']['burgersvector']
        
        # Set default parameter values if defect model not given
        else: 
            dislocation_model = None
            input_dict[keymap['dislocation_lineboxvector']] = input_dict.get(keymap['dislocation_lineboxvector'], 'a')
            input_dict[keymap['dislocation_stroh_m']] = input_dict.get(keymap['dislocation_stroh_m'], '0 1 0')
            input_dict[keymap['dislocation_stroh_n']] = input_dict.get(keymap['dislocation_stroh_n'], '0 0 1')
        
        # convert parameters if ucell exists
        if ucell is not None:
            dislocation_burgersvector = input_dict[keymap['dislocation_burgersvector']]
            dislocation_burgersvector = np.array(dislocation_burgersvector.strip().split(),
                                                dtype=float)
            
            # Convert crystallographic vectors to Cartesian vectors
            burgersvector = (dislocation_burgersvector[0] * ucell.box.avect +
                            dislocation_burgersvector[1] * ucell.box.bvect +
                            dislocation_burgersvector[2] * ucell.box.cvect)
            
            # Interpret and check Stroh orientation vectors
            stroh_m = np.array(input_dict[keymap['dislocation_stroh_m']].split(), dtype=float)
            stroh_n = np.array(input_dict[keymap['dislocation_stroh_n']].split(), dtype=float)
            try:
                assert stroh_m.shape == (3,) and stroh_n.shape == (3,)
                assert np.isclose(np.linalg.norm(stroh_m), 1.0)
                assert np.isclose(np.linalg.norm(stroh_n), 1.0)
                assert np.isclose(stroh_m.dot(stroh_n), 0.0)
            except:
                raise ValueError("Invalid m, n Stroh orientation parameters")
        
        else:
            burgersvector = None
            stroh_m = None
            stroh_n = None
        
        # Save processed terms
        input_dict[keymap['dislocation_model']] = dislocation_model
        input_dict[keymap['burgersvector']] = burgersvector
        input_dict[keymap['stroh_m']] = stroh_m
        input_dict[keymap['stroh_n']] = stroh_n

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
        dislocation_model = input_dict[keymap['dislocation_model']]
        dislocation_family = input_dict.get(keymap['dislocation_family'],
                                              input_dict['family'])
        a_uvw = input_dict[keymap['a_uvw']]
        b_uvw = input_dict[keymap['b_uvw']]
        c_uvw = input_dict[keymap['c_uvw']]
        atomshift = input_dict[keymap['atomshift']]
        dislocation_stroh_m = input_dict[keymap['dislocation_stroh_m']]
        dislocation_stroh_n = input_dict[keymap['dislocation_stroh_n']]
        dislocation_lineboxvector = input_dict[keymap['dislocation_lineboxvector']]
        dislocation_burgersvector = input_dict[keymap['dislocation_burgersvector']]

        # Save defect parameters
        record_model[f'{modelprefix}dislocation'] = disl = DM()
        if dislocation_model is not None:
            disl['key'] = dislocation_model['key']
            disl['id'] =  dislocation_model['id']
            disl['character'] = dislocation_model['character']
            disl['Burgers-vector'] = dislocation_model['Burgers-vector']
            disl['slip-plane'] = dislocation_model['slip-plane']
            disl['line-direction'] = dislocation_model['line-direction']
        disl['system-family'] = dislocation_family
        
        disl['calculation-parameter'] = cp = DM()
        cp['stroh_m'] = dislocation_stroh_m
        cp['stroh_n'] = dislocation_stroh_n
        cp['lineboxvector'] = dislocation_lineboxvector
        cp['a_uvw'] = a_uvw
        cp['b_uvw'] = b_uvw
        cp['c_uvw'] = c_uvw
        cp['atomshift'] = atomshift
        cp['burgersvector'] = dislocation_burgersvector
        
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

        disl = record_model[f'{modelprefix}dislocation']
        params[f'{prefix}dislocation_key'] = disl['key']
        params[f'{prefix}dislocation_id'] = disl['id']