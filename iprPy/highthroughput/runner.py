#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import subprocess
import random
import shutil
import time
import glob
import datetime
import requests

from DataModelDict import DataModelDict as DM

import iprPy

def main(*args):
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict)
    
    runner(input_dict['dbase'], 
           input_dict['run_directory'],
           orphan_directory = input_dict['orphan_directory'])
    
def runner(dbase, run_directory, orphan_directory=None):
    """High-throughput calculation runner"""
    
    # Define runner log file
    d = datetime.datetime.now()
    runner_log_dir = os.path.join(os.path.dirname(iprPy.rootdir), 'runner-logs')
    if not os.path.isdir(runner_log_dir):
        os.makedirs(runner_log_dir)
    log_file = os.path.join(runner_log_dir, '%04i-%02i-%02i-%02i-%02i-%06i.log' % (d.year, d.month, d.day, d.minute, d.second, d.microsecond))
    
    # Set default orphan_directory
    if orphan_directory is None:
        orphan_directory = os.path.join(os.path.dirname(run_directory), 'orphan')
    
    # Start runner log file
    with open(log_file, 'a') as log:
        
        # Change to the run directory
        os.chdir(run_directory)
        
        # Initialize bidfailcount counter
        bidfailcount = 0
        
        # flist is the running list of calculations
        flist = os.listdir(run_directory)
        while len(flist) > 0:
            
            # Pick a random calculation from the list
            index = random.randint(0, len(flist)-1)
            sim = flist[index]
            
            # Submit a bid and check if it succeeded
            if bid(sim):
                
                # Reset bidfailcount
                bidfailcount = 0
                
                # Move to simulation directory
                os.chdir(sim)
                log.write('%s\n' % sim)
                
                # Check that the calculation has calc_*.py, calc_*.in and record in the database
                try:
                    record = dbase.get_record(name=sim)
                    calc_py = get_file('calc_*.py')
                    calc_in = get_file('calc_*.in')
                
                # Pass ConnectionErrors forward killing runner
                except requests.ConnectionError as e:
                    raise requests.ConnectionError(e)
                
                # If not complete, zip and move to the orphan directory
                except:
                    log.write('Incomplete simulation: moved to orphan directory\n\n')
                    os.chdir(run_directory)
                    if not os.path.isdir(orphan_directory):
                        os.makedirs(orphan_directory)
                    shutil.make_archive(os.path.join(orphan_directory, sim), 'gztar', root_dir=run_directory, base_dir=sim)
                    removecalc(os.path.join(run_directory, sim))
                    flist = os.listdir(run_directory)
                    continue
                
                # Check if any files in the calculation folder are incomplete records 
                error_flag = False
                ready_flag = True

                for fname in glob.iglob('*'):
                    parent_sim, ext = os.path.splitext(os.path.basename(fname))
                    if ext in ('.json', '.xml'):
                        with open(fname) as f:
                            parent = DM(f)
                        try:
                            status = parent.find('status')
                            
                            # Check parent record in database to see if it has completed
                            if status == 'not calculated':
                                parent_record = dbase.get_record(name=parent_sim)
                                parent = DM(parent_record.content)
                                try:
                                    status = parent.find('status')
                                    
                                    # Mark flag if still incomplete
                                    if status == 'not calculated':
                                        ready_flag = False
                                        break
                                    
                                    # Skip if parent calculation failed
                                    elif status == 'error':
                                        with open(os.path.basename(fname), 'w') as f:
                                            f.write(parent_record.content)
                                        error_flag = True
                                        error_message = 'parent calculation issued an error'
                                        break
                                    
                                    # Ignore if unknown status
                                    else:
                                        raise ValueError('unknown status')
                                        
                                # Copy parent record to calculation folder if it is now complete
                                except:
                                    with open(os.path.basename(fname), 'w') as f:
                                        f.write(parent_record.content)
                                    log.write('parent %s copied to sim folder\n' % parent_sim)
                            
                            # skip if parent calculation failed
                            elif status == 'error':
                                error_flag = True
                                error_message = 'parent calculation issued an error'
                                break
                        except:
                            continue

                # Handle calculations that have unfinished parents
                if not ready_flag:
                    bid_files = glob.glob('*.bid')
                    os.chdir(run_directory)
                    for bid_file in bid_files:
                        os.remove(os.path.join(sim, bid_file))
                    flist = [parent_sim]              
                    log.write('parent %s not ready\n\n' % parent_sim)
                    continue
                
                # Run the calculation
                try:   
                    assert not error_flag, error_message
                    run = subprocess.Popen(['python', calc_py, calc_in, sim], stderr=subprocess.PIPE)
                    error_message = run.stderr.read()
                    
                    # Load results.json
                    try:
                        with open('results.json') as f:
                            model = DM(f)
                    # Throw errors if no results.json
                    except:
                        error_flag = True
                    assert not error_flag, error_message
                    log.write('sim calculated successfully\n\n')
                
                # Catch any errors and build results.json
                except:
                    model = DM(record.content)
                    record_type = model.keys()[0]
                    model[record_type]['status'] = 'error'
                    model[record_type]['error'] = str(sys.exc_info()[1])
                    with open('results.json', 'w') as f:
                        model.json(fp=f, indent=4)
                    log.write('error: %s\n\n' % model[record_type]['error'])

                # Update record in the database
                with open('results.json') as f:
                    model = DM(f)
                dbase.update_record(content=model.xml(), name=sim)
                                
                # Archive calculation and add to database
                dbase.add_tar(root_dir=run_directory, name=sim)
                
                # Remove simulation directory
                os.chdir(run_directory)
                removecalc(os.path.join(run_directory, sim))
            
            # Else if bid(sim) failed
            else:
                bidfailcount += 1
                
                # Stop unproductive worker after 10 consecutive bid fails
                if bidfailcount > 10:
                    sys.exit(0)
                
                # Pause for 10 seconds before trying again
                time.sleep(10)
            
            # Regenerate flist and flush log file
            flist = os.listdir(run_directory)
            log.flush()
            os.fsync(log.fileno())
        
