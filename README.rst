=====
iprPy
=====

This is the homepage for the Python tools used in calculating material 
properties as predicted by classical atomistic models for the NIST 
Interatomic Potential Repository.

The project is divided into three major components:

1. :ref:`demo`

2. :ref:`library`

3. :ref:`tools`

.. _demo:

Demonstration Calculations 
~~~~~~~~~~~~~~~~~~~~~~~~~~

The calculation folder holds the Python scripts for the calculations. The plan 
is that each .py script is independently runnable. Run parameters are specified
in the related .in input script.  The calculation can be ran directly from the 
terminal with “python calc_NAME.py calc_NAME.in”.  And the compiled results and 
metadata for a successful run is collected in the results.json file.

The Notebooks folder holds Jupyter demonstration Notebooks associated with the 
calculations.  Ideally, the code in the Notebooks should be as close to the 
code in the calc.py scripts as possible.  

.. _library:

Reference Library
~~~~~~~~~~~~~~~~~

The ref folder holds the potential artifacts and json files for all the IPR 
potentials, as well as json files for the crystal prototypes.

.. _tools:

High-Throughput Calculation Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Everything else is for doing the high-throughput calculations. prepare.py takes 
the prepare.in input script and generates calculations to run, runner.py goes 
over the folder where the calculations are placed and runs them, and process.py 
does any necessary postprocessing of the data. Right now these tools are still 
rough and some require hard-coded directories to be changed in them.  You can 
try to play with them, but it might be best to talk about them in a video conference.  



