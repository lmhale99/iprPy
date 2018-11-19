# Standard Python libraries
from __future__ import (print_function, division, absolute_import,
                        unicode_literals)
import os
import glob

import atomman as am

from .. import rootdir

def get_mp_structures(elements, api_key=None, lib_directory=None):
    """
    Accesses the Materials Project and downloads all structures for a list of
    elements as poscar files.
    
    Parameters
    ----------
    elements : list
        A list of element symbols.
    api_key : str, optional
        The user's Materials Project API key. If not given, will use "MAPI_KEY"
        environment variable
    lib_directory : str
        Path to the lib_directory to save the poscar files to.  Default uses
        the iprPy library/dft_structures directory.
    """
    # Function-specific imports
    import pymatgen as pmg
    from pymatgen.ext.matproj import MPRester
    
    # Define subset generator
    def subsets(fullset):
        for i, item in enumerate(fullset):
            yield [item]
            if len(fullset) > 1:
                for subset in subsets(fullset[i+1:]):
                    yield [item] + subset
    
    # Handle lib_directory
    if lib_directory is None:
        lib_directory = os.path.join(os.path.dirname(rootdir), 'library', 'ref')
    lib_directory = os.path.abspath(lib_directory)
    
    elements.sort()
    
    # Open connection to Materials Project
    with MPRester(api_key) as m:
        
        # Loop over subsets of elements
        for subelements in subsets(elements):
            
            # Set comp_directory
            elements_string = '-'.join(subelements)
            comp_directory = os.path.join(lib_directory, elements_string)
            if not os.path.isdir(comp_directory):
                os.makedirs(comp_directory)
            
            # Build list of downloaded entries
            have = []
            for fname in glob.iglob(os.path.join(comp_directory, 'mp-*.poscar')):
                have.append(os.path.splitext(os.path.basename(fname))[0])
            
            # Query MP for all entries corresponding to the elements
            entries = m.query({"elements": subelements}, ["material_id"])
            
            # Add entries to the list if not there
            missing = []
            for entry in entries:
                if entry['material_id'] not in have and entry['material_id'] not in missing:
                    missing.append(entry['material_id'])
            
            # Download missing entries
            try:
                entries = m.query({"material_id": {"$in": missing}}, ['material_id', 'cif'])
            except:
                pass
            else:
                # Convert cif to poscar and save
                for entry in entries:
                    struct = pmg.Structure.from_str(entry['cif'], fmt='cif')
                    struct = pmg.symmetry.analyzer.SpacegroupAnalyzer(struct).get_conventional_standard_structure()
                    system = am.load('pymatgen_Structure', struct)
                    system = system.normalize()
                    structure_file = os.path.join(comp_directory, entry['material_id']+'.poscar')
                    system.dump('poscar', f=structure_file)
                    print('Added', entry['material_id'])