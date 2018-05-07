# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

# iprPy imports
from .. import value

__all__ = ['lammps_minimize']

def lammps_minimize(input_dict, **kwargs):
    """
    Interprets calculation parameters associated with a LAMMPS minimization.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'energytolerance'** The energy tolerance for the structure
      minimization.  This value is unitless. (Default is 0.0).
    - **'forcetolerance'** The force tolerance for the structure
      minimization. This value is in units of force. (Default is 0.0).
    - **'maxiterations'** The maximum number of minimization iterations to
      use (default is 10000).
    - **'maxevaluations'** The maximum number of minimization evaluations
      to use (default is 100000).
    - **'maxatommotion'** The maximum distance in length units that any
      atom is allowed to relax in any direction during a single
      minimization iteration (default is 0.01 Angstroms).
    - **'force_unit'** The default force unit to use for reading
      forcetolerance.
    - **'length_unit'** The default length unit to use for reading
      maxatommotion.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    energytolerance : str
        Replacement parameter key name for 'energytolerance'.
    forcetolerance : str
        Replacement parameter key name for 'forcetolerance'.
    maxiterations : str
        Replacement parameter key name for 'maxiterations'.
    maxevaluations : str
        Replacement parameter key name for 'maxevaluations'.
    maxatommotion : str
        Replacement parameter key name for 'maxatommotion'.
    force_unit : str
        Replacement parameter key name for 'force_unit'.
    length_unit : str
        Replacement parameter key name for 'length_unit'.
    
    Raises
    ------
    ValueError
        If both energytolerance and forcetolerance are 0.0.
    """
    
    # Set default keynames
    keynames = ['energytolerance', 'forcetolerance', 'maxiterations',
                'maxevaluations', 'maxatommotion', 'force_unit',
                'length_unit']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    force_unit = input_dict[kwargs['force_unit']]
    length_unit = input_dict[kwargs['length_unit']]
    
    etol = float(input_dict.get(kwargs['energytolerance'], 0.0))
    ftol = value(input_dict, kwargs['forcetolerance'],
                 default_unit=force_unit, default_term='0.0')
    maxiter = int(input_dict.get(kwargs['maxiterations'], 100000))
    maxeval = int(input_dict.get(kwargs['maxevaluations'], 1000000))
    dmax = value(input_dict, kwargs['maxatommotion'],
                 default_unit=length_unit, default_term='0.01 angstrom')
    
    if etol == 0.0 and ftol == 0.0:
        raise ValueError('energytolerance and forcetolerance cannot both be 0.0')
    
    # Save processed terms
    input_dict[kwargs['energytolerance']] = etol
    input_dict[kwargs['forcetolerance']] = ftol
    input_dict[kwargs['maxiterations']] = maxiter
    input_dict[kwargs['maxevaluations']] = maxeval
    input_dict[kwargs['maxatommotion']] = dmax