from collections import OrderedDict
import numpy as np
import iprp

def isint(value):
    try:
        test = int(value)
        return True
    except:
        return False

def calc(expr,x,y,z):
    terms = []
    i = 0
    while i < len(expr):
        if expr[i] == '+' or expr[i] == '-' or expr[i] == '/':
            terms.append(expr[i])
            i += 1
        elif expr[i] == 'x' or expr[i] == 'X':
            terms.append(float(x))
            i += 1
        elif expr[i] == 'y' or expr[i] == 'Y':
            terms.append(float(y))
            i += 1
        elif expr[i] == 'z' or expr[i] == 'Z':
            terms.append(float(z))
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

def tofloat(expr):
    try:
        ind = expr.index('(')
        val = float(expr[:ind])
    except:    
        val = float(expr)
    return val
    
def ucell(cif_dict):
    if True:
    #try:
        if isinstance(cif_dict['_atom_site_fract_x'],list):
            xlist = cif_dict['_atom_site_fract_x']
            ylist = cif_dict['_atom_site_fract_y']
            zlist = cif_dict['_atom_site_fract_z']
        else:
            xlist = [cif_dict['_atom_site_fract_x']]
            ylist = [cif_dict['_atom_site_fract_y']]
            zlist = [cif_dict['_atom_site_fract_z']]
        symms = cif_dict['_symmetry_equiv_pos_as_xyz']    
        a = tofloat(cif_dict['_cell_length_a'])
        b = tofloat(cif_dict['_cell_length_b'])
        c = tofloat(cif_dict['_cell_length_c'])
        alpha = tofloat(cif_dict['_cell_angle_alpha'])
        beta = tofloat(cif_dict['_cell_angle_beta'])
        gamma = tofloat(cif_dict['_cell_angle_gamma'])
    else:
    #except:
        print 'Not all information supplied!'
        
    alat = np.array([a/a,b/a,c/a])
    angle = np.array([alpha,beta,gamma])
    
    coords = []
    site = 0
    for i in xrange(len(xlist)):
        site += 1
        x = X = float(xlist[i])
        y = Y = float(ylist[i])
        z = Z = float(zlist[i])
        
        for symm in symms:
            terms = symm.split(',')
            if len(terms) == 3:
                coord = np.empty(3)
                for i in xrange(3):
                    coord[i] = calc(terms[i],x,y,z)
                    while coord[i] >=1:
                        coord[i] - 1
                    while coord[i] < 0:
                        coord[i] + 1
                coords.append(coord)
        cell = []
        for i in xrange(len(coords)):
            unique = True
            for j in xrange(len(cell)):
                if np.allclose(coords[i],cell[j].coord):
                    unique = False
                    break
            if unique:
                cell.append(iprp.Atom(site,coords[i]))
  
    return alat,angle,cell
        
def cread(fname):
    with open(fname) as cif_file:
        cif_data = cif_file.read()
    terms = []
    i = 0
    while i < len(cif_data):
        if cif_data[i] == '#':
            i += 1
            while i < len(cif_data) and cif_data[i] != '\n':
                i += 1
        elif cif_data[i] == ' ' or cif_data[i] == '\n':
            i += 1
        elif cif_data[i] == "'":
            term = ''
            i += 1
            while cif_data[i] != "'":
                term += cif_data[i]
                i+=1
            terms.append(term.strip())
            i += 1   
        elif cif_data[i] == '"':
            term = ''
            i += 1
            while cif_data[i] != '"':
                term += cif_data[i]
                i+=1
            terms.append(term.strip())
            i += 1  
        elif cif_data[i] == ';':
            term = ''
            i += 1
            while cif_data[i] != ';':
                term += cif_data[i]
                i+=1
            terms.append(term.strip())
            i += 1  
        else:
            term = cif_data[i]
            i += 1
            while i < len(cif_data) and cif_data[i] != ' ' and cif_data[i] != '\n':
                term += cif_data[i]
                i += 1
            terms.append(term.strip())
    
    alldata = OrderedDict()
    i = 0
    while i < len(terms):
        if terms[i][:5] == 'data_':
            dname = terms[i][5:]
            alldata[dname] = data = OrderedDict()
            i += 1
        elif terms[i][0] == '_' and terms[i+1][0] != '_':
            data[terms[i]] = terms[i+1]
            i += 2
        elif terms[i] == 'loop_':
            vlist = []
            i += 1
            while i < len(terms) and terms[i][0] == '_':
                vlist.append(terms[i])
                i += 1
            dlist = []
            while i < len(terms) and terms[i][0] != '_' and terms[i] != 'loop_':
                dlist.append(terms[i])
                i += 1
        
            if len(dlist) == len(vlist):
                for j in xrange(len(vlist)):
                    data[vlist[j]] = dlist[j]
            
            elif len(dlist)%len(vlist) == 0:
                for j in xrange(len(vlist)):
                    data[vlist[j]] = []
                for k in xrange(len(dlist)):
                    j = k%len(vlist)
                    data[vlist[j]].append(dlist[k])

    return alldata
                    
def cif_print(alldata):                    
    for dname, data in alldata.iteritems():
        print dname
        for k,v in data.iteritems():
            if isinstance(v, list):
                print k
                for val in v:
                    print '  '+val
            else:
                print k, v
            
 
        
data = cread('C:\\Users\\lmh1\\Documents\\sql\\COD-1\\1506411.cif')
for name,d in data.iteritems():
    alat, angle, coords = ucell(d)

    print alat
    print angle
    print 
    for coord in coords:
        print coord
            