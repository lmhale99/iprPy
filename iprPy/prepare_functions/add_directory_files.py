import os
import glob

from iprPy.tools import list_build

def prepare(t,v):
    """
    Function for adding all file paths within a directory to a variable name.
    Requires exactly two terms:
    - name of the variable to add the file paths to.
    - directory or variable listing directories containing the files to be added.
    """

    assert len(t) >= 2
    name = t[0]
    dirs = list_build(' '.join(t[1:]), v)
    
    for dir in dirs:
        for fname in glob.iglob(os.path.join(dir, '*')):
            fname = os.path.realpath(fname)
            if os.path.isfile(fname):
                if not is_path_in_list(fname, v.aslist(name)):
                    v.append(name, fname)
                
def is_path_in_list(path, p_list):
    for p in p_list:
        if os.path.normcase(os.path.realpath(path)) == os.path.normcase(os.path.realpath(p)):
            return True
    return False 