import os
import atomman as am
from DataModelDict import DataModelDict as DM

from . import as_list, get_files_in_directory
    
def read_prototypes(directory, natypes=None, name=None):
    """
    Read in LAMMPS potential data model files.
    
    Arguments:
    directory -- path or list of paths to directories containing prototype 
                 data models.
                 
    Keyword Arguments:
    natypes -- number(s) of atom types to limit prototype inclusion.
    name -- name or list of names. If given, only prototypes with file names or
            identifiers consistent with values in name will be included.
    """
    prototypes = []
    
    #Loop over all data model files in the prototype directory
    for file in get_files_in_directory(directory, ext=['.json', '.xml']):
        prototype_name = os.path.splitext(os.path.basename(file))[0]
        
        #Load prototype
        if True:
            with open(file) as f:
                model = DM(f)
            ids = model['crystal-prototype']['identifier']
            prototype = am.load('system_model', model)[0]
        else:
            continue
        
        #Check that prototype is in name
        if name is not None and prototype_name not in as_list(name):
            match = False
            for name in ids.values():
                if name in as_list(name):
                    match = True
                    break
            if not match:
                continue
        
        #Check that prototype has the right number of natypes
        if natypes is not None and prototype.natypes not in as_list(natypes):
            continue
        
        prototypes.append({'model':model, 'prototype':prototype, 'file':file})
        
    return prototypes