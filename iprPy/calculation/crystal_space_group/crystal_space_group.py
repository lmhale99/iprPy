# coding: utf-8

# Python script created by Lucas Hale

# http://www.numpy.org/
import numpy as np

# https://atztogo.github.io/spglib/python-spglib.html
# https://atztogo.github.io/spglib/python-spglib.html
try:
    import spglib
except ImportError:
    raise ImportError("The package, spglib, is not installed by default. Please install with pip or conda.")

# https://github.com/usnistgov/atomman 
import atomman as am

def crystal_space_group(system: am.System,
                        symprec: float = 1e-5,
                        to_primitive: bool = False,
                        no_idealize: bool = False) -> dict:
    """
    Uses spglib to evaluate space group information for a given system.
    
    Parameters
    ----------
    system : atomman.System
        The system to analyze.
    symprec : float, optional
        Absolute length tolerance to use in identifying symmetry of atomic
        sites and system boundaries. Default value is 1e-5
    to_primitive : bool, optional
        Indicates if the returned unit cell is conventional (False) or
        primitive (True). Default value is False.
    no_idealize : bool, optional
        Indicates if the atom positions in the returned unit cell are averaged
        (True) or idealized based on the structure (False).  Default value is
        False.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:

        - **'number'** (*int*) The spacegroup number.
        - **'international_short'** (*str*) The short international spacegroup
          symbol.
        - **'international_full'** (*str*) The full international spacegroup
          symbol.
        - **'international'** (*str*) The international spacegroup symbol.
        - **'schoenflies'** (*str*) The schoenflies spacegroup symbol.
        - **'hall_symbol'** (*str*) The Hall symbol.
        - **'choice'** (*str*) The setting choice if there is one.
        - **'pointgroup_international'** (*str*) The international pointgroup
          symbol.
        - **'pointgroup_schoenflies'** (*str*) The schoenflies pointgroup
          symbol.
        - **'arithmetic_crystal_class_number'** (*int*) The arithmetic crystal
          class number.
        - **'arithmetic_crystal_class_symbol'** (*str*) The arithmetic crystal
          class symbol.
        - **'ucell'** (*am.System*) The spacegroup-processed unit cell.
        - **'hall_number'** (*int*) The Hall number.
        - **'wyckoffs'** (*list*) A list of the spacegroup's Wyckoff symbols
          where atoms are found.
        - **'equivalent_atoms'** (*list*) A list of indices indicating which
          atoms are equivalent to others.
        - **'pearson'** (*str*) The Pearson symbol.
        - **'wyckoff_fingerprint'** (*str*) The Wyckoff symbols joined
          together.
    """
    # Identify the standardized unit cell representation
    sym_data = spglib.get_symmetry_dataset(system.dump('spglib_cell'), symprec=symprec)
    ucell = spglib.standardize_cell(system.dump('spglib_cell'),
                                    to_primitive=to_primitive,
                                    no_idealize=no_idealize, symprec=symprec)
    
    # Convert back to atomman systems and normalize
    ucell = am.load('spglib_cell', ucell, symbols=system.symbols)
    ucell.atoms.pos -= ucell.atoms.pos[0]
    ucell = ucell.normalize()
    
    # Throw error if natoms > 2000
    natoms = ucell.natoms
    if natoms > 2000:
        raise RuntimeError('too many positions')

    # Average extra per-atom properties by mappings to primitive
    for index in np.unique(sym_data['mapping_to_primitive']):
        for key in system.atoms.prop():
            if key in ['atype', 'pos']:
                continue
            value = system.atoms.view[key][sym_data['mapping_to_primitive'] == index].mean()
            if key not in ucell.atoms.prop():
                ucell.atoms.view[key] = np.zeros_like(value)
            ucell.atoms.view[key][sym_data['std_mapping_to_primitive'] == index] = value
    
    # Get space group metadata
    sym_data = spglib.get_symmetry_dataset(ucell.dump('spglib_cell'))
    spg_type = spglib.get_spacegroup_type(sym_data['hall_number'])
    
    # Generate Pearson symbol
    if spg_type['number'] <= 2:
        crystalclass = 'a'
    elif spg_type['number'] <= 15:
        crystalclass = 'm'
    elif spg_type['number'] <= 74:
        crystalclass = 'o'
    elif spg_type['number'] <= 142:
        crystalclass = 't'
    elif spg_type['number'] <= 194:
        crystalclass = 'h'
    else:
        crystalclass = 'c'
    
    latticetype = spg_type['international'][0]
    if latticetype in ['A', 'B']:
        latticetype = 'C'
    
    pearson = crystalclass + latticetype + str(natoms)
    
    # Generate Wyckoff fingerprint
    fingerprint_dict = {} 
    usites, uindices = np.unique(sym_data['equivalent_atoms'], return_index=True)
    for usite, uindex in zip(usites, uindices):
        atype = ucell.atoms.atype[uindex]
        wykoff = sym_data['wyckoffs'][uindex]
        if atype not in fingerprint_dict:
            fingerprint_dict[atype] = [wykoff]
        else:
            fingerprint_dict[atype].append(wykoff)
    fingerprint = []
    for atype in sorted(fingerprint_dict.keys()):
        fingerprint.append(''.join(sorted(fingerprint_dict[atype])))
    fingerprint = ' '.join(fingerprint)

    # Return results
    results_dict = spg_type
    results_dict['ucell'] = ucell
    results_dict['hall_number'] = sym_data['hall_number']
    results_dict['wyckoffs'] = sym_data['wyckoffs']
    results_dict['equivalent_atoms'] = sym_data['equivalent_atoms']
    results_dict['pearson'] = pearson
    results_dict['wyckoff_fingerprint'] = fingerprint
    
    return results_dict