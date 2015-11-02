import os
import numpy as np
import iprp
import sys
from collections import OrderedDict


def main(argv):

    sites = [iprp.Atom(1,np.array([0.0, 0.0, 0.0])),
             iprp.Atom(2,np.array([0.25, 0.25, 0.25]))]
    space_group = 'F m -3 m'
    
    with open('sglist.txt','r') as f:
        space_group_symmetries = read_sg_file(f)
    
    
    symms = space_group_symmetries[space_group]
    
    ucell = generate_ucell(sites, symms)
    
    ntypes = 0
    for site in sites:
        if site.get('atype') > ntypes:
            ntypes = site.get('atype')
    
    output = '"site": ['
    
    first_type = True
    for atype in xrange(1,ntypes+1):
        if first_type:  
            first_type = False
        else:
            output += ','
        output += '\n'
        output += '    {\n'    
        output += '        "component": %i,\n'%atype
        output += '        "atomCoordinates": ['
        
        first_coord = True
        for atom in ucell:
            if atom.get('atype') == atype:
                if first_coord: 
                    first_coord = False
                else:
                    output += ','
                output += '\n'
                output += '            {\n'
                output += '                "value": [%.13f, %.13f, %.13f],\n'%(atom.get('coordx'),atom.get('coordy'),atom.get('coordz'))
                output += '                "unit": "scaled"\n'
                output += '            }'
        output += '\n'
        output += '        ]\n'
        output += '    }'
    output += '\n'
    output += ']'
    
    print output

        
    
    
def read_sg_file(file_data):
    data = OrderedDict()
    symm_read = False
    
    for line in file_data:
        line = line.strip()
        if symm_read:
            symm = line.split(',')
            if len(symm) == 3:
                data[name].append(symm)
            else:
                symm_read = False
                    
        else:
            if len(line) > 0 and line[0] == "'":
                name = line.strip("'")
                data[name] = []
                symm_read = True
    
    return data
            
def generate_ucell(sites, symms):
    ucell = []
    for site in sites:
        coords = []
        for symm in symms:
            coord = np.empty(3)
            for i in xrange(3):
                coord[i] = calc(symm[i],site.get('coord'))
                while coord[i] >=1:
                    coord[i] -= 1
                while coord[i] < 0:
                    coord[i] += 1
                if coord[i] == 0.0:
                    coord[i] = 0.0
                coords.append(coord)
        for i in xrange(len(coords)):
            unique = True
            for j in xrange(len(ucell)):
                if np.allclose(coords[i],ucell[j].get('coord')):
                    unique = False
                    break
            if unique:
                ucell.append(iprp.Atom(site.get('atype'), coords[i]))
    return ucell
        
    


    
def calc(expr,coord):
    terms = []
    i = 0
    while i < len(expr):
        if expr[i] == '+' or expr[i] == '-' or expr[i] == '/':
            terms.append(expr[i])
            i += 1
        elif expr[i] == 'x' or expr[i] == 'X':
            terms.append(coord[0])
            i += 1
        elif expr[i] == 'y' or expr[i] == 'Y':
            terms.append(coord[1])
            i += 1
        elif expr[i] == 'z' or expr[i] == 'Z':
            terms.append(coord[2])
            i += 1
        elif isint(expr[i]):
            term = expr[i]
            i += 1
            while i < len(expr) and (isint(expr[i]) or expr[i] == '.'):
                term += expr[i]
                i += 1
            terms.append(float(term))
        else:
            print 'Unsupported character '+expr[i]
    
    if terms[0] == '+':
        temp = terms.pop(0)
    elif terms[0] == '-':
        terms[1] = -1 * terms[1]
        temp = terms.pop(0)
    round1 = True
    while round1:
        try:
            div = terms.index('/')
            rh = terms.pop(div+1)
            temp = terms.pop(div)
            lh = terms.pop(div-1)               
            new = lh/rh
            terms.insert(div-1,new)
        except:
            round1 = False
    
    round2 = True
    while round2:
        try:
            add = terms.index('+')
        except:
            add = 9999999
        try:
            sub = terms.index('-')
        except:
            sub = 9999999
        if add == sub == 9999999:
            round2 = False
        else:
            if add < sub:
                rh = terms.pop(add+1)
                temp = terms.pop(add)
                lh = terms.pop(add-1)               
                new = lh+rh
                terms.insert(add-1,new)
            else:
                rh = terms.pop(sub+1)
                temp = terms.pop(sub)
                lh = terms.pop(sub-1)               
                new = lh-rh
                terms.insert(sub-1,new)
    if len(terms) > 1:
        print 'Rough row!'
    return terms[0]    
    
    
    
    
    
    
    
    
    
    
    
    
    
def isint(value):
    try:
        test = int(value)
        return True
    except:
        return False    
    
    
    
    
    
    
if __name__ == '__main__':
    main(sys.argv)        