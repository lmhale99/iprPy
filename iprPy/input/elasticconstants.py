from DataModelDict import DataModelDict as DM
import atomman as am
def elasticconstants(input_dict, build=True, **kwargs):
    """
    Finds and sets elastic constants from input_dict info
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    elasticconstants_model -- a record containing elastic constants to load.
    elasticconstants_content -- alternate file or content to load instead of specified 
                       elasticconstants_model. This is used by prepare functions.
    C11, C12, ..., C66-- individually specified elastic constant terms.
    C -- atomman.ElasticConstants object
    load_file -- the system load file, which is searched for elastic constants if 
                 neither elasticconstants_model nor Cij terms are specified.
    load_content -- alternate file or content to load instead of specified load_file.
    pressure_unit -- default unit of pressure to use for reading in elastic constants.
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    build -- build -- boolean indicating if C should be built. If False,
             parameters will be interpreted, but the object won't be created. 
             Default value is True.
    elasticconstants_model -- replacement parameter key name for 'elasticconstants_model'
    elasticconstants_content -- replacement parameter key name for 'elasticconstants_content'
    Ckey -- replacement parameter key name for identifying the C11, C12, etc. terms    
    load_file -- replacement parameter key name for 'load_file'
    load_content -- replacement parameter key name for 'load_content'
    C -- replacement parameter key name for 'C'
    pressure_unit -- replacement parameter key name for 'pressure_unit'
    """
    
    # Set default keynames
    keynames = ['elasticconstants_model', 'elasticconstants_content', 'C', 
                'pressure_unit', 'load_file', 'load_content']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)

    # Extract input values and assign default values
    C = None
    Ckey = kwargs.get('Ckey', 'C')
    elasticconstants_model =   input_dict.get(kwargs['elasticconstants_model'],   None)
    elasticconstants_content = input_dict.get(kwargs['elasticconstants_content'], None)
    load_file =                input_dict.get(kwargs['load_file'],   None)
    load_content =             input_dict.get(kwargs['load_content'], None)
    pressure_unit =            input_dict[kwargs['pressure_unit']]
    
    # Replace model with content if given
    if elasticconstants_content is not None:
        elasticconstants_model = elasticconstants_content
    
    # Pull out any single elastic constant terms
    Cdict = {}
    for key in input_dict:
        keyhead = key[:len(Ckey)]
        keytail = key[len(Ckey):]
        if keyhead == Ckey:
            Cdict['C'+keytail] = iprPy.input.value(input_dict, key, default_unit=pressure_unit)
    
    # If model is given
    if elasticconstants_model is not None:
        assert len(Cdict) == 0, (keyhead + 'ij values and ' + kwargs['elasticconstants_model'] + 
                                 ' cannot both be specified.')
                                 
        if build is True:
            C = am.ElasticConstants(model=DM(elasticconstants_model))
            
    # Else if individual Cij terms are given
    elif len(Cdict) > 0:
        if build is True:
            C = am.ElasticConstants(**Cdict)
    
    # Else check load_file for elastic constants
    else:
        if build is True:
            if load_content is not None:
                load_file = load_content
                
            C = am.ElasticConstants(model=DM(load_file))
                    
    # Save processed terms
    input_dict[kwargs['C']] = C