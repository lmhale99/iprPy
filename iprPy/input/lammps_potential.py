from DataModelDict import DataModelDict as DM
import atomman.lammps as lmp

def lammps_potential(input_dict, file='potential_file', dir='potential_dir', model='potential_model', pot='potential'):
    """
    Process input terms associated with a LAMMPS potential.
    
    Arguments:
    input_dict -- dictionary of input terms to process.
    
    Keyword Arguments:
    file -- key in input_dict where the potential file's path is stored.
            Default value is 'potential_file'.
    dir -- key in input_dict where the potential directory's path is stored.
           Default value is 'potential_dir'.
    model -- key in input_dict where the potential data model will be saved.
             Default value is 'potential_model'.
    pot -- key in input_dict where the potential object will be saved.
           Default value is 'potential'.
    """
    
    #Check for potential file
    assert file in input_dict, file + ' value not supplied'
    
    #Set default directory value if not given
    input_dict[dir] = input_dict.get(dir, '')
    
    #load potential data model and Potential object
    try:
        with open(input_dict[file]) as f:
            input_dict[model] = DM(f)
        input_dict[pot] = lmp.Potential(input_dict[model], input_dict[dir])
    except:
        raise ValueError(file + ' not a valid LAMMPS potential data model')