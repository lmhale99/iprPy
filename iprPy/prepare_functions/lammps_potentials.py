import os
import atomman.lammps as lmp
import sys

from iprPy.tools import list_build

def prepare(terms, variable):
    """Generate potential_file and potential_dir terms."""
    
    #check on existing potential_file and potential_dir terms
    potential_file = variable.aslist('potential_file')
    potential_dir = variable.aslist('potential_dir')
    assert len(potential_file) == len(potential_dir), 'potential_file and potential_dir must be of the same length!'
    for i in xrange(len(potential_file)):
        potential_file[i] = os.path.realpath(potential_file[i])
        potential_dir[i] = os.path.realpath(potential_dir[i])
    
    #break terms apart using keywords 'name' and 'with'
    try: i_with = terms.index('with')
    except: i_with = len(terms)
    try: i_name = terms.index('name')
    except: i_name = len(terms)
    
    if i_name < i_with:
        pot_paths = ' '.join(terms[:i_name])
        pot_names = terms[i_name+1:i_with]
        with_elems = terms[i_with+1:]
    else:
        pot_paths = ' '.join(terms[:i_with])
        with_elems = terms[i_with+1:i_name]
        pot_names = terms[i_name+1:]
    assert 'with' not in pot_names and 'with' not in with_elems, 'with can only appear once in prepare lammps_potentials'     
    assert 'name' not in pot_names and 'name' not in with_elems, 'name can only appear once in prepare lammps_potentials'  
    
    #replace terms with defined variables
    if pot_paths in variable:
        pot_paths = variable.aslist(pot_paths)
    else:
        pot_paths = [pot_paths]
    
    pot_names = list_build(pot_names, variable)
    with_elems = list_build(with_elems, variable)
    
    #generate list of all potential names from pot_paths if none were given
    if len(pot_names) == 0:
        for pot_path in pot_paths:
            for fname in os.listdir(pot_path): 
                name, ext = os.path.splitext(fname)
                if ext in ['.json', '.xml'] and name not in pot_names:
                    pot_names.append(name)    
    
    #iterate through pot_paths, pot_names and with_elems to build 
    #potential_file and potential_dir variable lists
    for pot_path in pot_paths:
        for pot_name in pot_names:
            p_dir = os.path.realpath(os.path.join(pot_path, pot_name))
            if os.path.isdir(p_dir) and not is_path_in_list(p_dir, potential_dir):
                try:
                    with open(p_dir+'.xml') as f:
                        pot = lmp.Potential(f)
                        p_file = p_dir+'.xml'
                except:
                    try:
                        with open(p_dir+'.json') as f:
                            pot = lmp.Potential(f)
                            p_file = p_dir+'.json'
                    except:
                        p_file = None
                if p_file is not None:
                    if len(with_elems) == 0:
                        potential_file.append(p_file)
                        potential_dir.append(p_dir)
                    else:
                        elements = pot.elements()
                        for with_elem in with_elems:
                            if with_elem in elements:
                                potential_file.append(p_file)
                                potential_dir.append(p_dir)
                                break
    variable['potential_file'] = potential_file
    variable['potential_dir'] = potential_dir




def is_path_in_list(path, p_list):
    for p in p_list:
        if os.path.normcase(path) == os.path.normcase(p):
            return True
    return False
    
def process(*args, **kwargs):
    pass