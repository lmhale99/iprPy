import atomman as am
import atomman.lammps as lmp
from copy import deepcopy
import os

def gen_element_pairings(defined_element, potentials, potential_directories, crystals, crystal_elements):
    """iterate over each unique potential-crystal-symbol set for the listed conditions."""    

    #replace defined element names with their respective lists.
    crystal_elements = deepcopy(crystal_elements)
    for i in xrange(len(crystal_elements)):
        for j in xrange(len(crystal_elements[i])):
            if crystal_elements[i][j] in defined_element:
                crystal_elements[i][j] = defined_element[crystal_elements[i][j]]
            else:
                crystal_elements[i][j] = [crystal_elements[i][j]]
    
    #iterate over all potentials
    for pot, pot_dir in zip(potentials, potential_directories):
        with open(pot) as f:
            potential = lmp.Potential(f)
        pot_symbols = potential.symbols
    
        #iterate over all crystals
        for crystal, c_e_lists in zip(crystals, crystal_elements):
            #generate every unique combo for 
            for el_array in iterbox(len(pot_symbols), len(c_e_lists)):
                symbols = []
                for el_index in el_array:
                    symbols.append(pot_symbols[el_index])
                match = True
                
                #construct symbols list and check that the elements match with the crystal's elements
                for symbol, c_e_list in zip(symbols, c_e_lists):

                    if potential.elements(symbol)[0] not in c_e_list:
                        match = False
                        break
                    
                if match:
                    yield pot, pot_dir, symbols, crystal

def iterbox(a, b):
    """Allows for dynamic iteration over all arrays of length b where each term is in range 0-a"""
    for i in xrange(a):    
        if b > 1:
            for j in iterbox(a,b-1):
                yield [i] + j    
        elif b == 1:
            yield [i] 
            