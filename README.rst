=====
iprPy
=====

The iprPy project is a collection of tools and resources for developing and 
performing classical atomistic simulations. It was originally created to 
support basic property calculations for the NIST Interatomic Potential 
Repository allowing for the different hosted potentials to be evaluated and 
compared. The robustness of iprPy is such that it can also be used for handling 
more complex materials analyses for research purposes.

The design principles for iprPy are:

- Full documentation is provided for all calculations explaining not only how 
  to perform the calculations, but also detailing the strengths and weaknesses 
  of the underlying routines. 
  
- Each calculation is a complete, independent unit of work with clear input 
  parameters and structured results. This makes it possible to easily share the 
  calculations and provide results that are both human- and machine-readable. 
  
- Calculations should be easily adapted to work with high-throughput resources 
  for performing over a wide range of potentials and conditions.

Setup
=====

1. Install Python 2.7. Common scientific libraries like numpy are heavily used, 
   so it is often easiest to use a distributed package such as Anaconda. 
   
2. Install `atomman`_. All of the calculations currently implemented use the 
   atomman package for providing a wrapper around LAMMPS simulations.
   
3. Download iprPy.
    - `https://github.com/usnistgov/iprPy`_ hosts the current stable release 
      version.
    - `https://github.com/lmhale99/iprPy`_ hosts developmental version(s).
    
4. In a terminal, go into the iprPy root directory add the iprPy package to 
   Python with the command::
    
    python setup.py develop

Getting Started
===============

The best place to start is to look at the Jupyter Notebooks in the docs 
directory. The docs/methods directory contains Notebooks describing the 
underlying routines used by each calculation and provides an example 
demonstration. The docs/reference directory contains Notebooks that describe 
how to run the calculation scripts and use the high-throughput tools to prepare 
multiple instances of the calculations. 

.. _atomman: https://github.com/usnistgov/atomman
.. _https://github.com/usnistgov/iprPy: https://github.com/usnistgov/iprPy
.. _https://github.com/lmhale99/iprPy: https://github.com/lmhale99/iprPy