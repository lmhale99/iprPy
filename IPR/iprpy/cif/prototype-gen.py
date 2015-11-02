import os
import re

def isint(value):
    try:
        test = int(value)
        return True
    except:
        return False

def xyz_parse(xyz):
    #remove quotes and compress
    try:
        start = xyz.index("'")+1
        end = xyz.rindex("'")
        reduced = xyz[start:end]
        xyz = reduced.replace(' ','')
    except:
        pass
    
    #make all lowercase
    xyz = xyz.lower()
    
    #test for and remove identifying number
    terms = xyz.split()
    if len(terms) == 2 and isint(terms[0]):
        xyz = terms[1]
    else:
        xyz = terms[0]
        
    return xyz 
    
      
dirs = ['C:\Users\lmh1\Documents\sql\COD-1',
        'C:\Users\lmh1\Documents\sql\COD-2']
readtime = False
sg = {}
for dir in dirs:
    flist = os.listdir(dir)
    for fname in flist:
        bad = False
        f = open(os.path.join(dir,fname),'r')
        sgnum = 0
        sgname = ''
        for line in f:
            terms = line.split()
            if bad:
                break
            if len(terms) > 0:
                if bad:
                    break
                if readtime:
                    if terms[0] == 'loop_' or terms[0][0]=='_':
                        readtime = False
                    else:
                        xyz = xyz_parse(line)
                        sg[sgnum][sgname].append(xyz)
                        
                elif terms[0] == '_space_group_IT_number':
                    try:
                        sgnum = terms[1]
                    except:
                        bad = True
                        break
                elif terms[0] == '_symmetry_space_group_name_H-M':
                    try:
                        sgname = terms[1]
                    except:
                        bad = True
                        break
                    for i in xrange(2,len(terms)):
                        sgname += " " + terms[i]
                elif terms[0] == '_symmetry_equiv_pos_as_xyz':
                    if sgnum > 0 and sgname != '':
                        try:
                            test = sg[sgnum]
                        except:
                            sg[sgnum] = {}
                        sg[sgnum][sgname] = []
                        readtime = True
                   
        f.close()
sglist = open('sglist.txt','w')
for i in xrange(1,231):
    showit = True
    try:
        num = str(i)
        spaceg = sg[num]
    except:
        showit = False
    
    if showit:
        sglist.write(str(i)+'\n')
        for spacen, symm in spaceg.iteritems():
            sglist.write(spacen+'\n')
            for xyz in symm:
                sglist.write(xyz+'\n')
            sglist.write('\n')
        sglist.write('\n')
sglist.close()

             
                
    
    