from collections import OrderedDict
import numpy as np
import os
import sys
from atomman import Atom, Box, System

class Cif:
    def __init__(self, filename=None):
        self.alldict = OrderedDict()
        if filename is not None:
            self.load(filename)
                
    def load(self, filename):
        terms = self.__parse(filename)
        self.__list_to_dict(terms)
                
    def __parse(self, filename):
    #Reads in cif file and parses it into a proper term list
        with open(filename, "r") as fin: 
            lines = fin.readlines()
            terms = []
            
            #Strip away comments
            i = 0
            while i < len(lines):
                #strip comments
                if '#' in lines[i][0]:
                    hash_index = lines[i].index('#')
                    lines[i] = lines[i][:hash_index]
                if len(lines[i]) == 0:
                    i += 1
                
                #Handle semicolondeliminters 
                elif lines[i][0] == ';':
                    term = lines[i][1:]
                    i += 1
                    while lines[i][0] != ';':
                        term += lines[i]
                        i += 1
                        if i == len(lines):
                            raise ValueError('Bad file!')
                    terms.append(term.strip())
                    i += 1
                    
                else:
                    words = lines[i].split()
            
                    #Separate out terms using whitespace
                    j = 0
                    while j < len(words):
                        #Handle double quotes
                        if words[j][0] == '"':
                            words[j] = words[j][1:]
                            term = ''                   
                            while True:
                                term += words[j] + ' '
                                if words[j][-1:] == '"':
                                    term = term[:-2]
                                    break
                                j += 1
                                assert j < len(words), 'Bad file!'
                            term = '"' + term + '"'
                            terms.append(term)
                            
                        #Handle single quotes
                        elif words[j][0] == "'":
                            words[j] = words[j][1:]
                            term = ''                   
                            while True:
                                term += words[j] + ' '
                                if words[j][-1:] == "'":
                                    term = term[:-2]
                                    break
                                j += 1
                                assert j < len(words), 'Bad file!' + str(words)
                            term = "'" + term + "'"
                            terms.append(term)
                        else:
                            terms.append(words[j])
                        j += 1
                    i += 1

        return terms
                   
    def __list_to_dict(self, terms):
    #Converts a list of terms into a dictionary
        data = 'data_none'
        alldict = OrderedDict()

        i = 0
        while i < len(terms):
            
            #Single key-value pairs
            if terms[i][0] == '_':
                try:
                    alldict[data][terms[i]] = terms[i+1]
                except:
                    alldict[data] = OrderedDict()
                    alldict[data][terms[i]] = terms[i+1]
                i += 2
            
            #Loops
            elif terms[i] == 'loop_':
                i += 1
                if i == len(terms):
                    raise ValueError('Bad file!')
                key_list = []
                
                #Retrieve key names
                while terms[i][0] == '_':
                    key_list.append(terms[i])
                    try:
                        alldict[data][terms[i]] = []
                    except:
                        alldict[data] = OrderedDict()
                        alldict[data][terms[i]] = []
                    i += 1
                    assert i < len(terms), 'Bad file!'
                
                #Save values to key names
                j = 0        
                while i < len(terms) and terms[i] != 'loop_':
                    if len(terms[i]) > 0 and terms[i][0] == '_':
                        break 
                    if len(terms[i]) > 5 and terms[i][:5] == 'data_':
                        break
                    if len(terms[i]) > 1 and terms[i][0] == '"' and terms[i][-1] == '"':
                        terms[i] = terms[i][1:-1]
                    elif len(terms[i]) > 1 and terms[i][0] == "'" and terms[i][-1] == "'":
                        terms[i] = terms[i][1:-1]    
                    alldict[data][key_list[j]].append(terms[i])
                    i += 1
                    j += 1
                    if j == len(key_list):
                        j = 0
                assert j == 0, 'Bad file! ' + str(key_list)
            
            #Change data block
            elif terms[i][:5] == 'data_':
                data = terms[i]
                i += 1
            
            else:
                print 'Unknown term', terms[i]
                i += 1
        keys = alldict.keys()
        self.alldict = alldict[keys[0]]
    
    def __calc(self, symm, site):
        pos = np.empty(3)
        i = 0
        for i in xrange(3):
            terms = []
            c = 0
            while c < len(symm[i]):
                if symm[i][c] == 'x':
                    terms.append(site[0])
                    c += 1
                elif symm[i][c] == 'y':
                    terms.append(site[1])
                    c += 1
                elif symm[i][c] == 'z':
                    terms.append(site[2])
                    c += 1
                elif symm[i][c] == ' ':
                    c += 1
                else:
                    terms.append(symm[i][c])
                    if symm[i][c].isdigit() or symm[i][c] == '.':
                        c += 1
                        while c < len(symm[i]) and (symm[i][c].isdigit() or symm[i][c] == '.'):
                            terms[-1] += symm[i][c]
                            c += 1
                        terms[-1] = float(terms[-1])
                    else: 
                        c += 1
            
            #Remove leading signs
            if terms[0] == '+':
                terms = terms[1:]
            elif terms[0] == '-':
                terms[1] = -terms[1]
                terms = terms[1:]
            
            #Multipy and divide
            while '*' in terms or '/' in terms:
                for j in xrange(len(terms)):
                    if terms[j] == '*':
                        value = terms[j-1] * terms[j+1]
                        newterms = terms[:j-1] + [value] + terms[j+2:]
                        break
                    elif terms[j] == '/':
                        value = terms[j-1] / terms[j+1]                        
                        newterms = terms[:j-1] + [value] + terms[j+2:]
                        break
                terms = newterms 
            
            #add and subtract
            while '+' in terms or '-' in terms:
                for j in xrange(len(terms)):
                    if terms[j] == '+':
                        value = terms[j-1] + terms[j+1]
                        newterms = terms[:j-1] + [value] + terms[j+2:]
                        break
                    elif terms[j] == '-':
                        value = terms[j-1] - terms[j+1]
                        newterms = terms[:j-1] + [value] + terms[j+2:]
                        break
                terms = newterms

            #Check that all calculations are done
            assert len(terms) == 1, terms            
            
            #Save value and put inside box
            pos[i] = terms[0]          
            while pos[i] >= 1:
                pos[i] -= 1.0
            while pos[i] < 0:
                pos[i] += 1.0  
        return pos
    
    def __tofloat(self, value):
    #Converts string to number and removes error range
        try:
            value = float(value)
        except:
            p_index = value.index('(') 
            value = float(value[:p_index])
        return value  
    
    def ucell(self):
        #Read in cell parameters
        try:
            a = self.__tofloat(self.alldict['_cell_length_a'] )
            b = self.__tofloat(self.alldict['_cell_length_b'] )
            c = self.__tofloat(self.alldict['_cell_length_c'] )
            alpha = self.__tofloat(self.alldict['_cell_angle_alpha'] )
            beta =  self.__tofloat(self.alldict['_cell_angle_beta']  )
            gamma = self.__tofloat(self.alldict['_cell_angle_gamma'] )
            box = Box(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)
        except:
            print 'Bad cell parameters'
            return None
        
        #Read in atom site fractions
        try:
            xlist = self.alldict['_atom_site_fract_x']
            ylist = self.alldict['_atom_site_fract_y']
            zlist = self.alldict['_atom_site_fract_z']
            
            if isinstance(xlist, list):
                site_fracts = []
                assert len(xlist) == len(ylist) == len(zlist)
                for i in xrange(len(xlist)):
                    site_fracts.append(np.array([self.__tofloat(xlist[i]),
                                                 self.__tofloat(ylist[i]), 
                                                 self.__tofloat(zlist[i])] ))
            else:
                site_fracts = [np.array([self.__tofloat(xlist[i]),
                                         self.__tofloat(ylist[i]), 
                                         self.__tofloat(zlist[i])] )]           
        except:
            print 'Bad atom site fractions'
            return None
        
        #Read in symmetry lists
        try:
            symms = self.alldict['_space_group_symop_operation_xyz']
        except:
            try:
                symms = self.alldict['_symmetry_equiv_pos_as_xyz']
            except:
                print 'No symmetries listed'
                return None
        if not isinstance(symms, list):
            symms = [symms]
        
        for i in xrange(len(symms)):
            if len(symms[i]) > 2:
                if (symms[i][0] == '"' and symms[i][-1] == '"') or (symms[i][0] == "'" and symms[i][-1] == "'"):
                    symms[i] = symms[i][1:-1] 
            symms[i] = symms[i].lower()
            symms[i] = symms[i].split(',')
            if len(symms[i]) != 3:
                raise ValueError('Bad symmetry terms')

        site = 0
        cell = []
        for site_fract in site_fracts:
            coords = []
            site += 1
    
            for symm in symms:
                coord = self.__calc(symm, site_fract)
                unique = True
                for c in coords:
                    if np.allclose(c, coord, rtol = 0.000001):
                        unique = False
                        break
                if unique:
                    coords.append(coord)
            for coord in coords:
                cell.append(Atom(site, coord))

        system = System(box=box, atoms=cell, scale=True)
        
        return system
        
    def element_list(self):
        try:
            try:
                elements = self.alldict['_atom_site_type_symbol']
            except:
                elements = self.alldict['_atom_site_label']
        except:
            print 'No atom site symbols or labels!'
            return None
        
        for i in xrange(len(elements)):
            for j in xrange(len(elements[i])):
                if elements[i][j].isdigit():
                    elements[i] = elements[i][:j]
                    break
            if len(elements[i]) == 0:
                print 'Bad atom site symbol or label!'
                return None
        return elements
            
            
    
        




            
