import os
import subprocess
import random
import shutil
import time
from DataModelDict import DataModelDict
import sys

def main():
    sim_dir = 'C:/users/lmh1/Documents/iprPy_run/'
    xml_dir = 'C:/users/lmh1/Documents/iprPy_run/xml_library'
    
    to_run_dir = os.path.join(sim_dir, 'to_run')
    has_ran_dir = os.path.join(sim_dir, 'has_ran')
    
    os.chdir(to_run_dir)
    flist = os.listdir(to_run_dir)
    
    while len(flist) > 0:
        index = random.randint(0, len(flist)-1)
        sim = flist[index]
        
        if bid(sim):
            os.chdir(sim)
            
            try:
                calc_py = None
                calc_in = None
                calc_name = None
                pot_name = None
                
                #find calc_*.py and calc_*.in files
                for fname in os.listdir(os.getcwd()):
                    if fname[:5] == 'calc_':
                        if fname[-3:] == '.py':
                            if calc_py is None:
                                calc_py = fname
                                calc_name = fname[5:-3]
                            else:
                                raise ValueError('folder has multiple calc_*.py scripts')
                        elif fname[-3:] == '.in':
                            if calc_in is None:
                                calc_in = fname
                            else:
                                raise ValueError('folder has multiple calc_*.in scripts')
                    elif fname[-5:] == '.json' or fname[-4:] == '.xml':
                        try:
                            with open(fname) as f:
                                test = DataModelDict(f)
                                pot_name = test.find('LAMMPS-potential')['potential']['id']
                        except:
                            pass

                assert pot_name is not None, 'LAMMPS-potential data model not found'                
                assert calc_py is not None, 'calc_*.py script not found'
                assert calc_py is not None, 'calc_*.in script not found'
                run = subprocess.Popen(['python', calc_py, calc_in, sim], stderr=subprocess.PIPE)
                if run.stderr.read() != '':
                    raise RuntimeError(run.stderr.read())

            except:
                with open(os.path.join(xml_dir, sim + '.xml')) as f:
                    model = DataModelDict(f)
                key = model.keys()[0]
                model[key]['error'] = str(sys.exc_info()[1])
                with open('results.json', 'w') as f:
                    model.json(fp=f, indent=4)
            pot_xml_dir = os.path.join(xml_dir, pot_name, calc_name, 'standard')
            print pot_xml_dir
            with open('results.json') as f:
                model = DataModelDict(f)
            with open(os.path.join(pot_xml_dir, sim + '.xml'), 'w') as f:
                model.xml(fp=f, indent=4)
            os.chdir(to_run_dir)
            shutil.move(os.path.join(to_run_dir, sim), os.path.join(has_ran_dir, sim))    
            
        flist = os.listdir(to_run_dir)
        
        
        
#Bids for chance to run simulation        
def bid(sim):
    #check if bid already exists
    for fname in os.listdir(sim):
        if fname[-4:] == '.bid':
            return False

    #place a bid
    pid = os.getpid()
    with open(os.path.join(sim, str(pid)+'.bid'), 'w') as f:
        f.write('bid for pid: %i' % pid)
    
    #wait one second
    time.sleep(1)

    #check bids
    bids = []
    for fname in os.listdir(sim):
        if fname[-4:] == '.bid':
            bids.append(int(fname[:-4]))
    if min(bids) == pid:
        return True
    else:
        return False
    
                
            
            
if __name__ == '__main__':
    main()
            



            
            
