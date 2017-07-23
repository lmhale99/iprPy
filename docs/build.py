import os
import glob
import iprPy

for fname in glob.iglob(os.path.join('source', 'rst', '*.rst')):
    with open(fname) as f:
        content = f.read()
    if ':maxdepth:' not in content:
        content = content.replace('.. toctree::', '.. toctree::\n    :maxdepth: 1')
    with open(fname, 'w') as f:
        f.write(content)
    
readme_file = os.path.join('..', 'README.rst')
template_file = os.path.join('source', 'index.template')
rst_file = os.path.join('source', 'index.rst')

fill_terms = {}
with open(readme_file) as f:
    fill_terms['README'] = f.read()

with open(template_file) as f:
    template = f.read()
    
with open(rst_file, 'w') as f:
    f.write(iprPy.tools.filltemplate(template, fill_terms, '<', '>'))