import os
from setuptools import setup, find_packages

def getversion():
    """Fetches version information from VERSION file"""
    with open(os.path.join('iprPy', 'VERSION'), encoding='UTF-8') as version_file:
        version = version_file.read().strip()
    return version

def getreadme():
    with open('README.rst', encoding='UTF-8') as readme_file:
        return readme_file.read()

setup(name = 'iprPy',
      version = getversion(),
      description = 'Interatomic Potential Repository Python Property Calculations and Tools',
      long_description = getreadme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Physics'
      ],
      keywords = [
        'atom', 
        'atomic', 
        'atomistic', 
        'molecular dynamics', 
        'high-throughput', 
        'interatomic potential',
      ], 
      url = 'https://github.com/usnistgov/iprPy',
      author = 'Lucas Hale',
      author_email = 'lucas.hale@nist.gov',
      packages = find_packages(),
      install_requires = [
        'DataModelDict',
        'numpy', 
        'matplotlib',
        'scipy',
        'pandas',
        'atomman>=1.4.11',
        'requests',
        'bokeh',
        'plotly',
        'kaleido'
      ],
      entry_points = {
        'console_scripts': [
          'iprPy = iprPy.command_line:command_line'
        ]
      },
      include_package_data = True,
      zip_safe = False)
