# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

__all__ = ['lammps_atomcharges']

def lammps_atomcharges(input_dict, build=True, **kwargs):
    """
    Assigns per-atom charges (if needed) to a loaded ucell system based on
    a loaded atomma.lammps.Potential object.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'potential'** the loaded atomman.lammps.Potential object.
    - **'ucell'** the loaded crystal system.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    build : bool
        If False, parameters will be interpreted, but objects won't be built
        from them (Default is True).
    potential : str
        Replacement parameter key name for 'potential'.
    ucell : str
        Replacement parameter key name for 'ucell'.
    """
    
    # Set default keynames
    keynames = ['potential', 'ucell']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    if build:
        # Extract input values
        ucell = input_dict[kwargs['ucell']]
        potential = input_dict[kwargs['potential']]
        
        # Check if ucell was loaded with charge info
        if 'charge' not in ucell.atoms_prop():
            ucell.atoms.prop_atype('charge', potential.charges(ucell.symbols))