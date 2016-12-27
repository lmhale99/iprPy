from DataModelDict import DataModelDict as DM
import atomman.lammps as lmp

def potential(input_dict, **kwargs):
    """
    Handles input parameters associated with a LAMMPS potential.
    1. Checks that 'potential_file' is given in input file
    2. Sets default value of '' to 'potential_dir' term if needed.
    3. Saves atomman.lammps.Potential object of the potential to the input_dict
       as 'potential'.
    
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    potential -- replacement parameter key name for 'potential'
    potential_file -- replacement parameter key name for 'potential_file'
    potential_dir -- replacement parameter key name for 'potential_dir'
    """
    
    #Set default keynames
    keynames = ['potential_file', 'potential_dir', 'potential']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    #Check for potential file
    assert kwargs['potential_file'] in input_dict, kwargs['potential_file'] + ' value not supplied'
    
    #Set default directory value if not given
    input_dict[kwargs['potential_dir']] = input_dict.get(kwargs['potential_dir'], '')
    
    #load potential data model and Potential object
    with open(input_dict[kwargs['potential_file']]) as f:
        input_dict[kwargs['potential']] = lmp.Potential(f, input_dict[kwargs['potential_dir']])