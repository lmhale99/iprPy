import atomman as am
import numpy as np
from collections import OrderedDict

#Reads a LAMMPS style dump file and returns an atomman.System. 
def read_dump(fname):
    with open(fname, 'r') as fin:
        pbc = None
        box = None
        natoms = None
        
        readnatoms = False
        readtime = False
        bcount = 3
        
        #loop over all lines in file
        for line in fin:
            terms = line.split()
            if len(terms) > 0:
                
                #read number of atoms if time to do so
                if readnatoms:                
                    natoms = int(terms[0])
                    if box is not None:
                        system = am.System(natoms=natoms, box=box, pbc=pbc)
                    readnatoms = False
                
                #read x boundary condition values if time to do so
                elif bcount == 0:
                    xlo = float(terms[0])
                    xhi = float(terms[1])
                    if len(terms) == 3:
                        xy = float(terms[2])
                    bcount += 1
                    
                #read y boundary condition values if time to do so
                elif bcount == 1:
                    ylo = float(terms[0])
                    yhi = float(terms[1])
                    if len(terms) == 3:
                        xz = float(terms[2])
                    bcount += 1
                    
                #read z boundary condition values if time to do so
                elif bcount == 2:
                    zlo = float(terms[0])
                    zhi = float(terms[1])
                    if len(terms) == 3:
                        yz = float(terms[2])
                        xlo = xlo - min((0.0, xy, xz, xy + xz))
                        xhi = xhi - max((0.0, xy, xz, xy + xz))
                        ylo = ylo - min((0.0, yz))
                        yhi = yhi - max((0.0, yz))
                        box = am.Box(xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi, zlo=zlo, zhi=zhi, xy=xy, xz=xz, yz=yz)
                    else:
                        box = am.Box(xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi, zlo=zlo, zhi=zhi)
                    if natoms is not None:
                        system = am.System(natoms=natoms, box=box, pbc=pbc)  
                    bcount += 1
                
                #read atomic values if time to do so
                elif readtime:
                    a_id = int(terms[id_index]) - 1
                    for i in xrange(len(terms)):
                        if i != id_index:
                            prop = terms_info[i][0]
                            #If scaler
                            if len(terms_info[i]) == 1:
                                try:
                                    prop_dict[prop] = np.array(terms[i], dtype=int)
                                except:
                                    prop_dict[prop] = np.array(terms[i], dtype=float)
                            
                            #If vector
                            elif len(terms_info[i]) == 2:
                                i_index = terms_info[i][1]
                                try:
                                    prop_dict[prop][i_index] = terms[i]
                                except:
                                    try:
                                        test = int(terms[i])
                                        prop_dict[prop] = np.zeros(prop_shapes[prop], dtype=int)
                                    except:
                                        prop_dict[prop] = np.zeros(prop_shapes[prop], dtype=float)
                                    prop_dict[prop][i_index] = terms[i]
                            
                            #If array        
                            elif len(terms_info[i]) == 3:
                                i_index = terms_info[i][1]
                                j_index = terms_info[i][2]
                                try:
                                    prop_dict[prop][i_index][j_index] = terms[i]
                                except:
                                    try:
                                        test = int(terms[i])
                                        prop_dict[prop] = np.zeros(prop_shapes[prop], dtype=int)
                                    except:
                                        prop_dict[prop] = np.zeros(prop_shapes[prop], dtype=float)
                                    prop_dict[prop][i_index][j_index] = terms[i]
                                      
                    for prop_name, prop_value in prop_dict.iteritems():
                        system.atoms(a_id, prop_name, prop_value, scale=scale)
                    
                #if not time to read data, check ITEM: header information
                else:
                    #only consider ITEM: lines
                    if terms[0] == 'ITEM:':
                    
                        #ITEM: NUMBER indicates it is time to read natoms
                        if terms[1] == 'NUMBER':
                            readnatoms = True
                            
                        #ITEM: BOX gives pbc and indicates it is time to read box parameters
                        if terms[1] == 'BOX':
                            pbc = [True, True, True]
                            for i in xrange(3):
                                if terms[i + len(terms) - 3] != 'pp':
                                    pbc[i] = False
                            bcount = 0
                            
                        #ITEM: ATOMS gives list of per-Atom property names and indicates it is time to read atomic values      
                        elif terms[1] == 'ATOMS':
                            terms_info = terms[2:]
                            prop_dict = OrderedDict()
                            id_index = -1
                            pos_list = ['', '', '']
                            
                            #Separate out vector/matrix names and indexes into tuples
                            for i in xrange(len(terms_info)):        
                                try:
                                    start = terms_info[i].index('[')
                                    end = terms_info[i].index(']')
                                    pname = terms_info[i][:start]
                                    i_index = int(terms_info[i][start+1:end])
                                    try:
                                        start2 = terms_info[i][end+1:].index('[')
                                        end2 = terms_info[i][end+1:].index(']')
                                        j_index = int(terms_info[i][end+1:][start2+1:end2])
                                        terms_info[i] = (pname, i_index, j_index)
                                    except:
                                        terms_info[i] = (pname, i_index)
                                except:
                                    terms_info[i] = (terms_info[i],)

                                #Handle special names
                                if terms_info[i][0] == 'id':
                                    assert len(terms_info[i]) == 1
                                    id_index = i                                

                                elif terms_info[i][0] == 'type':
                                    assert len(terms_info[i]) == 1
                                    terms_info[i] = ('atype',)
                                    prop_dict['atype'] = np.zeros((), dtype=int)

                                elif terms_info[i][0] in ['x', 'xu', 'xs', 'xsu']:
                                    assert len(terms_info[i]) == 1
                                    for j in xrange(i+1, len(terms_info)):
                                        assert terms_info[j][0] not in ['x', 'xu', 'xs', 'xsu'], 'Only one set of positions allowed'
                                    pos_list[0] = terms_info[i][0]
                                    terms_info[i] = ('pos', 0)

                                elif terms_info[i][0] in ['y', 'yu', 'ys', 'ysu']:
                                    assert len(terms_info[i]) == 1
                                    for j in xrange(i+1, len(terms_info)):
                                        assert terms_info[j][0] not in ['y', 'yu', 'ys', 'ysu'], 'Only one set of positions allowed'
                                    pos_list[1] = terms_info[i][0]
                                    terms_info[i] = ('pos', 1)

                                elif terms_info[i][0] in ['z', 'zu', 'zs', 'zsu']:
                                    assert len(terms_info[i]) == 1
                                    for j in xrange(i+1, len(terms_info)):
                                        assert terms_info[j][0] not in ['z', 'zu', 'zs', 'zsu'], 'Only one set of positions allowed'
                                    pos_list[2] = terms_info[i][0]
                                    terms_info[i] = ('pos', 2)    

                            assert id_index > -1, 'atom id not found'
                            try:
                                test = prop_dict['atype']
                            except:
                                raise ValueError('atom type not found')
                                    
                            if pos_list == ['x', 'y', 'z'] or pos_list == ['xu', 'yu', 'zu']:
                                scale = False
                                prop_dict['pos'] = np.zeros((3L,), dtype=float)
                            elif pos_list == ['xs', 'ys', 'zs'] or pos_list == ['xsu', 'ysu', 'zsu']:
                                scale = True
                                prop_dict['pos'] = np.zeros((3L,), dtype=float) 
                            else:
                                raise ValueError('Missing or mixed coordinates not allowed')

                            #build prop_shapes dictionary
                            prop_shapes = {}
                            for i in xrange(len(terms_info)):
                                try:
                                    test = prop_shapes[terms_info[i][0]]
                                except:
                                    if len(terms_info[i]) == 1:
                                        prop_shapes[terms_info[i][0]] = ()
                                    elif len(terms_info[i]) == 2:
                                        maxi = 0
                                        for j in xrange(i, len(terms_info)):
                                            if terms_info[i][0] == terms_info[j][0]:
                                                if terms_info[j][1] > maxi:
                                                    maxi = terms_info[j][1]
                                        maxi = long(maxi+1)
                                        prop_shapes[terms_info[i][0]] = (maxi, )
                                    elif len(terms_info[i]) == 3:
                                        maxi = 0
                                        maxj = 0
                                        for j in xrange(i, len(terms_info)):
                                            if terms_info[i][0] == terms_info[j][0]:
                                                if terms_info[j][1] > maxi:
                                                    maxi = terms_info[j][1]
                                                if terms_info[j][2] > maxj:
                                                    maxj = terms_info[j][2]
                                        maxi = long(maxi+1)
                                        maxj = long(maxj+1)
                                        prop_shapes[terms_info[i][0]] = (maxi, maxj)
                            readtime = True  
        
    return system    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
