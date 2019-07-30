import io
import os
import sys
import glob
from pathlib import Path

import iprPy

def main(*calcnames):
    """
    Generates Jupyter Notebooks from the templates.  Note that this overwrites
    the Jupyter Notebooks that have templates!  If you only want to update one
    or two, give the calculation names as inline arguments.
    
    Parameters
    calcnames : list
        Indicates that a limited set of Jupyter Notebooks is to be generated
        from the templates.  An empty list (default value) will generate all
        Notebooks
    """
    # Specify directory paths
    iprPydir = Path(iprPy.rootdir, '..')
    notebookdir = Path(iprPydir, 'notebook')
    templatedir = Path(iprPydir, 'notebook', 'template')
    calcdir = Path(iprPy.rootdir, 'calculation')
    
    # Loop over all template Notebooks
    for templatepath in templatedir.glob('*.ipynb'):
        
        # Get calculation's name
        calcname = templatepath.stem
        if len(calcnames) > 0 and calcname not in calcnames:
            continue
        
        # Read in template file
        with io.open(templatepath, encoding='UTF-8') as templatefile:
            template = templatefile.read()
        
        # Build content_dict containing calculation content
        content_dict = {}
        for contentpath in Path(calcdir, calcname).glob('*'):
            if (contentpath.is_file() and contentpath.suffix not in ['.pyc','.pyd']):
                contentname = contentpath.name
                
                # Save full file contents according to the file's name
                with io.open(contentpath, encoding='UTF-8') as contentfile:
                    lines = contentfile.readlines()
                content_dict[contentname] = ipynbformat(lines)
                
                # Save functions as file's name plus function name
                if contentpath.suffix == '.py':
                
                    for functionname, functionlines in parsefunctions(lines):
                        name = f'{contentname}({functionname})'
                        content_dict[name] = ipynbformat(functionlines)
        
        # Fill in template and save complete Notebook
        notebook = iprPy.tools.filltemplate(template, content_dict, '^fill^', '^here^')
        notebookpath = Path(notebookdir, f'{calcname}.ipynb')
        with io.open(notebookpath, 'w', encoding='UTF-8') as notebookfile:
            notebookfile.write(notebook)
    
    build_index(notebookdir)

def build_index(notebookdir):
    
    index = '# List of Jupyter Calculation Notebooks'
    
    for notebookpath in notebookdir.glob('*.ipynb'):
    
        # Get calculation's name
        calcname = notebookpath.stem
        
        index += '\n\n## ['+calcname+']('+calcname+'.ipynb)'
    
    indexpath = Path(notebookdir, 'README.md')
    with open(indexpath, 'w') as indexfile:
        indexfile.write(index)

def ipynbformat(lines):
    """Converts raw file lines to the JSON content lines used in ipynb"""
    
    line = repr(lines[0])[1:-1].replace('"', r'\"')
    alllines = line + '",\n'
    for i in range(1, len(lines)-1):
        line = repr(lines[i])[1:-1].replace('"', r'\"')
        alllines += '    "' + line + '",\n'
    line = repr(lines[-1])[1:-1].replace('"', r'\"')
    alllines += '    "' + line
    
    return alllines.replace(r"\'", r"'")

def parsefunctions(lines):
    """
    Parses out the lines of a Python script corresponding to primary functions.
    """
    name = None
    for i in range(len(lines)):
        if lines[i].strip() != '':
        
            if lines[i][0] != ' ' and name is not None:
                yield name, lines[start:i]
                name = None
                
            if lines[i][:4] == 'def ':
                start = i
                name = lines[i][4:].split('(')[0].strip()
                
if __name__ == '__main__':
    main(*sys.argv[1:])