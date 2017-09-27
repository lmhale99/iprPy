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

def buildcalculations():
    """Builds doc/source pages for all calculation styles implemented in iprPy"""
    
    # Specify relative path to Python code for the iprPy.calculations submodule
    pypath = '../iprPy/calculations'
    
    # Specify relative path to doc/source folder for calculations
    docpath = 'source/calculations'
    
    # Load template file(s)
    with open(os.path.join('templates', 'calcindex.template')) as f:
        indextemplate = f.read()
        
    with open(os.path.join('templates', 'calcscript.template')) as f:
        scripttemplate = f.read()
    
    # Remove existing doc source
    shutil.rmtree(docpath)
    
    # Loop over all implemented calculation styles
    for name in iprPy.calculation_styles():
        print(name)
        sys.stdout.flush()
        pydir = os.path.join(pypath, name)
        docdir = os.path.join(docpath, name)
        
        # Verify calculation is a submodule
        if os.path.isdir(pydir):
            
            # Create doc folder
            if not os.path.isdir(docdir):
                os.makedirs(docdir)
            
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
            
            # copy theory.md to theory.rst
            copy_md2rst(os.path.join(pydir, 'theory.md'),
                        os.path.join(docdir, 'theory.rst'))
                        
            # copy README.md to intro.rst
            copy_md2rst(os.path.join(pydir, 'README.md'),
                        os.path.join(docdir, 'intro.rst'))
                
def buildrecords():
    """Builds doc/source pages for all record styles implemented in iprPy"""
    
    # Specify relative path to Python code for the iprPy.records submodule
    pypath = '../iprPy/records'
    
    # Specify relative path to doc/source folder for records
    docpath = 'source/records'
    
    # Load template file(s)
    with open(os.path.join('templates', 'recordindex.template')) as f:
        indextemplate = f.read()
    
    # Remove existing doc source
    shutil.rmtree(docpath)
    
   # Loop over all implemented record styles
    for name in iprPy.record_styles():
        print(name)
        sys.stdout.flush()
        pydir = os.path.join(pypath, name)
        docdir = os.path.join(docpath, name)
        
         # Verify record is a submodule
        if os.path.isdir(pydir):
            
            # Create doc folder
            if not os.path.isdir(docdir):
                os.makedirs(docdir)
            
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
    
    # Specify relative path to Python code for the iprPy.databases submodule
    pypath = '../iprPy/databases'
    
    # Specify relative path to doc/source folder for databases
    docpath = 'source/databases'
    
    # Load template file(s)
    with open(os.path.join('templates', 'databaseindex.template')) as f:
        indextemplate = f.read()
    
    # Remove existing doc source
    shutil.rmtree(docpath)
    
    # Loop over all implemented database styles
    for name in iprPy.database_styles():
        print(name)
        sys.stdout.flush()
        pydir = os.path.join(pypath, name)
        docdir = os.path.join(docpath, name)
        
         # Verify record is a submodule
        if os.path.isdir(pydir):
            
            # Create doc folder
            if not os.path.isdir(docdir):
                os.makedirs(docdir)
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name), name, '='*len(name)])
            with open(os.path.join(docdir, 'index.rst'), 'w') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))

            # copy README.md to intro.rst
            copy_md2rst(os.path.join(pydir, 'README.md'),
                        os.path.join(docdir, 'intro.rst'))
                
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