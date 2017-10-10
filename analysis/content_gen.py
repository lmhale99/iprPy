from __future__ import print_function, division
import os
import glob
import shutil

import iprPy

# Define parameters
potential = '1985--Foiles-S-M--Ni-Cu'
content_dir = '../webcontent/perpotential'
html_file = 'Interatomic Potentials Repository Project.html'
template_file = 'Interatomic Potentials Repository Project.template'

# Copy potential content
for fname in glob.iglob(os.path.join(content_dir, potential, '*')):
    shutil.copy(fname, os.getcwd())

    
# Load content
content = {}

try:
    with open('EvsR.html') as f:
        content['EvsR'] = f.read()
except:
    content['EvsR'] = ''
    
try:
    with open('Structure.html') as f:
        content['Structure'] = f.read()
except:
    content['Structure'] = ''
    
try:
    with open('Point.html') as f:
        content['Point'] = f.read()
except:
    content['Point'] = ''
    
try:
    with open('Surface.html') as f:
        content['Surface'] = f.read()
except:
    content['Surface'] = ''
    
# Build html from template
with open(template_file) as f:
    template = f.read()
with open(html_file, 'w') as f:
    f.write(iprPy.tools.filltemplate(template, content, '<!--!', '!-->'))