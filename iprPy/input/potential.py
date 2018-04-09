# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

def potential(input_dict, **kwargs):
    """
    Interprets calculation parameters associated with a potential-LAMMPS
    record.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'potential_file'** the potential-LAMMPS model to load.
    - **'potential_dir'** the directory containing all of the potential's
      artifacts.
    - **'potential_content'** alternate file or content to load instead of
      specified potential_file. This is used by prepare functions.
    - **'potential'** the atomman.lammps.Potential object created.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    potential_file : str
        Replacement parameter key name for 'potential_file'.
    potential_dir : str
        Replacement parameter key name for 'potential_dir'.
    potential : str
        Replacement parameter key name for 'potential'.
    """
    
    # Set default keynames
    keynames = ['potential_file', 'potential_dir', 'potential_content',
                'potential']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    potential_file = input_dict[kwargs['potential_file']]
    potential_dir = input_dict.get(kwargs['potential_dir'], '')
    potential_content = input_dict.get(kwargs['potential_content'], None)
    
    # Use potential_content instead of potential_file if given
    if potential_content is not None:
        potential_file = potential_content
    
    # Save processed terms
    input_dict[kwargs['potential_dir']] = potential_dir
    input_dict[kwargs['potential']] = lmp.Potential(potential_file,
                                                    potential_dir)