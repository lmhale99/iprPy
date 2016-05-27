#!/usr/bin/env python
import shutil
import sys

def main(*args):
    
    #Read in input script terms
    run_directory, lib_directory = __initial_setup(*args)
    try:
        shutil.rmtree(run_directory)
    except:
        pass
    try:
        shutil.rmtree(lib_directory)
    except:
        pass

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
        raise ValueError('destroy.py input requires both run_directory and lib_directory')
    
if __name__ == '__main__':
    main(*sys.argv[1:])