from __future__ import print_function, division, absolute_import
import os
import sys
import glob
import iprPy
import shutil
import pypandoc

def main():
    
    buildcalculations()
    buildrecords()
    builddatabases()
    copynotebooks()

def buildcalculations():
    """Builds doc/source pages for all calculation styles implemented in iprPy"""
    
    # Specify path to Python code for the iprPy.calculations submodule
    pypath = os.path.join(iprPy.rootdir, 'calculation')
    
    # Specify relative path to doc/source folder for calculations
    docpath = os.path.join(iprPy.rootdir, '..', 'doc', 'source', 'calculation')
    
    # Define template index
    indextemplate = """<nameheader>

.. toctree::
    :maxdepth: 1

    intro
    theory
    parameters
    calc"""
    
    scripttemplate = """<scriptheader>

Calculation script functions
----------------------------
.. automodule:: iprPy.calculation.<name>.calc_<name>
    :members:
    :undoc-members:
    :show-inheritance:"""
    
    # Remove existing doc source
    if os.path.isdir(docpath):
        shutil.rmtree(docpath)
    os.makedirs(docpath)
    
    # Loop over all implemented calculation styles
    for name in iprPy.calculation.loaded.keys():
        print(name)
        sys.stdout.flush()
        pydir = os.path.join(pypath, name)
        docdir = os.path.join(docpath, name)
        os.mkdir(docdir)
        
        # Verify calculation is a submodule
        if os.path.isdir(pydir):
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name), name, '='*len(name)])
            with open(os.path.join(docdir, 'index.rst'), 'w') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))
            
            # Create calc.rst
            d = {}
            pyname = 'calc_' + name + '.py'
            d['scriptheader'] = '\n'.join(['=' * len(pyname), pyname, '='*len(pyname)])
            d['name'] = name
            with open(os.path.join(docdir, 'calc.rst'), 'w') as f:
                f.write(iprPy.tools.filltemplate(scripttemplate, d, '<', '>'))
            
            # copy README.md to intro.rst
            copy_md2rst(os.path.join(pydir, 'README.md'),
                        os.path.join(docdir, 'intro.rst'))
            
            # copy theory.md to theory.rst
            copy_md2rst(os.path.join(pydir, 'theory.md'),
                        os.path.join(docdir, 'theory.rst'))
            
            # copy parameters.md to parameters.rst
            copy_md2rst(os.path.join(pydir, 'parameters.md'),
                        os.path.join(docdir, 'parameters.rst'))

def buildrecords():
    """Builds doc/source pages for all record styles implemented in iprPy"""
    
    # Specify path to Python code for the iprPy.record submodule
    pypath = os.path.join(iprPy.rootdir, 'record')
    
    # Specify relative path to doc/source folder for record
    docpath = os.path.join(iprPy.rootdir, '..', 'doc', 'source', 'record')
    
    indextemplate = """<nameheader>

.. toctree::
    :maxdepth: 1

    intro"""
    
    # Remove existing doc source
    if os.path.isdir(docpath):
        shutil.rmtree(docpath)
    os.makedirs(docpath)
    
   # Loop over all implemented record styles
    for name in iprPy.record.loaded.keys():
        print(name)
        sys.stdout.flush()
        pydir = os.path.join(pypath, name)
        docdir = os.path.join(docpath, name)
        os.mkdir(docdir)
        
         # Verify record is a submodule
        if os.path.isdir(pydir):
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name), name, '='*len(name)])
            with open(os.path.join(docdir, 'index.rst'), 'w') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))
            
            # copy README.md to intro.rst
            copy_md2rst(os.path.join(pydir, 'README.md'),
                        os.path.join(docdir, 'intro.rst'))

def builddatabases():
    """Builds doc/source pages for all database styles implemented in iprPy"""
    
    # Specify path to Python code for the iprPy.database submodule
    pypath = os.path.join(iprPy.rootdir, 'database')
    
    # Specify relative path to doc/source folder for database
    docpath = os.path.join(iprPy.rootdir, '..', 'doc', 'source', 'database')
    
    indextemplate = """<nameheader>

.. toctree::
    :maxdepth: 1

    intro"""
    
    # Remove existing doc source
    if os.path.isdir(docpath):
        shutil.rmtree(docpath)
    os.makedirs(docpath)
    
   # Loop over all implemented database styles
    for name in iprPy.database.loaded.keys():
        print(name)
        sys.stdout.flush()
        pydir = os.path.join(pypath, name)
        docdir = os.path.join(docpath, name)
        os.mkdir(docdir)
        
         # Verify database is a submodule
        if os.path.isdir(pydir):
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name), name, '='*len(name)])
            with open(os.path.join(docdir, 'index.rst'), 'w') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))
            
            # copy README.md to intro.rst
            copy_md2rst(os.path.join(pydir, 'README.md'),
                        os.path.join(docdir, 'intro.rst'))

def copynotebooks():
    
    # Specify path to Jupyter Notebooks
    pypath = os.path.join(iprPy.rootdir, '..', 'notebook')
    
    # Specify relative path to doc/source folder for database
    docpath = os.path.join(iprPy.rootdir, '..', 'doc', 'source', 'notebook')
    
    # Remove existing doc source
    if os.path.isdir(docpath):
        shutil.rmtree(docpath)
    os.makedirs(docpath)
    
    # Make calculationfiles folder
    os.mkdir(os.path.join(docpath, 'calculationfiles'))
    
    for oldpath in glob.iglob(os.path.join(pypath, '*.ipynb')):
        oldname = os.path.basename(oldpath)
        newname = oldname.replace(' ', '_')
        print(newname)
        newpath = os.path.join(docpath, newname)
        shutil.copy(oldpath, newpath)
    
    
        
def copy_md2rst(infile, outfile):
    
    # Read infile
    try:
        with open(infile) as f:
            text = f.read()
    except:
        text = ''
    
    # Strip top of file
    try:
        text = text[text.index('## Introduction') + 1:]
    except:
        pass
    
    # Write to outfile
    with open(outfile, 'w') as f:
        f.write(pypandoc.convert_text(text, 'rst', format='md').replace('\r\n', '\n'))

def parsemath(st):
    """Alters the Latex encoding so that it is properly interpreted by Sphinx"""
    count = 0
    end = len(st)
    while True:
        try:
            i = st.rindex('$', 0, end)
        except:
            break
        if i>0 and st[i-1] == '$':
            end = i-1
            if end < 0:
                break
        else:
            if count % 2 == 0:
                st = st[:i] + '$``' + st[i+1:]
            else:
                st = st[:i] + '``$' + st[i+1:]
            count += 1
            end = i
    return st

if __name__ == '__main__':
    main()