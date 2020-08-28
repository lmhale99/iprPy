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
            'dislocation_slip_hkl',
            'dislocation_ξ_uvw',
            'dislocation_burgers',
            'dislocation_m',
            'dislocation_n',
            'dislocation_shift',
            'dislocation_shiftscale',
            'dislocation_shiftindex',
            'sizemults',
            'amin',
            'bmin',
            'cmin',
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
        
        # Replace defect model with defect content if given
        if dislocation_content is not None:
            dislocation_file = dislocation_content
        
        # If defect model is given
        if dislocation_file is not None:
            
            # Verify competing parameters are not defined
            for key in ('dislocation_slip_hkl',
                        'dislocation_ξ_uvw',
                        'dislocation_burgers',
                        'dislocation_m',
                        'dislocation_n',
                        'dislocation_shift',
                        'dislocation_shiftscale',
                        'dislocation_shiftindex'):
                assert keymap[key] not in input_dict, (keymap[key] + ' and '
                                                    + keymap['dislocation_file']
                                                    + ' cannot both be supplied')
            
            # Load defect model
            dislocation_model = DM(dislocation_file).find('dislocation')
            
            # Extract parameter values from defect model
            input_dict[keymap['dislocation_family']] = dislocation_model['system-family']
            input_dict[keymap['dislocation_slip_hkl']] = dislocation_model['calculation-parameter']['slip_hkl']
            input_dict[keymap['dislocation_ξ_uvw']] = dislocation_model['calculation-parameter']['ξ_uvw']
            input_dict[keymap['dislocation_burgers']] = dislocation_model['calculation-parameter']['burgers']
            input_dict[keymap['dislocation_m']] = dislocation_model['calculation-parameter']['m']
            input_dict[keymap['dislocation_n']] = dislocation_model['calculation-parameter']['n']
            shift = dislocation_model['calculation-parameter'].get('shift', None)
            shiftindex = dislocation_model['calculation-parameter'].get('shiftindex', None)
            input_dict[keymap['dislocation_shiftscale']] = boolean(dislocation_model['calculation-parameter'].get('shiftscale', False))
        
        # Set default parameter values if defect model not given
        else: 
            dislocation_model = None
            input_dict[keymap['dislocation_lineboxvector']] = input_dict.get(keymap['dislocation_lineboxvector'], 'a')
            input_dict[keymap['dislocation_m']] = input_dict.get(keymap['dislocation_m'], '0 1 0')
            input_dict[keymap['dislocation_n']] = input_dict.get(keymap['dislocation_n'], '0 0 1')
            shift = input_dict.get(keymap['dislocation_shift'], None)
            shiftindex = input_dict.get(keymap['dislocation_shiftindex'], None)
            input_dict[keymap['dislocation_shiftscale']] = boolean(input_dict.get(keymap['dislocation_shiftscale'], False))
        
        # Process defect parameters
        input_dict[keymap['dislocation_model']] = dislocation_model
        try:
            input_dict[keymap['dislocation_slip_hkl']] = np.array(input_dict[keymap['dislocation_slip_hkl']].split(), dtype=int)
            assert input_dict[keymap['dislocation_slip_hkl']].shape == (3,)
        except:
            raise ValueError('Invalid dislocation_slip_hkl: must be 3 integers')
        try:
            input_dict[keymap['dislocation_ξ_uvw']] = np.array(input_dict[keymap['dislocation_ξ_uvw']].split(), dtype=int)
            assert input_dict[keymap['dislocation_ξ_uvw']].shape == (3,)
        except:
            raise ValueError('Invalid dislocation_ξ_uvw: must be 3 integers')
        try:
            input_dict[keymap['dislocation_burgers']] = np.array(input_dict[keymap['dislocation_burgers']].split(), dtype=float)
            assert input_dict[keymap['dislocation_burgers']].shape == (3,)
        except:
            raise ValueError('Invalid dislocation_burgers: must be 3 floats')

        try:
            input_dict[keymap['dislocation_m']] = m = np.array(input_dict[keymap['dislocation_m']].split(), dtype=float)
            input_dict[keymap['dislocation_n']] = n = np.array(input_dict[keymap['dislocation_n']].split(), dtype=float)
            assert m.shape == (3,) and n.shape == (3,)
            assert np.isclose(m[0], 1.0) or np.isclose(m[1], 1.0) or np.isclose(m[2], 1.0)
            assert np.isclose(n[0], 1.0) or np.isclose(n[1], 1.0) or np.isclose(n[2], 1.0)
            assert np.isclose(np.linalg.norm(m), 1.0) and np.isclose(np.linalg.norm(n), 1.0)
            assert np.isclose(m.dot(n), 0.0)
        except:
            raise ValueError("Invalid dislocation_m, dislocation_n orientation parameters: must be orthogonal unit vectors aligned with Cartesian axes")

        if shift is not None:
            shift = np.array(shift.split(), dtype='float')
        elif shiftindex is not None:
            shiftindex = int(shiftindex)
        input_dict[keymap['dislocation_shift']] = shift
        input_dict[keymap['dislocation_shiftindex']] = shiftindex

        # Set default values for fault system manipulations
        sizemults = input_dict.get(keymap['sizemults'], '1 1 1')
        input_dict[keymap['amin']] = float(input_dict.get(keymap['amin'], 0.0))
        input_dict[keymap['bmin']] = float(input_dict.get(keymap['bmin'], 0.0))
        input_dict[keymap['cmin']] = float(input_dict.get(keymap['cmin'], 0.0))

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
        dislocation_model = input_dict[keymap['dislocation_model']]
        dislocation_family = input_dict.get(keymap['dislocation_family'],
                                              input_dict['family'])
        sizemults = input_dict[keymap['sizemults']]
        slip_hkl = input_dict[keymap['dislocation_slip_hkl']]
        ξ_uvw = input_dict[keymap['dislocation_ξ_uvw']]
        burgers = input_dict[keymap['dislocation_burgers']]
        m = input_dict[keymap['dislocation_m']]
        n = input_dict[keymap['dislocation_n']]
        shift = input_dict[keymap['dislocation_shift']]
        shiftscale = input_dict[keymap['dislocation_shiftscale']]
        shiftindex = input_dict[keymap['dislocation_shiftindex']]

        # Save defect parameters
        record_model[f'{modelprefix}dislocation'] = disl = DM()

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
        
        if dislocation_model is not None:
            disl['key'] = dislocation_model['key']
            disl['id'] =  dislocation_model['id']
            disl['character'] = dislocation_model['character']
            disl['Burgers-vector'] = dislocation_model['Burgers-vector']
            disl['slip-plane'] = dislocation_model['slip-plane']
            disl['line-direction'] = dislocation_model['line-direction']
        else:
            disl['key'] = None
            disl['id'] = None
        disl['system-family'] = dislocation_family
        disl['calculation-parameter'] = cp = DM()
        cp['slip_hkl'] = f'{slip_hkl[0]} {slip_hkl[1]} {slip_hkl[2]}'
        cp['ξ_uvw'] = f'{ξ_uvw[0]} {ξ_uvw[1]} {ξ_uvw[2]}'
        cp['burgers'] = f'{burgers[0]} {burgers[1]} {burgers[2]}'
        cp['m'] = f'{m[0]} {m[1]} {m[2]}'
        cp['n'] = f'{n[0]} {n[1]} {n[2]}'
        if shift is not None:
            cp['shift'] = f'{shift[0]} {shift[1]} {shift[2]}'
        if shiftindex is not None:
            cp['shiftindex'] = str(shiftindex)
        cp['shiftscale'] = str(shiftscale)
        
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

        cp = disl['calculation-parameter']
        params[f'{prefix}dislocation_slip_hkl'] = cp['slip_hkl']
        params[f'{prefix}dislocation_ξ_uvw'] = cp['ξ_uvw']
        params[f'{prefix}dislocation_burgers'] = cp['burgers']
        params[f'{prefix}dislocation_m'] = cp['m']
        params[f'{prefix}dislocation_n'] = cp['n']
        params[f'{prefix}dislocation_shift'] = cp.get('shift', None)
        params[f'{prefix}dislocation_shiftscale'] = cp['shiftscale']
        params[f'{prefix}dislocation_shiftindex'] = cp.get('shiftindex', None)