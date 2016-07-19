import os
import atomman.lammps as lmp
import sys

from iprPy.tools import term_extractor
import add_directory_files

def description():
    """Returns a description for the prepare_function."""
    return "The lammps_potentials prepare_function adds matching values to the 'potential_file' and 'potential_dir' variables. The directories given by 'potential_path' should contain LAMMPS-potential data model (JSON/XML) files and sub-directories with matching names containing the potential's artifacts (eg. setfl file). The optional variables 'potential_name' and 'elements' limits the search for only potentials with the given names, and/or potentials containing at least one of the listed elements."
    
def keywords():
    """Return the list of keywords used by this prepare_function that are searched for from the inline terms and pre-defined variables."""
    return ['potential_path', 'potential_name', 'elements']


def prepare(terms, variables):
    """Add to 'potential_file' and 'potential_dir' variables from the given 'file_directory'. The optional variables 'potential_name' and 'elements' limits the search for only potentials with the given names, and/or potentials containing at least one of the listed elements."""
    
    #check on existing potential_file and potential_dir terms
    assert len(variables.aslist('potential_file')) == len(variables.aslist('potential_dir')), 'potential_file and potential_dir must be of the same length!'
    
    v = term_extractor(terms, variables, keywords())
    
    #Generate list of files within file_directory
    add_directory_files.prepare(['file_directory', 'potential_path', 'v_name', 'all_files'], v)
    
    #iterate through the files
    for fname in v.iteraslist('all_files'):
        pot_name, ext = os.path.splitext(os.path.basename(fname))
        
        #Check if the file is a data model
        if ext in ['.json', '.xml']:
            
            #If potential_name is given, check that pot_name is in it
            if 'potential_name' in v:
                if pot_name not in v.aslist('potential_name'):
                    continue
            
            #Check that the file is a LAMMPS-potential data model
            try:
                with open(fname) as f:
                    pot = lmp.Potential(f)
            except:
                continue
                
            #If elements is given, check that the potential contains at least one
            if 'elements' in v:
                match = False
                for el in pot.elements():
                    if el in v.aslist('elements'):
                        match = True
                        break
                if not match:
                    continue
                    
            #Add to potential_file and potential directory if not already there
            if not is_path_in_list(fname, variables.aslist('potential_file')):
                dname = os.path.splitext(fname)[0]
                if not os.path.isdir(dname):
                    dname = ''
                variables.append('potential_file', fname)
                variables.append('potential_dir',  dname)

def is_path_in_list(path, p_list):
    for p in p_list:
        if os.path.normcase(os.path.realpath(path)) == os.path.normcase(os.path.realpath(p)):
            return True
    return False 
    
