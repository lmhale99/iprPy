# Standard Python libraries
from pathlib import Path
import uuid

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am

# iprPy imports
from .. import libdir

def build_reference_crystal_model(name, ucell, sourcename, sourcelink):
    """Generates a reference_crystal data model"""
    model = DM()
    model['reference-crystal'] = DM()
    model['reference-crystal']['key'] = str(uuid.uuid4())
    model['reference-crystal']['id'] = name
    
    model['reference-crystal']['source'] = DM()
    model['reference-crystal']['source']['name'] = sourcename
    model['reference-crystal']['source']['link'] = sourcelink
    
    model['reference-crystal']['atomic-system'] = ucell.model()['atomic-system']

    return model

# Define subset generator
def subsets(fullset):
    """Yields element combination subsets"""
    for i, item in enumerate(fullset):
        yield [item]
        if len(fullset) > 1:
            for subset in subsets(fullset[i+1:]):
                yield [item] + subset

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
        the iprPy library/reference_crystal directory.
    """
    # Function-specific imports
    import pymatgen as pmg
    from pymatgen.ext.matproj import MPRester
    
    # Set source name and link
    sourcename = "Materials Project"
    sourcelink = "https://materialsproject.org/"

    # Handle lib_directory
    if lib_directory is None:
        lib_directory = Path(libdir, 'reference_crystal')
    
    elements.sort()

    # Build list of downloaded entries
    have = []
    for fname in lib_directory.glob('*.json'):
        have.append(fname.stem)
    
    # Open connection to Materials Project
    with MPRester(api_key) as m:
        
        # Loop over subsets of elements
        for subelements in subsets(elements):
            
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
                # Convert cif to model and save
                for entry in entries:
                    name = entry['material_id']
                    struct = pmg.Structure.from_str(entry['cif'], fmt='cif')
                    struct = pmg.symmetry.analyzer.SpacegroupAnalyzer(struct).get_conventional_standard_structure()
                    ucell = am.load('pymatgen_Structure', struct).normalize()
                    model = build_reference_crystal_model(name, ucell, sourcename, sourcelink)
                    with open(Path(libdir, name+'.json'), 'w') as f:
                        model.json(fp=f, indent=4)
                    print('Added', entry['material_id'])