#!/usr/bin/env python2.7

#Standard python libraries
import os
import sys

#External python libraries
import atomman
import atomman.lammps as lmp
from DataModelDict import DataModelDict

#Internal python libraries
import prepare


def main(args):
    lammps_exe = None
    potentials = []
    potential_directories = []
    crystals = []
    elements = []
    xml_library_dir = None
    iprPy_dir = os.getcwd()
    u_length = 'angstrom'
    u_press = 'GPa'
    u_energy = 'eV'
    u_time = 'ns'
    
    defined_element = {'*': ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Uut', 'Fl', 'Uup', 'Lv', 'Uus', 'Uuo', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr']}

    with open(args[0]) as prepare_in:
        
        #go through input lines in order
        for line in prepare_in:
            #print line
            terms = line.split()
            
            #ignore blank and comment lines
            if len(terms) > 0 and terms[0][0] != '#':
                
                if terms[0] == 'lammps_exe':
                    lammps_exe = set_lammps_exe(terms[1:])
                
                elif terms[0] == 'simulation_dir':
                    set_simulation_dir(terms[1:])
                    
                elif terms[0] == 'xml_library_dir':
                    xml_library_dir = set_xml_library_dir(terms[1:])
                    
                elif terms[0] == 'iprPy_dir':
                    iprPy_dir = set_iprPy_dir(terms[1:])
                
                elif terms[0] == 'define_element_list':
                    defined_element = set_define_element_list(terms[1:], defined_element)
                
                elif terms[0] == 'potential':
                    potentials, potential_directories = set_potential(terms[1:], potentials, potential_directories, defined_element)
                    
                elif terms[0] == 'crystal':
                    crystals, elements  = set_crystal(terms[1:], crystals, elements)
                    
                elif terms[0] == 'calc_structure_static':
                    prepare.structure_static(terms[1:],
                                             lammps_exe, xml_library_dir, iprPy_dir,
                                             defined_element, 
                                             potentials, potential_directories,
                                             crystals, elements,
                                             u_length, u_press, u_energy)
    
                            
def set_lammps_exe(terms):
    """Interpret lammps_exe arguments."""
    lammps_exe = ' '.join(terms)
    try:
        lammps_exe = os.path.abspath(os.path.realpath(lammps_exe))
        assert os.path.isfile(lammps_exe)
    except:
        raise ValueError('lammps_exe argument not accessible file')
    return lammps_exe

def set_simulation_dir(terms):
    """Interpret simulation_dir arguments."""
    dir = ' '.join(terms)
    try:
        os.chdir(dir)        
    except:
        os.makedirs(dir)
        os.chdir(dir)
    if not os.path.isdir('to_run'):    
        os.mkdir('to_run')
    if not os.path.isdir('has_ran'):    
        os.mkdir('has_ran')
    
def set_xml_library_dir(terms):
    """Interpret xml_library_dir arguments."""
    xml_library_dir = ' '.join(terms)
    try:
        xml_library_dir = os.path.abspath(os.path.realpath(xml_library_dir))
        assert os.path.isdir(xml_library_dir)
    except:
        raise ValueError('xml_library_dir argument not accessible directory')
    return xml_library_dir
    
def set_iprPy_dir(terms):
    """Interpret iprPy_dir arguments."""
    iprPy_dir = ' '.join(terms)
    try:
        iprPy_dir = os.path.abspath(os.path.realpath(iprPy_dir))
        assert os.path.isdir(iprPy_dir)
    except:
        raise ValueError('iprPy_dir argument not accessible directory')
    return iprPy_dir    


def set_element_list(terms, defined_element):
    """Interpret define_element_list arguments."""
    try:
        assert len(terms) >= 3 and terms[1] == '='
        defined_element[terms[0]] = []
    except:
        raise ValueError('invalid define_element_list arguments')
        
    for term in terms[2:]:
        defined_element[terms[0]].append(term)
        
    return defined_element
    
def set_potential(terms, potentials, potential_directories, defined_element):
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

                if el in defined_element:
                    elements.extend(defined_element[el])
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
            if pot not in potentials:
                with open(pot) as f:
                    potential = lmp.Potential(f)
                potentials.append(pot)
                pot_dir = os.path.join(os.path.dirname(pot), potential.id)
                if not os.path.isdir(pot_dir):
                    pot_dir = ''                
                potential_directories.append(pot_dir)
                
    
    elif len(terms) == 1 and terms[0] == 'clear':
        potentials = []
        potential_directories = []
    
    else:
        raise ValueError('invalid potential argument')
    
    return potentials, potential_directories

