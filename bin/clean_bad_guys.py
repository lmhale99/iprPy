# coding: utf-8
# Standard Python libraries
import os
import sys
from pathlib import Path
import shutil

# iprPy imports
import iprPy

def clean_bad_guys(database, run_directory, message):
    for calc_directory in Path(run_directory).glob('*'):
        calc_name = calc_directory.name
        print(calc_name)

        # Load content
        record = database.get_record(name=calc_name)
        model = record.model
        
        # Update status and error fields
        root = record.modelroot
        model[root]['status'] = 'error'
        model[root]['error'] = message
        
        # Save to execution directory
        with open(Path(calc_directory, 'results.json'), 'w', encoding='utf-8') as f:
            model.json(fp=f, indent=4, ensure_ascii=False)
            
        # Update record
        tries = 0
        #while tries < 10:
        #    try:
        database.update_record(style=record.style, model=model, name=calc_name)
        #        break
        #    except:
        #        tries += 1
        #if tries == 10:
        #    print(f'failed to update record {calc_name}', flush=True)
        #else:
        #    try:
                # tar.gz calculation and add to database
        database.add_tar(style=record.style, root_dir=run_directory, name=calc_name)
        #    except:
        #        print(f'failed to upload archive {calc_name}', flush=True)      
        #    else:    
        removecalc(calc_directory)
        

def removecalc(calc_directory):
    """
    Removes the specified calculation from the run directory leaving .bid files
    for last to help avoid runner collisions.

    Parameters
    ----------
    calc_directory : path-like object
        The calculation directory to delete.
    """
    
    # Loop over all files and directories in calc_directory
    for path in calc_directory.iterdir():

        # If path is a directory, try rmtree up to 10 times
        if path.is_dir():
            tries = 0
            while tries < 10:
                try:
                    shutil.rmtree(path)
                    break
                except:
                    tries += 1

        # If path is a non-.bid file, try remove up to 10 times
        elif path.is_file() and path.suffix != '.bid':
            tries = 0
            while tries < 10:
                try:
                    path.unlink()
                    break
                except:
                    tries += 1

    # Use rmtree on remaining content (hopefully only *.bid and the calc_directory folder)
    tries = 0
    while tries < 10:
        try:
            shutil.rmtree(calc_directory)
            break
        except:
            tries += 1
    
    if tries == 10:
        print(f'failed to delete {calc_directory}', flush=True)

if __name__ == '__main__':
    database = iprPy.load_database('iprhub')
    run_directory = iprPy.load_run_directory('iprhub_38')

    # Known runtime errors
    message = 'failed to finish in a reasonable time'
    #message = 'memory issue with neighborlist'
    #message = 'calculation always crashes before finishing'
    #message = 'bad elastic constants'

    # relax_liquid:melt errors
    #message = 'duplicate phase'
    #message = 'no liquid phase found at any temperature'
    #message = 'melt temperature too high: evaporated'
    #message = 'melt temperature too low: remained solid'

    clean_bad_guys(database, run_directory, message)
