import os
from DataModelDict import DataModelDict as DM

def system_family(input_dict, **kwargs):
    """
    Sets system_family (and system_potential) input terms based on a load file.
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    load -- load command containing a load style and load file path.
    load_file -- if given, this is used instead of the load file path specified
                 by the 'load' term. This is useful for prepare scripts as it 
                 allows a file to be interpreted prior to copying it to a 
                 calculation instance.
    system_family -- if the load file contains a system_family term, then it is
                     passed on. Otherwise, a new system_family is created based 
                     on the load file's name.
    system_potential -- if the load file is associated with a particular 
                        potential (i.e. is a calculation record) then a 
                        system_potential term is assigned that potential's id.
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    load -- replacement parameter key name for 'load'
    load_file -- replacement parameter key name for 'load_file'
    system_family -- replacement parameter key name for 'system_family'
    system_potential -- replacement parameter key name for 'system_potential'
    """
    
    #Set default keynames
    keynames = ['load', 'load_file', 'system_family', 'system_potential']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    #split load command into style and file
    load_terms = input_dict[kwargs['load']].split(' ')
    assert len(load_terms) > 1, kwargs['load'] + ' value must specify both style and file'
    load_style = load_terms[0]
    load_file =  input_dict[kwargs['load']].replace(load_style, '', 1).strip()
    
    #Define load_file_name
    load_file_name = os.path.splitext(os.path.basename(load_file))[0]
    
    #Replace load_file if indicated by input_dict terms
    if kwargs['load_file'] in input_dict:
        load_file = input_dict[kwargs['load_file']]
   
    #If load_style is system_model, check for system_family and system_potential
    if load_style == 'system_model':
        
        #Replace load_file if indicated by input_dict terms
        if kwargs['load_file'] in input_dict:
            model = input_dict[kwargs['load_file']]
        else:
            with open(load_file) as f:
                model = DM(f)
        
        #pass existing system_family name onto next generation
        try: 
            input_dict[kwargs['system_family']] = model.find('system-info')['artifact']['family']
        #generate new system_family name using load_file_name 
        except: 
            input_dict[kwargs['system_family']] = load_file_name
        
        #find if it is associated with a specific potential
        try: 
            input_dict[kwargs['system_potential']] = model.find('potential')['key']
        except: pass
    
    #Other load_styles won't have a system_family, so generate one using load_file_name
    else: 
        input_dict[kwargs['system_family']] = load_file_name