def set_crystal(terms, crystals, elements):
    """Interpret crystal arguments."""
    
    new_list = []    
    
    if len(terms) >= 3 and terms[0] == 'add':
        if terms[1] == 'prototypes':
            try:
                i = terms.index('only')
            except:
                i = len(terms)
            try:
                path = os.path.abspath(os.path.realpath(' '.join(terms[2:i])))
                assert os.path.isdir(path)
            except:
                raise ValueError(path + ' is not an accessible directory')
            names = terms[i+1:]
            
            for fname in os.listdir(path):
                try:
                    crystal = os.path.join(path, fname)
                    with open(crystal) as f:
                        model = DataModelDict(f)
                        natypes = atomman.models.crystal(model)[0].natypes
                        model.find('crystal-prototype')
                except:
                    continue
    
                if len(names) > 0:
                    print names
                    match = False
                    for name in names:
                        print name
                        if name in model['atom-system']['identifier'].values():
                            match = True
                            break
                    if not match:
                        continue
                
                if crystal in crystals:
                    elements[crystals.index(crystal)] = ['*' for i in xrange(natypes)]
                else:
                    crystals.append(crystal)
                    elements.append(['*' for i in xrange(natypes)])

        elif terms[1] == 'prototype':
            try:
                i = terms.index('elements')
            except:
                i = len(terms)
            try:
                path = os.path.abspath(os.path.realpath(' '.join(terms[2:i])))
                assert os.path.isfile(path)
            except:
                raise ValueError(path + ' is not an accessible file')
            element = terms[i+1:]
            
            try:
                crystal = path
                with open(crystal) as f:
                    model = DataModelDict(f)
                    natypes = atomman.models.crystal(model)[0].natypes
                    model.find('crystal-prototype')
            except:
                raise ValueError(path + ' is not a crystal prototype file')
                
            if len(element) == 0:
                element = ['*' for i in xrange(natypes)]
            elif len(element) != natypes:
                raise ValueError('number of elements (%i) and number of atom types (%i) do not match' % (len(element), natypes))
                    
            if crystal in crystals:
                elements[crystals.index(crystal)] = element
            else:
                crystals.append(crystal)
                elements.append(element)
        
        elif terms[1] == 'cifs':
            try:
                i = terms.index('only')
            except:
                i = len(terms)
            try:
                path = os.path.abspath(os.path.realpath(' '.join(terms[2:i])))
                assert os.path.isdir(path)
            except:
                raise ValueError(path + ' is not an accessible directory')
            names = terms[i+1:]
            
            for fname in os.listdir(path):
                if len(names) > 0:
                    if fname[:-4] not in names:
                        continue
                
                try:
                    crystal = os.path.join(path, fname)
                    with open(crystal) as f:
                        element = atomman.models.cif_cell(f)[1]
                    if not isinstance(element, list): [element]
                except:
                    continue
                
                if crystal in crystals:
                    elements[crystals.index(crystal)] = element
                else:
                    crystals.append(crystal)
                    elements.append(element)
        
        elif terms[1] == 'cif':
            try:
                i = terms.index('elements')
            except:
                i = len(terms)
            try:
                path = os.path.abspath(os.path.realpath(' '.join(terms[2:i])))
                assert os.path.isfile(path)
            except:
                raise ValueError(path + ' is not an accessible file')
            
            if True:
                crystal = path
                with open(crystal) as f:
                    element = atomman.models.cif_cell(f)[1]
                    natypes = len(element)
            else:
                raise ValueError(path + ' is not a cif file')
            
            if len(terms[i+1:]) > 0:
                element = terms[i+1:]

            if len(element) != natypes:
                raise ValueError('number of elements (%i) and number of atom types (%i) do not match' % (len(element), natypes))
                    
            if crystal in crystals:
                elements[crystals.index(crystal)] = element
            else:
                crystals.append(crystal)
                elements.append(element)
        else:
            raise ValueError('invalid crystal argument') 
        

    elif len(terms) == 1 and terms[0] == 'clear':
        proto_list = []
    
    else:
        raise ValueError('invalid crystal argument') 

    return crystals, elements


    
    
    
    
if __name__ == '__main__':
    main(sys.argv[1:])