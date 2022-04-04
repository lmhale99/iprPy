from pathlib import Path
import iprPy
import shutil
import pypandoc
import inspect

def main():
    
    buildcalculations()
    copynotebooks()

def buildcalculations():
    """Builds doc/source pages for all calculation styles implemented in iprPy"""
    
    # Find root iprPy directory
    rootdir = Path(inspect.getfile(iprPy)).parent

    # Specify path to Python code for the iprPy.calculations submodule
    pypath = Path(rootdir, 'calculation')
    
    # Specify relative path to doc/source folder for calculations
    docpath = Path(rootdir, '..', 'doc', 'source', 'calculation')
    
    # Remove existing doc source
    if docpath.is_dir():
        cleantree(docpath)
    
    # Loop over all implemented calculation styles
    for name in iprPy.calculationmanager.loaded_style_names:
        print(name, flush=True)
        calc = iprPy.load_calculation(name)
        
        pydir = Path(pypath, name)
        docdir = Path(docpath, name)
        docdir.mkdir(parents=True)
        
        # Verify calculation is a submodule
        if pydir.is_dir():
            
            # Create index.rst
            with open(Path(docdir, 'index.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(calc_index(calc))
            
            # Create doc.rst
            with open(Path(docdir, 'doc.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(calc_doc(calc))

            # Create template.rst
            with open(Path(docdir, 'template.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(calc_template(calc))
            
            # Create function.rst
            with open(Path(docdir, 'function.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(calc_function(calc))
            
            # Create class.rst
            with open(Path(docdir, 'class.rst'), 'w', encoding='UTF-8', newline='\n') as f:
                f.write(calc_class(calc))

def calc_index(calc):
    """Generates the index.rst content for a calculation style"""

    content = '\n'.join([
        calc.calc_style,
        '=' * len(calc.calc_style),
        '',
        '.. toctree::',
        '    :maxdepth: 1',
        '',
        '    doc',
        '    template',
        '    function',
        '    class',
    ])
    return content

def calc_function(calc):
    """Generates the function.rst content for a calculation style"""

    content = '\n'.join([
        Path(inspect.getfile(calc.calc)).name,
        '=' * len(Path(inspect.getfile(calc.calc)).name), 
        '',
        'Calculation functions',
        '---------------------',
        f'.. automodule:: {calc.calc.__module__}',
        '    :members:',
        '    :undoc-members:',
        '    :show-inheritance:',
    ])

    return content

def calc_class(calc):
    """Generates the class.rst content for a calculation style"""

    content = '\n'.join([
        calc.__module__.split('.')[-1],
        '=' * len(calc.__module__.split('.')[-1]), 
        '',
        'Calculation class',
        '-----------------',
        f'.. automodule:: {calc.__module__}',
        '    :members:',
        '    :undoc-members:',
        '    :show-inheritance:',
    ])

    return content

def calc_doc(calc):
    content = (pypandoc.convert_text(calc.maindoc, 'rst', format='md', encoding='UTF-8') + '\n' +
               pypandoc.convert_text(calc.theorydoc, 'rst', format='md', encoding='UTF-8'))

    return content

def calc_template(calc):
    return pypandoc.convert_text(calc.templatedoc, 'rst', format='md', encoding='UTF-8')


def copynotebooks():
    
    # Find root iprPy directory
    rootdir = Path(inspect.getfile(iprPy)).parent

    # Specify path to Jupyter Notebooks
    pypath = Path(rootdir, '..', 'notebook')
    
    # Specify relative path to doc/source folder for database
    docpath = Path(rootdir, '..', 'doc', 'source', 'notebook')
    
    # Remove existing doc source
    if docpath.is_dir():
        cleantree(docpath)
    
    for oldpath in pypath.glob('*/* - Methodology and code.ipynb'):
        oldname = oldpath.name
        newname = oldname.replace(' - Methodology and code', '').replace(' ', '_')
        #newname = oldname.replace(' ', '_')
        print(newname)
        newpath = Path(docpath, newname)
        shutil.copy(oldpath, newpath)

def cleantree(path):
    """Removes content in the existing directory."""
    
    # Try rmtree up to 10 times
    for i in range(10):
        if path.is_dir():
            try:
                shutil.rmtree(path)
            except:
                pass
            else:
                break
    path.mkdir(parents=True)

if __name__ == '__main__':
    main()