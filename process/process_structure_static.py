import os
import glob
from DataModelDict import DataModelDict

def structure_static(xml_lib_dir):
    calc_name = 'structure_static'
    groups = os.path.join(xml_lib_dir, '*', calc_name, '*')
    
    error_dict = DataModelDict()
    
    for group_dir in glob.iglob(groups):
        if os.path.isdir(group_dir):
            calc_dir, group_name = os.path.split(group_dir)
            pot_name = os.path.basename(os.path.dirname(calc_dir))
            print pot_name
            try:
                with open(os.path.join(calc_dir, 'badlist.txt'), 'r') as f:
                    badlist = f.read().split()
            except:
                badlist = []
            
            data = DataModelDict()
            
            for sim_path in glob.iglob(os.path.join(group_dir, '*.xml')):
                sim_file = os.path.basename(sim_path)
                sim_name = sim_file[:-4]
                
                if sim_name in badlist:
                    continue
                    
                with open(sim_path) as f:
                    sim = DataModelDict(f)['calculation-crystal-phase']
                
                if 'error' in sim:
                    badlist.append(sim_name)
                    error_message = sim['error']
                    error = 'Unknown error'
                    for line in error_message.split('\n'):
                        if 'Error' in line:
                            error = line
                    error_dict.append(error, sim_name)
                    continue
            
                try:
                    cell = sim['relaxed-atomic-system']['cell']
                except:
                    tar_gz_path = sim_path[:-4] + '.tar.gz'
                    if os.isfile(tar_gz_path):
                        error_dict.append('Unknown error', sim_name)
                    continue
                    
                data.append('key', sim.get('calculation-id', ''))
                data.append('file', sim['crystal-info'].get('artifact', ''))
                data.append('symbols', '_'.join(sim['crystal-info'].aslist('symbols')))
                
                data.append('Temperature (K)', sim['phase-state']['temperature']['value'])
                data.append('Pressure (GPa)', sim['phase-state']['pressure']['value'])

                cell = cell[cell.keys()[0]]
                data.append('Ecoh (eV)', sim['cohesive-energy']['value'] )
                if 'a' in cell:
                    data.append('a (A)', cell['a']['value'])
                else:
                    data.append('a (A)', '')
                if 'b' in cell:
                    data.append('b (A)', cell['b']['value'])
                else:
                    data.append('b (A)', '')
                if 'c' in cell:
                    data.append('c (A)', cell['c']['value'])
                else:
                    data.append('c (A)', '')
                C_dict = {}
                for C in sim['elastic-constants'].iteraslist('C'):
                    C_dict[C['ij']] = C['stiffness']['value']
                data.append('C11 (GPa)', C_dict.get('1 1', ''))
                data.append('C22 (GPa)', C_dict.get('2 2', ''))
                data.append('C33 (GPa)', C_dict.get('3 3', ''))
                data.append('C12 (GPa)', C_dict.get('1 2', ''))
                data.append('C13 (GPa)', C_dict.get('1 3', ''))
                data.append('C23 (GPa)', C_dict.get('2 3', ''))
                data.append('C44 (GPa)', C_dict.get('4 4', ''))
                data.append('C55 (GPa)', C_dict.get('5 5', ''))
                data.append('C66 (GPa)', C_dict.get('6 6', ''))
                
            
            if len(data.keys()) > 0: 
                with open(os.path.join(calc_dir, 'structure_static_'+group_name+'.csv'), 'w') as f:
                    f.write(','.join(data.keys())+'\n')
                    for i in xrange(len(data.aslist('key'))):
                        f.write(','.join([str(data.aslist(k)[i]) for k in data.keys()]) + '\n')

            
            with open(os.path.join(calc_dir, 'badlist.txt'), 'w') as f:
                for bad in badlist:
                    f.write(bad+'\n')


    


    
    
        