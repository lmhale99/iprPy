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

def get_oqmd_structures(elements, lib_directory=None):
    """
    Accesses the Materials Project and downloads all structures for a list of
    elements as poscar files.
    
    Parameters
    ----------
    elements : list
        A list of element symbols.
    lib_directory : str
        Path to the lib_directory to save the poscar files to.  Default uses
        the iprPy library/dft_structures directory.
    """
    # Function-specific imports
    import requests
    
    sourcename = "Open Quantum Materials Database"
    sourcelink = "http://oqmd.org/"

    # Handle lib_directory
    if lib_directory is None:
        lib_directory = Path(libdir, 'reference_crystal')
    if not lib_directory.is_dir():
        lib_directory.mkdir()
    
    elements.sort()

    # Build list of downloaded entries
    have = []
    for fname in lib_directory.glob('*.json'):
        have.append(fname.stem)
    
    # Build list of missing OQMD entries
    elements_string = '-'.join(elements)
    
    composition_r = requests.get('http://oqmd.org/materials/composition/' + elements_string)
    composition_html = composition_r.text
    
    missing = []
    count = 0
    while True:
        count += 1
        try:
            start = composition_html.index('href="/materials/entry/') + len('href="/materials/entry/')
        except:
            break
        else:
            end = start + composition_html[start:].index('">')
            entry_number = composition_html[start:end]
            composition_html = composition_html[end+2:]
            entry_id = 'oqmd-'+entry_number
            if entry_id not in have and entry_id not in missing:
                missing.append(entry_id)
        if count > 100:
            raise ValueError('Loop likely infinite')
    
    # Download missing entries
    for entry_id in missing:
        entry_number = entry_id.replace('oqmd-', '')
        entry_r = requests.get('http://oqmd.org/materials/entry/' + entry_number)
        entry_html = entry_r.text
        
        start = entry_html.index('href="/materials/structure/') + len('href="/materials/structure/')
        end = start + entry_html[start:].index('">')
        structure_number = entry_html[start:end]
        
        try:
            structure_url = 'http://oqmd.org/materials/export/conventional/poscar/' + structure_number
            structure_r = requests.get(structure_url)
            structure_r.raise_for_status()
        except:
            try:
                structure_url = 'http://oqmd.org/materials/export/primitive/poscar/' + structure_number
                structure_r = requests.get(structure_url)
                structure_r.raise_for_status()
            except:
                continue
        
        # Save as model
        ucell = am.load('poscar', structure_r.text).normalize()
        model = build_reference_crystal_model(entry_id, ucell, sourcename, sourcelink)
        with open(Path(lib_directory, entry_id+'.json'), 'w') as f:
            model.json(fp=f, indent=4)
        print('Added', entry_id)