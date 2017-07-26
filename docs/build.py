import os
import glob
import iprPy
import shutil

def main():
    buildcalculations()
    buildrecords()
    builddatabases()

def buildcalculations():
    indextemplate = """<nameheader>

.. toctree::
    :maxdepth: 1

    intro
    theory
    calc
"""

    calctemplate = """<scriptheader>

Calculation script functions
----------------------------
.. automodule:: iprPy.calculations.<name>.calc_<name>
    :members:
    :undoc-members:
    :show-inheritance:
    """
    
    pypath = '../iprPy/calculations'
    rstpath = 'source/calculations'
    
    # Identify all module folders
    for dir in glob.iglob(os.path.join(pypath, '*')):
        if os.path.isdir(dir):
            name = os.path.basename(dir)
            if not os.path.isdir(os.path.join(rstpath, name)):
                os.mkdir(os.path.join(rstpath, name))
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name),
                                         name,
                                         '='*len(name)])
            indexrst = os.path.join(rstpath, name, 'index.rst')
            with open(indexrst, 'w') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))
                                                 
            # Create calc.rst
            d = {}
            pyname = 'calc_' + name + '.py'
            d['scriptheader'] = '\n'.join(['=' * len(pyname),
                                           pyname,
                                           '='*len(pyname)])
            d['name'] = name
            calcrst = os.path.join(rstpath, name, 'calc.rst')
            with open(calcrst, 'w') as f:
                f.write(iprPy.tools.filltemplate(calctemplate, d, '<', '>'))
            
            # theory.md
            infile = os.path.join(pypath, name, 'theory.md')
            outfile = os.path.join(rstpath, name, 'theory.md')
            with open(infile) as f:
                theory = f.read()
            with open(outfile, 'w') as f:
                f.write(parsemath(theory))
                        
            # intro.md
            infile = os.path.join(pypath, name, 'README.md')
            outfile = os.path.join(rstpath, name, 'intro.md')
            with open(infile) as f:
                readme = f.read()
            index = readme.index('## Introduction') + 1
            with open(outfile, 'w') as f:
                f.write(parsemath(readme[index:]))
                
def buildrecords():
    indextemplate = """<nameheader>

.. toctree::
    :maxdepth: 1

    intro
"""
    
    pypath = '../iprPy/records'
    rstpath = 'source/records'
    
    # Identify all module folders
    for dir in glob.iglob(os.path.join(pypath, '*')):
        if os.path.isdir(dir):
            name = os.path.basename(dir)
            if not os.path.isdir(os.path.join(rstpath, name)):
                os.mkdir(os.path.join(rstpath, name))
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name),
                                         name,
                                         '='*len(name)])
            indexrst = os.path.join(rstpath, name, 'index.rst')
            with open(indexrst, 'w') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))

            # intro.md
            infile = os.path.join(pypath, name, 'README.md')
            outfile = os.path.join(rstpath, name, 'intro.md')
            with open(infile) as f:
                readme = f.read()
            index = readme.index('## Introduction') + 1
            with open(outfile, 'w') as f:
                f.write(parsemath(readme[index:]))

def builddatabases():
    indextemplate = """<nameheader>

.. toctree::
    :maxdepth: 1

    intro
"""
    
    pypath = '../iprPy/databases'
    rstpath = 'source/databases'
    
    # Identify all module folders
    for dir in glob.iglob(os.path.join(pypath, '*')):
        if os.path.isdir(dir):
            name = os.path.basename(dir)
            if not os.path.isdir(os.path.join(rstpath, name)):
                os.mkdir(os.path.join(rstpath, name))
            
            # Create index.rst
            d = {}
            d['nameheader'] = '\n'.join(['=' * len(name),
                                         name,
                                         '='*len(name)])
            indexrst = os.path.join(rstpath, name, 'index.rst')
            with open(indexrst, 'w') as f:
                f.write(iprPy.tools.filltemplate(indextemplate, d,'<', '>'))

            # intro.md
            infile = os.path.join(pypath, name, 'README.md')
            outfile = os.path.join(rstpath, name, 'intro.md')
            with open(infile) as f:
                readme = f.read()
            index = readme.index('## Introduction') + 1
            with open(outfile, 'w') as f:
                f.write(parsemath(readme[index:]))
                
                
def parsemath(st):
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