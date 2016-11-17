import os
import atomman.lammps as lmp
from DataModelDict import DataModelDict as DM

from . import get_files_in_directory
from ..tools import as_list
    
def read_lammps_potentials(directory, element=None, name=None):
    """
    Read in LAMMPS potential data model files.
    
    Arguments:
    directory -- path or list of paths to directories containing LAMMPS 
                 potential data models.
                 
    Keyword Arguments:
    element -- element tag or list of element tags. If given, only potentials 
               in directory that have at least one matching element will be 
               included.
    name -- name or list of names. If given, only potentials in directory with
            id's given by name will be included.    
    """
    
    potentials = []
    
    #Loop over all data model files in the potential directory
    for file in get_files_in_directory(directory, ext=['.json', '.xml']):
        
        #Load potential
        try:
            with open(file) as f:
                model = DM(f)
            potential = lmp.Potential(model)
        except:
            continue

        #Check if potential id is in name
        if name is not None and potential.id not in as_list(name):
            continue
            
        #Check if potential has an element in element    
        if element is not None:
            match = False
            for el in potential.elements():
                if el in as_list(element):
                    match = True
                    break
            if not match:
                continue
        
        #Check if there is a corresponding potential directory
        dir = os.path.splitext(file)[0]
        if not os.path.isdir(dir):
            dir = ''
            
        potentials.append({'model':model, 'potential':potential, 'file':file, 'dir':dir})
        
    return potentials
