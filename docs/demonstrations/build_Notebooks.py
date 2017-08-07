"""
==================
build_Notebooks.py
==================

This script generates the demonstration Notebooks for all implemented
calculations by filling in the template Notebooks.

1. It searches the calculation folders for any *_template.ipynb files.
2. The contents of all other files in the calculation folder are read in.  For
   .py files, the contained primary functions are identified.
3. The contents of the files are then used to replace delimited terms in the 
   Jupyter Notebooks:
   
   - The leading delimiter is ^fill^
   - The trailing delimiter is ^here^
   - The full contents of a file will be added if the filename is given 
     between the delimiters:
        
        ^fill^README.md^here^
     
   - The Python code for a specific function will be added if the filename
     followed by the function name in parenthesis is added:
        
        ^fill^calc.py(main)^here^

NOTE: After building, check that the Notebooks still work.  If changes need to
be made, make them to the files in the calculation folders NOT to the
generated Notebooks!
"""

from __future__ import absolute_import, division, print_function

import os 
import glob
import iprPy

def ipynbformat(lines):
    """Converts raw file lines to the JSON content lines used in ipynb"""
    
    line = repr(lines[0])[1:-1].replace('"', r'\"')
    alllines = line + '",\n'
    for i in xrange(1, len(lines)-1):
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
    for i in xrange(len(lines)):
        if lines[i].strip() != '':
        
            if lines[i][0] != ' ' and name is not None:
                yield name, lines[start:i]
                name = None
                
            if lines[i][:4] == 'def ':
                start = i
                name = lines[i][4:].split('(')[0].strip()
                
indexmd = '# List of Jupyter Calculation Notebooks'
                
for templatepath in glob.iglob(os.path.join(iprPy.rootdir, 'calculations','*', '*_template.ipynb')):
    calcname = os.path.basename(templatepath).replace('_template.ipynb', '')
    calcpath = os.path.dirname(templatepath)
    
    with open(templatepath) as ftemplate:
        template = ftemplate.read()
    calcname = os.path.basename(templatepath).replace('_template.ipynb', '')

    fill_terms = {}
    for fpath in glob.iglob(os.path.join(calcpath, '*')):
        fname = os.path.basename(fpath)
        with open(fpath) as f:
            lines = f.readlines()
        fill_terms[fname] = ipynbformat(lines)
            
        if os.path.splitext(fname)[1] == '.py':
            for name, funclines in parsefunctions(lines):
                fill_terms[fname+'('+name+')'] = ipynbformat(funclines)
        
    test = iprPy.tools.filltemplate(template, fill_terms, '^fill^', '^here^')
    with open(calcname+'.ipynb', 'w') as ftest:
        ftest.write(test)
        
    indexmd += '\n\n## ['+calcname+']('+calcname+'.ipynb)'
    
    with open('index.md', 'w') as f:
        f.write(indexmd)
