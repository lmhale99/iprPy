import os
import glob

from iprPy.tools import term_extractor

def description():
    """Returns a description for the prepare_function."""
    return "The add_directory_files prepare_function adds all file paths in the directories listed in 'file_directory' to a variable name 'v_name'."
    
def keywords():
    """Return the list of keywords used by this prepare_function that are searched for from the inline terms and pre-defined variables."""
    return ['v_name', 'file_directory']

def prepare(terms, variables):
    """
    Function for adding all file paths within a directory or list of directories to a variable name.
    """

    v = term_extractor(terms, variables, keywords())
    
    key = v.get('v_name', 'file')
    assert not isinstance(key, list), 'v_name must be single-valued'
    dirs = v.aslist('file_directory')
    assert len(dirs) > 0, 'No values found for file_directory'
    
    for dir in dirs:

        for fname in glob.iglob(os.path.join(dir, '*')):
            fname = os.path.realpath(fname)

            if os.path.isfile(fname):
                if not is_path_in_list(fname, variables.aslist(key)):
                    variables.append(key, fname)
                
def is_path_in_list(path, p_list):
    for p in p_list:
        if os.path.normcase(os.path.realpath(path)) == os.path.normcase(os.path.realpath(p)):
            return True
    return False 