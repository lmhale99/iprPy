from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()
    

setup(name='iprPy',
      version='0.6',
      description='Interatomic Potential Repository Python Property Calculations and Tools',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Physics'
      ],
      keywords=['atom', 'atomic', 'atomistic', 'molecular dynamics', 'high-throughput', 'interatomic'], 
      url='https://github.com/usnistgov/iprPy',
      author='Lucas Hale',
      author_email='lucas.hale@nist.gov',
      packages=find_packages(),
      install_requires=[
        'xmltodict',
        'DataModelDict',
        'numpy', 
        'matplotlib',
        'scipy',
        'pandas',
        'numericalunits',
        'atomman'
      ],
      include_package_data=True,
      zip_safe=False)