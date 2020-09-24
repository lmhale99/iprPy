from pathlib import Path
import os
import sys
import glob
import iprPy
import shutil
import pypandoc

rootdir = 'E:/Python-packages/iprPy/iprPy'

def main():
    
    buildcalculations()
    buildrecords()
    builddatabases()
    copynotebooks()

def buildcalculations():
    """Builds doc/source pages for all calculation styles implemented in iprPy"""
    
    # Specify path to Python code for the iprPy.calculations submodule
    pypath = Path(rootdir, 'calculation')
    
    # Specify relative path to doc/source folder for calculations
    docpath = Path(rootdir, '..', 'doc', 'source', 'calculation')
    
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
    if docpath.is_dir():
        cleantree(docpath)
    
    # Loop over all implemented calculation styles
    for name in iprPy.calculation.loaded.keys():
        print(name, flush=True)
        calc = iprPy.load_calculation(name)
        
        pydir = Path(pypath, name)
        docdir = Path(docpath, name)
        docdir.mkdir(parents=True)
        
        # Verify calculation is a submodule
        if pydir.is_dir():
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name), name, '='*len(name)])
            with open(Path(docdir, 'index.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))
            
            # Create calc.rst
            d = {}
            pyname = 'calc_' + name + '.py'
            d['scriptheader'] = '\n'.join(['=' * len(pyname), pyname, '='*len(pyname)])
            d['name'] = name
            with open(Path(docdir, 'calc.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(iprPy.tools.filltemplate(scripttemplate, d, '<', '>'))

            # Copy README.md to intro.rst
            copy_md2rst(Path(pydir, 'README.md'),
                        Path(docdir, 'intro.rst'))
            
            # Copy theory.md to theory.rst
            copy_md2rst(Path(pydir, 'theory.md'),
                        Path(docdir, 'theory.rst'))
            
            # Create parameters.md
            with open(Path(pydir, 'parameters.md'), 'w', encoding='utf-8') as f:
                f.write(calc.templatedoc)

            # Copy parameters.md to parameters.rst
            copy_md2rst(Path(pydir, 'parameters.md'),
                        Path(docdir, 'parameters.rst'))

            # Create empty calc_.in file from template
            t = {}
            for key in calc.allkeys:
                t[key] = ''
            infile = iprPy.tools.filltemplate(calc.template, t, '<', '>')
            with open(Path(pydir, f'calc_{calc.style}.in'), 'w', encoding='utf-8') as f:
                f.write(infile)

def buildrecords():
    """Builds doc/source pages for all record styles implemented in iprPy"""
    
    # Specify path to Python code for the iprPy.record submodule
    pypath = Path(rootdir, 'record')
    
    # Specify relative path to doc/source folder for record
    docpath = Path(rootdir, '..', 'doc', 'source', 'record')
    
    indextemplate = """<nameheader>

.. toctree::
    :maxdepth: 1

    intro"""
    
    # Remove existing doc source
    if docpath.is_dir():
        cleantree(docpath)
    
   # Loop over all implemented record styles
    for name in iprPy.record.loaded.keys():
        print(name, flush=True)
        pydir = Path(pypath, name)
        docdir = Path(docpath, name)
        docdir.mkdir(parents=True)
        
         # Verify record is a submodule
        if pydir.is_dir():
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name), name, '='*len(name)])
            with open(Path(docdir, 'index.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))
            
            # copy README.md to intro.rst
            copy_md2rst(Path(pydir, 'README.md'),
                        Path(docdir, 'intro.rst'))

def builddatabases():
    """Builds doc/source pages for all database styles implemented in iprPy"""
    
    # Specify path to Python code for the iprPy.database submodule
    pypath = Path(rootdir, 'database')
    
    # Specify relative path to doc/source folder for database
    docpath = Path(rootdir, '..', 'doc', 'source', 'database')
    
    indextemplate = """<nameheader>

.. toctree::
    :maxdepth: 1

    intro"""
    
    # Remove existing doc source
    if docpath.is_dir():
        cleantree(docpath)
    
   # Loop over all implemented database styles
    for name in iprPy.database.loaded.keys():
        print(name, flush=True)
        pydir = Path(pypath, name)
        docdir = Path(docpath, name)
        docdir.mkdir(parents=True)
        
         # Verify database is a submodule
        if pydir.is_dir():
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name), name, '='*len(name)])
            with open(Path(docdir, 'index.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))
            
            # copy README.md to intro.rst
            copy_md2rst(Path(pydir, 'README.md'),
                        Path(docdir, 'intro.rst'))

def copynotebooks():
    
    # Specify path to Jupyter Notebooks
    pypath = Path(rootdir, '..', 'notebook')
    
    # Specify relative path to doc/source folder for database
    docpath = Path(rootdir, '..', 'doc', 'source', 'notebook')
    
    # Remove existing doc source
    if docpath.is_dir():
        cleantree(docpath)
    
    # Make calculationfiles folder
    Path(docpath, 'calculationfiles').mkdir(parents=True)
    
    for oldpath in pypath.glob('*.ipynb'):
        oldname = oldpath.name
        newname = oldname.replace(' ', '_')
        print(newname)
        newpath = Path(docpath, newname)
        shutil.copy(oldpath, newpath)

def cleantree(path):
    try:
        shutil.rmtree(path)
    except:
        try:
            shutil.rmtree(path)
        except:
            pass
    
    try:
        os.makedirs(path)
    except:
        pass

def copy_md2rst(infile, outfile):
    
    # Read infile
    try:
        with open(infile, encoding='UTF-8') as f:
            text = f.read()
    except:
        text = ''
    
    # Strip top of file
    try:
        text = text[text.index('## Introduction') + 1:]
    except:
        pass
    
    # Write to outfile
    with open(outfile, 'w', newline='\n', encoding='UTF-8') as f:
        f.write(pypandoc.convert_text(text, 'rst', format='md', encoding='UTF-8').replace('\r\n', '\n'))

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