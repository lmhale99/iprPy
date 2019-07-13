# https://github.com/usnistgov/atomman
import atomman as am

__all__ = ['atomman_peierlsnabarro']

def atomman_peierlsnabarro(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with a 
    calculation_generalized_stacking_fault record.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'peierlsnabarro_model'** a calculation record to load.
    - **'peierlsnabarro_content'** alternate file or content to load instead of
      specified dislocation_model.  This is used by prepare functions.
    - **'gamma'** a loaded GammaSurface object.
    - **'peierlsnabarro'** the SemiDiscretePeierlsNabarro object solution for
      peierlsnabarro_model and gamma.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    peierlsnabarro_model : str
        Replacement parameter key name for 'peierlsnabarro_model'
    peierlsnabarro_content :str
        Replacement parameter key name for 'peierlsnabarro_content'
    gamma : str
        Replacement parameter key name for 'gamma'.
    peierlsnabarro :str
        Replacement parameter key name for 'peierlsnabarro'
    """
    
    # Set default keynames
    keynames = ['peierlsnabarro_model', 'peierlsnabarro_content', 'gamma',
                'peierlsnabarro']
    
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    peierlsnabarro_model = input_dict.get(kwargs['peierlsnabarro_model'], None)
    peierlsnabarro_content = input_dict.get(kwargs['peierlsnabarro_content'], None)
    gamma = input_dict[kwargs['gamma']]
    
    # Replace defect model with defect content if given
    if peierlsnabarro_content is not None:
        peierlsnabarro_model = peierlsnabarro_content
    
    # Load Peierls-Nabarro solution
    if build is True:
        peierlsnabarro = am.defect.SDVPN(model=peierlsnabarro_model,
                                         gamma=gamma)
    else:
        peierlsnabarro = None
    
    # Save processed terms
    input_dict[kwargs['peierlsnabarro']] = peierlsnabarro