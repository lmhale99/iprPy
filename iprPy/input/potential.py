import atomman.lammps as lmp

def potential(input_dict, **kwargs):
    """
    Initializes atomman.lammps.Potential based on input_dict keys 
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    potential_file -- the potential-LAMMPS model to load.
    potential_dir -- the directory containing all of the potential's artifacts 
    potential_content -- alternate file or content to load instead of specified 
                         potential_file. This is used by prepare functions.
    potential -- the atomman.lammps.Potential object created
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    potential_file -- replacement parameter key name for 'potential_file'
    potential_dir -- replacement parameter key name for 'potential_dir'
    potential -- replacement parameter key name for 'potential'
    """
    
    # Set default keynames
    keynames = ['potential_file', 'potential_dir', 'potential_content', 'potential']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    potential_file =    input_dict[kwargs['potential_file']]
    potential_dir =     input_dict.get(kwargs['potential_dir'], '')
    potential_content = input_dict.get(kwargs['potential_content'], None)
    
    # Use potential_content instead of potential_file if given
    if potential_content is not None:
        potential_file = potential_content
    
    # Save processed terms
    input_dict[kwargs['potential_dir']] = potential_dir
    input_dict[kwargs['potential']] =     lmp.Potential(potential_file, potential_dir)