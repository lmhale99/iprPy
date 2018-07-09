#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import io
import os
import glob
import iprPy
from iprPy.compatibility import range

def main():
    
    # Specify directory paths
    iprPydir = os.path.join(iprPy.rootdir, '..')
    notebookdir = os.path.join(iprPydir, 'notebook')
    templatedir = os.path.join(iprPydir, 'notebook', 'template')
    calcdir = os.path.join(iprPy.rootdir, 'calculation')
    
    # Loop over all template Notebooks
    templatepaths = os.path.join(templatedir, '*.ipynb')
    for templatepath in glob.iglob(templatepaths):
        
        # Get calculation's name
        calcname = os.path.splitext(os.path.basename(templatepath))[0]
        
        # Read in template file
        with io.open(templatepath, encoding='UTF-8') as templatefile:
            template = templatefile.read()
        
        # Build content_dict containing calculation content
        content_dict = {}
        for contentpath in glob.iglob(os.path.join(calcdir, calcname, '*')):
            if (os.path.isfile(contentpath) 
                and os.path.splitext(contentpath)[1] not in ['.pyc','.pyd']):
                contentname = os.path.basename(contentpath)
                
                # Save full file contents according to the file's name
                with io.open(contentpath, encoding='UTF-8') as contentfile:
                    lines = contentfile.readlines()
                content_dict[contentname] = ipynbformat(lines)
                
                # Save functions as file's name plus function name
                if os.path.splitext(contentname)[1] == '.py':
                
                    for functionname, functionlines in parsefunctions(lines):
                        name = contentname+'('+functionname+')'
                        content_dict[name] = ipynbformat(functionlines)
        
        # Fill in template and save complete Notebook
        notebook = iprPy.tools.filltemplate(template, content_dict,
                                            '^fill^', '^here^')
        notebookpath = os.path.join(notebookdir, calcname+'.ipynb')
        with io.open(notebookpath, 'w', encoding='UTF-8') as notebookfile:
            notebookfile.write(notebook)
    
    build_index(notebookdir)

def build_index(notebookdir):
    
    index = '# List of Jupyter Calculation Notebooks'
    
    notebookpaths = os.path.join(notebookdir, '*.ipynb')
    for notebookpath in glob.iglob(notebookpaths):
    
        # Get calculation's name
        calcname = os.path.splitext(os.path.basename(notebookpath))[0]
        
        index += '\n\n## ['+calcname+']('+calcname+'.ipynb)'
    
    indexpath = os.path.join(notebookdir, 'README.md')
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
    main()