def bid(sim):
    """Bids for chance to run simulation"""
    try:
        # Wait to make sure sim is not being deleted
        time.sleep(1)
        
        # Check if bid already exists
        for fname in os.listdir(sim):
            if fname[-4:] == '.bid':
                return False

        # Place a bid
        pid = os.getpid()
        with open(os.path.join(sim, str(pid)+'.bid'), 'w') as f:
            f.write('bid for pid: %i' % pid)
        
        # Wait to make sure all bids are in
        time.sleep(1)

        # Check bids
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
    """Uniquely find file accoring to wildcard string"""
    
    # glob any file matching path string (with wildcards)
    file = glob.glob(path_string)
    
    # Return if exactly 1 match found, otherwise issue an error
    if len(file) == 1:
        return file[0]
    elif len(file) == 0:
        raise ValueError('Cannot find file matching ' + path_string)
    else:
        raise ValueError('Multiple files found matching '+ path_string)
    
        
def process_input(input_dict):
    """Processes the runner.in input commands"""
    
    input_dict['dbase'] = iprPy.database_fromdict(input_dict)
    input_dict['run_directory'] = os.path.abspath(input_dict['run_directory'])
    input_dict['orphan_directory'] = input_dict.get('orphan_directory', None)
    
def removecalc(dir):
    """Removes calculation instance directories leaving .bid files for last"""
    
    # Loop over all files and directories in dir
    for fname in glob.iglob(os.path.join(dir, '*')):
        
        # If fname is a directory, try rmtree up to 10 times
        if os.path.isdir(fname):
            tries = 0
            while tries < 10:
                try:
                    shutil.rmtree(fname)
                    break
                except:
                    tries += 1
        
        # If fname is a non-.bid file, try remove up to 10 times
        elif os.path.isfile(fname) and fname[-4:] != '.bid':
            tries = 0
            while tries < 10:
                try:
                    os.remove(fname)
                    break
                except:
                    tries += 1
    
    # Use rmtree on remaining content (hopefully only *.bid and the dir folder)
    shutil.rmtree(dir)
    
if __name__ == '__main__':
    main(*sys.argv[1:])