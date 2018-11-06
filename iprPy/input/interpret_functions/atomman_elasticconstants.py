# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am

# iprPy imports
from ..value import value

__all__ = ['atomman_elasticconstants']

def atomman_elasticconstants(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with elastic constants.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'elasticconstants_file'** a record containing elastic constants to
      load.
    - **'elasticconstants_content'** alternate file or content to load instead
      of specified elasticconstants_file.  This is used by prepare functions.
    - **'C11', 'C12', ..., 'C66'** individually specified elastic constant
      terms.
    - **'C'** atomman.ElasticConstants object.
    - **'load_file'** the system load file, which is searched for elastic
      constants if neither elasticconstants_file nor Cij terms are specified.
    - **'load_content'** alternate file or content to load instead of
      the specified load_file.
    - **'pressure_unit'** default unit of pressure to use for reading in
      elastic constants.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    build : bool
        If False, parameters will be interpreted, but objects won't be built
        from them (Default is True).
    elasticconstants_file : str
        Replacement parameter key name for 'elasticconstants_file'.
    elasticconstants_content : str
        Replacement parameter key name for 'elasticconstants_content'.
    Ckey : str
        Replacement parameter key name for for identifying the C11, C12, etc.
        terms.
    load_file : str
        Replacement parameter key name for 'load_file'.
    load_content : str
        Replacement parameter key name for 'load_content'.
    C : str
        Replacement parameter key name for 'C'.
    pressure_unit : str
        Replacement parameter key name for 'pressure_unit'.
    """
    
    # Set default keynames
    keynames = ['elasticconstants_file', 'elasticconstants_content', 'C',
                'pressure_unit', 'load_file', 'load_content']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    C = None
    Ckey = kwargs.get('Ckey', 'C')
    elasticconstants_file = input_dict.get(kwargs['elasticconstants_file'], None)
    elasticconstants_content = input_dict.get(kwargs['elasticconstants_content'], None)
    load_file = input_dict.get(kwargs['load_file'], None)
    load_content = input_dict.get(kwargs['load_content'], None)
    pressure_unit = input_dict[kwargs['pressure_unit']]
    
    # Replace model with content if given
    if elasticconstants_content is not None:
        elasticconstants_file = elasticconstants_content
    
    # Pull out any single elastic constant terms
    Cdict = {}
    for key in input_dict:
        keyhead = key[:len(Ckey)]
        keytail = key[len(Ckey):]
        if keyhead == Ckey:
            Cdict['C'+keytail] = value(input_dict, key, default_unit=pressure_unit)
    
    # If model is given
    if elasticconstants_file is not None:
        assert len(Cdict) == 0, (keyhead + 'ij values and '
                                 + kwargs['elasticconstants_file']
                                 + ' cannot both be specified.')
        
        if build is True:
            C = am.ElasticConstants(model=DM(elasticconstants_file))
    
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