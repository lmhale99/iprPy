import os
from DataModelDict import DataModelDict
import uuid
import shutil
import sys
from iprpy_test.prepare import *
import atomman.lammps as lmp

def main(args):
    sim_dir = os.getcwd()
    lammps_exe = None
    pot_list = []
    pot_dir_list = []
    proto_list = []
    define_list = {}

    with open(args[0]) as prepare_in:
        
        #go through input lines in order
        for line in prepare_in:
            terms = line.split()
            
            #ignore blank and comment lines
            if len(terms) > 0 and terms[0][0] != '#':
                
                if terms[0] == 'lammps_exe':
                    lammps_exe = set_lammps_exe(terms[1:])
                
                elif terms[0] == 'simulation_dir':
                    sim_dir = set_simulation_dir(terms[1:])
                    
                elif terms[0] == 'potential':
                    pot_list, pot_dir_list = set_potential(terms[1:], pot_list, pot_dir_list, define_list)
                    
                elif terms[0] == 'prototype':
                    proto_list = set_prototype(terms[1:], proto_list)
                    
                elif terms[0] == 'define_list':
                    define_list = set_define_list(terms[1:], define_list)
                
                elif terms[0] == 'calc_struct_static':
                    assert lammps_exe is not None, 'lammps_exe not specified'
                    assert len(pot_list) > 0, 'no potentials set'
                    assert len(proto_list) > 0, 'no prototypes set'
        


    print 'lammps_exe = ', lammps_exe
    print 'simulation_dir = ', sim_dir
    print 'potential:'
    for i in xrange(len(pot_list)):
        print pot_list[i]
        print pot_dir_list[i]
        print
        
    print 'prototype:'
    for proto in proto_list:
        print proto
    
                            
def set_lammps_exe(terms):
    """Interpret lammps_exe arguments."""
    try:
        assert len(terms) == 1
        lammps_exe = os.path.abspath(os.path.realpath(terms[0]))
        assert os.path.isfile(lammps_exe)
    except:
        raise ValueError('lammps_exe argument not accessible file')
    return lammps_exe

def set_define_list(terms, define_list):
    """Interpret define_list arguments."""
    try:
        assert len(terms) >= 3 and terms[1] == '='
        define_list[terms[0]] = []
    except:
        raise ValueError('invalid define_list arguments')
        
    for term in terms[2:]:
        define_list[terms[0]].append(term)
        
    return define_list
        
def set_simulation_dir(terms):
    """Interpret simulation_dir arguments."""
    try:
        assert len(terms) == 1
        sim_dir = os.path.abspath(os.path.realpath(terms[0]))
        assert os.path.isdir(sim_dir)
    except:
        raise ValueError('simulation_dir argument not accessible directory')
    return sim_dir
    
def set_potential(terms, pot_list, pot_dir_list, define_list):
    """Interpret potential arguments."""
    new_list = []
    if len(terms) == 0:
        raise ValueError('invalid potential argument')
    elif terms[0] == 'add':
        for i in xrange(1, len(terms)):
            if terms[i] == 'with':
                break
            
            try:
                path = os.path.abspath(os.path.realpath(terms[i]))
                if os.path.isfile(path):
                    new_list.append(path)
                elif os.path.isdir(path):
                    flist = os.listdir(path)
                    for fname in flist:
                        fpath = os.path.abspath(os.path.realpath(os.path.join(path, fname)))
                        if os.path.isfile(fpath):
                            new_list.append(fpath)
            except:
                raise ValueError('Error accessing potential files/directories')
                
        if terms[i] == 'with':
            elterms = terms[i+1:]

            elements = []
                
            for el in elterms:

                if el in define_list:
                    elements.extend(define_list[el])
                else:
                    elements.append(el)
       
            with_list = []
            for pot in new_list:
                with open(pot) as f:
                    potential = lmp.Potential(f)
                has_el = False
                for el in potential.elements():
                    if el in elements:
                        has_el = True
                        break
                if has_el:
                    with_list.append(pot)
            
            new_list = with_list
                
        for pot in new_list:
            if pot not in pot_list:
                with open(pot) as f:
                    potential = lmp.Potential(f)
                pot_list.append(pot)
                pot_dir = os.path.join(os.path.dirname(pot), potential.id)
                if not os.path.isdir(pot_dir):
                    pot_dir = ''                
                pot_dir_list.append(pot_dir)
                
    
    elif len(terms) == 1 and terms[0] == 'clear':
        pot_list = []
        pot_dir_list = []
    
    else:
        raise ValueError('invalid potential argument')
    
    return pot_list, pot_dir_list

def set_prototype(terms, proto_list):
    """Interpret prototype arguments."""
    new_list = []
    if len(terms) == 0:
        raise ValueError('invalid prototype argument')
    
    elif terms[0] == 'add':
        for i in xrange(1, len(terms)):
            try:
                path = os.path.abspath(os.path.realpath(terms[i]))
                if os.path.isfile(path):
                    new_list.append(path)
                elif os.path.isdir(path):
                    flist = os.listdir(path)
                    for fname in flist:
                        fpath = os.path.abspath(os.path.realpath(os.path.join(path, fname)))
                        if os.path.isfile(fpath):
                            new_list.append(fpath)
            except:
                raise ValueError('Error accessing prototype files/directories')
                
        for proto in new_list:
            if proto not in proto_list:
                proto_list.append(proto)
        
        return proto_list

    elif len(terms) == 1 and terms[0] == 'clear':
        proto_list = []
    
    else:
        raise ValueError('invalid prototype argument') 

    return proto_list
    
if __name__ == '__main__':
    main(sys.argv[1:])