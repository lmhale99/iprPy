#!/usr/bin/env python
import os
import sys
import subprocess
import random
import shutil
import time
import glob
from DataModelDict import DataModelDict as DM


def main(*args):
    
    #Read in input script terms
    run_directory, lib_directory = __initial_setup(*args)
    
    #The orphan dir is where incomplete calculations or calculations without records are placed
    orphan_dir = os.path.join(lib_directory, 'orphan')
    
    log_file = str(os.getpid()) + '-runner.log'
    with open(log_file, 'a') as log:
        
        #Change to the run directory
        os.chdir(run_directory)
        
        #flist is the running list of calculations
        flist = os.listdir(run_directory)
        while len(flist) > 0:
            
            #Pick a random calculation from the list
            index = random.randint(0, len(flist)-1)
            sim = flist[index]
            
            #Submit a bid
            if bid(sim):
                os.chdir(sim)
                log.write('%s\n' % sim)
                #Check that the calculation has calc_*.py, calc_*.in and record in the library
                try:
                    record = get_file(os.path.join(lib_directory, '*', '*', '*', '*', sim+'.json'))
                    calc_py = get_file('calc_*.py')
                    calc_in = get_file('calc_*.in')
                
                #If not complete, zip and move to the orphan directory
                except:
                    log.write('Incomplete simulation: moved to orphan directory\n\n')
                    os.chdir(run_directory)
                    if not os.path.isdir(orphan_dir):
                        os.makedirs(orphan_dir)
                    shutil.make_archive(os.path.join(orphan_dir, sim), 'gztar', root_dir=run_directory, base_dir=sim)
                    shutil.rmtree(os.path.join(run_directory, sim))
                    flist = os.listdir(run_directory)
                    continue
                
                #Check if any files in the calculation folder are incomplete records 
                error_flag = False
                ready_flag = True

                for fname in glob.iglob('*'):
                    if os.path.splitext(fname)[1] in ('.json', '.xml'):
                        with open(fname) as f:
                            parent = DM(f)
                        try:
                            status = parent.find('status')
                            
                            #Check parent record in library to see if it has completed
                            if status == 'not calculated':
                                parent_record = get_file(os.path.join(lib_directory, '*', '*', '*', '*', fname))
                                with open(parent_record) as f:
                                    parent = DM(f)
                                try:
                                    status = parent.find('status')
                                    
                                    #Mark flag if still incomplete
                                    if status == 'not calculated':
                                        ready_flag = False
                                        parent_key = os.path.splitext(fname)[0]
                                        break
                                    
                                    #skip if parent calculation failed
                                    elif status == 'error':
                                        shutil.copy(parent_record, fname)
                                        error_flag = True
                                        error_message = 'parent calculation issued an error'
                                        break
                                
                                #Copy parent record to calculation folder if it is now complete
                                except:
                                    shutil.copy(parent_record, fname)
                                    log.write('parent %s copied to sim folder\n' % parent_key)
                            
                            #skip if parent calculation failed
                            elif status == 'error':
                                error_flag = True
                                error_message = 'parent calculation issued an error'
                                break
                        except:
                            continue

                #Handle calculations that have unfinished parents
                if not ready_flag:
                    bid_files = glob.glob('*.bid')
                    os.chdir(run_directory)
                    for bid_file in bid_files:
                        os.remove(os.path.join(sim, bid_file))
                    flist = [parent_key]              
                    log.write('parent %s not ready\n\n' % parent_key)
                    continue
                
                #Run the calculation
                try:   
                    assert not error_flag, error_message
                    run = subprocess.Popen(['python', calc_py, calc_in, sim], stderr=subprocess.PIPE)
                    error_message = run.stderr.read()
                    
                    #Check for results.json file
                    try:
                        with open('results.json') as f:
                            model = DM(f)
                    except:
                        error_flag = True
                    assert not error_flag, error_message
                    log.write('sim calculated successfully\n\n')
                
                #Catch any errors and add them to results.json
                except:
                    with open(record) as f:
                        model = DM(f)
                    key = model.keys()[0]
                    model[key]['status'] = 'error'
                    model[key]['error'] = str(sys.exc_info()[1])
                    with open('results.json', 'w') as f:
                        model.json(fp=f, indent=4)
                    log.write('error: %s\n\n' % model[key]['error'])

                #Update record in the library
                with open('results.json') as f:
                    model = DM(f)
                with open(record, 'w') as f:
                    model.json(fp=f, indent=2)
                
                #Zip and move calculation folder to the library
                os.chdir(run_directory)
                record_dir = os.path.dirname(record)
                shutil.make_archive(os.path.join(record_dir, sim), 'gztar', root_dir=run_directory, base_dir=sim)
                try:
                    shutil.rmtree(os.path.join(run_directory, sim))    
                except:
                    pass
            flist = os.listdir(run_directory)
            log.flush()
            os.fsync(log.fileno())
        
#Bids for chance to run simulation        
def bid(sim):
    try:
        #wait to make sure sim is not being deleted
        time.sleep(0.25)
        
        #check if bid already exists
        for fname in os.listdir(sim):
            if fname[-4:] == '.bid':
                return False

        #place a bid
        pid = os.getpid()
        with open(os.path.join(sim, str(pid)+'.bid'), 'w') as f:
            f.write('bid for pid: %i' % pid)
        
        #wait to make sure all bids are in
        time.sleep(0.75)

        #check bids
        bids = []
        for fname in os.listdir(sim):
            if fname[-4:] == '.bid':
                bids.append(int(fname[:-4]))
        if min(bids) == pid:
            return True
        else:
            return False
    except:
        return False                

def get_file(path_string):
    file = glob.glob(path_string)
    if len(file) == 1:
        return file[0]
    elif len(file) == 0:
        raise ValueError('Cannot find file matching ' + path_string)
    else:
        raise ValueError('Multiple files found matching '+ path_string)
    
        
def __initial_setup(*args):            
    run_directory = None
    lib_directory = None
    with open(args[0]) as f:
        for line in f:
            terms = line.split()
            if len(terms) > 0 and terms[0][0] != '#':
                if terms[0] == 'run_directory' and run_directory is None:
                    run_directory = ' '.join(terms[1:])
                elif terms[0] == 'lib_directory' and lib_directory is None:
                    lib_directory = ' '.join(terms[1:])
                else:
                    raise ValueError('Invalid runner.py input line')
    if run_directory is not None and lib_directory is not None:
        return run_directory, lib_directory
    else:
        raise ValueError('runner.py input requires both run_directory and lib_directory')
    
if __name__ == '__main__':
    main(*sys.argv[1:])
            



            
            
