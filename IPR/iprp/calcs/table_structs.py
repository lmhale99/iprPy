import os
import iprp.models as dm

def table_structs(ipr_dir, potential):
    struct_dir = os.path.join(ipr_dir, 'results', 'json', 'struct')
    flist = os.listdir(struct_dir)
    name = potential.get('id')
    
    cryslist = []
    
    for fname in flist:
        if fname[:8] == 'struct--' and fname[-5:] == '.json' and name in fname:
            filename = os.path.join(struct_dir, fname)
            cryslist.append(dm.CrystalPhase(filename))
    
    sortedlist = sorted(cryslist,key=lambda unit: unit.get('ecoh'))
    
    term_list = ['hash', 'prototype', 'chem_formula', 'ecoh', 'alat', 'b_mod', 'cij']     
    
    sim_dir = os.path.join(ipr_dir, 'results', 'sim', name)
    with open(os.path.join(sim_dir, 'struct.csv'),'w') as csv:
        
        for term in term_list:
            if term == 'alat':
               csv.write('alat,blat,clat,') 
            elif term == 'cij':
               csv.write('C11,C22,C33,C12,C13,C23,C44,C55,C66,') 
            else:    
                csv.write(term+',')
        csv.write('\n')
        
        for crystal in sortedlist:
            for term in term_list:
                if term == 'ecoh' or term == 'b_mod':
                    csv.write('%f,' % crystal.get(term))
                elif term == 'alat':
                    csv.write('%f,%f,%f,' % (crystal.get('alat')[0],
                                             crystal.get('alat')[1], 
                                             crystal.get('alat')[2]))
                elif term == 'cij':
                    csv.write('%f,%f,%f,%f,%f,%f,%f,%f,%f,' % (crystal.get('cij')[0,0],
                                                               crystal.get('cij')[1,1],
                                                               crystal.get('cij')[2,2],
                                                               crystal.get('cij')[0,1],
                                                               crystal.get('cij')[0,2],
                                                               crystal.get('cij')[1,2],
                                                               crystal.get('cij')[3,3],
                                                               crystal.get('cij')[4,4],
                                                               crystal.get('cij')[5,5]))                    
                else:
                    csv.write('%s,' % crystal.get(term))
            csv.write('\n')
            