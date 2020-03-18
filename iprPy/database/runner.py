# Standard Python libraries
import os
import sys
import subprocess
import random
import shutil
import time
import glob
import datetime
import requests

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import rootdir

def runner(dbase, run_directory, orphan_directory=None, hold_directory=None):
    """
    High-throughput calculation runner.
    
    Parameters
    ----------
    dbase : iprPy.Database
        The database to interact with.
    run_directory : str
        The path to the directory where the calculation instances to run are
        located.
    orphan_directory : str, optional
        The path for the orphan directory where incomplete calculations are
        moved.  If None (default) then will use 'orphan' at the same level as
        the run_directory.
    hold_directory : str, optional
        The path for the hold directory where tar archives that failed to be
        uploaded are moved to.  If None (default) then will use 'hold' at the
        same level as the run_directory.
    """
    # Get path to Python executable running this script
    py_exe = sys.executable
    if py_exe is None:
        py_exe = 'python'
    
    # Get absolute path to run_directory
    run_directory = os.path.abspath(run_directory)
    
    # Get original working directory
    original_dir = os.getcwd()
    
    # Define runner log file
    d = datetime.datetime.now()
    pid = os.getpid()
    runner_log_dir = os.path.join(os.path.dirname(rootdir),
                                  'runner-logs')
    if not os.path.isdir(runner_log_dir):
        os.makedirs(runner_log_dir)
    log_file = os.path.join(runner_log_dir,
                            '%04i-%02i-%02i-%02i-%02i-%06i-%i.log'
                            % (d.year, d.month, d.day, d.minute, d.second,
                               d.microsecond, pid))
    
    # Set default orphan_directory
    if orphan_directory is None:
        orphan_directory = os.path.join(os.path.dirname(run_directory),
                                        'orphan')
        
    # Set default orphan_directory
    if hold_directory is None:
        hold_directory = os.path.join(os.path.dirname(run_directory), 'hold')
    
    # Start runner log file
    with open(log_file, 'a') as log:
        
        # Change to the run directory
        os.chdir(run_directory)
        
        # Initialize bidfailcount counter
        bidfailcount = 0
        
        # Announce the runner's pid
        print(f'Runner started with pid {pid}', flush=True)
        
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
                
                # Check that the calculation has calc_*.py, calc_*.in and
                # record in the database
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
                    shutil.make_archive(os.path.join(orphan_directory, sim),
                                        'gztar', root_dir=run_directory,
                                        base_dir=sim)
                    removecalc(os.path.join(run_directory, sim))
                    flist = os.listdir(run_directory)
                    continue
                
                # Check if any files in the calculation folder are incomplete
                # records
                error_flag = False
                ready_flag = True
                
                for fname in glob.iglob('*'):
                    parent_sim, ext = os.path.splitext(os.path.basename(fname))
                    if ext in ('.json', '.xml'):
                        parent = DM(fname)
                        try:
                            status = parent.find('status')
                            
                            # Check parent record in database to see if it has completed
                            if status == 'not calculated':
                                parent_record = dbase.get_record(name=parent_sim)
                                try:
                                    status = parent_record.content.find('status')
                                    
                                    # Mark flag if still incomplete
                                    if status == 'not calculated':
                                        ready_flag = False
                                        break
                                    
                                    # Skip if parent calculation failed
                                    elif status == 'error':
                                        with open(os.path.basename(fname), 'w') as f:
                                            parent_record.content.json(fp=f, indent=4)
                                        error_flag = True
                                        error_message = 'parent calculation issued an error'
                                        break
                                    
                                    # Ignore if unknown status
                                    else:
                                        raise ValueError('unknown status')
                                        
                                # Copy parent record to calculation folder if it is now complete
                                except:
                                    with open(os.path.basename(fname), 'w') as f:
                                        parent_record.content.json(fp=f, indent=4)
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
                    run = subprocess.Popen([py_exe, calc_py, calc_in, sim],
                                           stderr=subprocess.PIPE)
                    error_message = run.stderr.read()
                    try:
                        error_message = error_message.decode('UTF-8')
                    except:
                        pass
                    
                    # Load results.json
                    try:
                        model = DM('results.json')
                    
                    # Throw errors if no results.json
                    except:
                        error_flag = True
                    assert not error_flag, error_message
                    log.write('sim calculated successfully\n')
                
                # Catch any errors and build results.json
                except:
                    model = record.content
                    keys = list(model.keys())
                    record_type = keys[0]
                    model[record_type]['status'] = 'error'
                    model[record_type]['error'] = str(sys.exc_info()[1])
                    with open('results.json', 'w') as f:
                        model.json(fp=f, indent=4)
                    log.write('error: %s\n' % model[record_type]['error'])
                
                # Update record
                tries = 0
                while tries < 10:
                    try:
                        dbase.update_record(content=model, name=sim)
                        break
                    except:
                        tries += 1
                if tries == 10:
                    os.chdir(run_directory)
                    log.write('failed to update record\n')
                else:
                    # Archive calculation and add to database or hold_directory
                    try:
                        dbase.add_tar(root_dir=run_directory, name=sim)
                    except:
                        log.write('failed to upload archive\n')
                        if not os.path.isdir(hold_directory):
                            os.makedirs(hold_directory)
                        shutil.move(sim+'.tar.gz', hold_directory)
                    os.chdir(run_directory)
                    removecalc(os.path.join(run_directory, sim))
                log.write('\n')
            
            # Else if bid(sim) failed
            else:
                bidfailcount += 1
                
                # Stop unproductive worker after 10 consecutive bid fails
                if bidfailcount > 10:
                    print("Didn't find an open simulation", flush=True)
                    break
                
                # Pause for 10 seconds before trying again
                time.sleep(10)
            
            # Regenerate flist and flush log file
            flist = os.listdir(run_directory)
            log.flush()
            os.fsync(log.fileno())
        print('No simulations left to run', flush=True)
        os.chdir(original_dir)

def bid(sim):
    """
    Bids for the chance to run a calculation instance. Used to help avoid
    runner collisions.
    
    Parameters
    ----------
    sim : str
        The path to the calculation to try bidding on.
        
    Returns
    -------
    bool
        True if bidding is successful, False if bidding fails.
    """
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

def get_file(path):
    """
    Uniquely find a single file according to a wildcard string.
    
    Parameters
    ----------
    path : str
        The str path with wildcards to use for identifying the file.
        
    Returns
    -------
    str
        The actual str path to the matching file.
    
    Raises
    ------
    ValueError
        If multiple or no matching files found.
    """
    
    # glob any file matching path string (with wildcards)
    file = glob.glob(path)
    
    # Return if exactly 1 match found, otherwise issue an error
    if len(file) == 1:
        return file[0]
    elif len(file) == 0:
        raise ValueError('Cannot find file matching ' + path)
    else:
        raise ValueError('Multiple files found matching '+ path)

def removecalc(dir):
    """
    Removes the specified calculation instance directory leaving .bid files
    for last to help avoid runner collisions.
    
    Parameters
    ----------
    dir : str
        The path to the calculation instance directory to delete.
    """
    
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
    tries = 0
    while tries < 10:
        try:
            shutil.rmtree(dir)
            break
        except:
            tries += 1
            if tries == 10:
                print('failed to delete', os.path.basename(dir), flush=True)