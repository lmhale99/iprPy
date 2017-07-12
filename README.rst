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

1. Install Python 2.7
   
   a. Using an Anaconda Python distribution is preferred as the scipy family 
      of tools is heavily used.
   
   b. The package 'xmltodict'_ needs to be manually installed beforehand. This 
      can easily be done with the terminal command::

    pip install xmltodict

   c. All other requirements should come with Anaconda or will automatically 
      install during step 4 (let me know if not true).

2. All of the files for iprPy can be found at

    - `https://github.com/usnistgov/iprPy`_ for the stable release.
    
    - `https://github.com/lmhale99/iprPy`_ for the development version(s).
    
3. Download or clone the whole project to a local directory. 
    
4. In a terminal, go into the iprPy root directory and add the iprPy package 
   to Python with the command::
    
    python setup.py develop

Getting Started
===============

Updated documentation is currently in the process. For now, you can check out 
the iprPy Guide in the docs directory for a general overview. Otherwise, send 
me an email if you have questions (lucas.hale at nist.gov).

Specific capabilities and functions are outlined in the docs/reference 
directory.

Introduction tutorials are coming soon.

Demonstration Jupyter Notebooks for each implemented calculation are in the 
docs/demonstrations directory.

.. _xmltodict: https://github.com/martinblech/xmltodict
.. _https://github.com/usnistgov/iprPy: https://github.com/usnistgov/iprPy
.. _https://github.com/lmhale99/iprPy: https://github.com/lmhale99/iprPy