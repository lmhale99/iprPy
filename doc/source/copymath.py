from __future__ import print_function, division, absolute_import
import os
import sys
import glob
import shutil

def main():
    
    copymath()

def copymath():
    """Copies the .rst files containing math sections from 'source' to 'rst'"""
    
    # Copy over all intro.rst files
    for source in glob.iglob(os.path.join('source', '*', '*', 'intro.rst')):
        print(source)
        sys.stdout.flush()
        rst = source.replace('source', 'rst', 1)
        if not os.path.isdir(os.path.dirname(rst)):
            os.makedirs(os.path.dirname(rst))
        shutil.copy(source, rst)
        
    # Copy over all theory.rst files
    for source in glob.iglob(os.path.join('source', '*', '*', 'theory.rst')):
        print(source)
        sys.stdout.flush()
        rst = source.replace('source', 'rst', 1)
        if not os.path.isdir(os.path.dirname(rst)):
            os.makedirs(os.path.dirname(rst))
        shutil.copy(source, rst)

if __name__ == '__main__':
    main()