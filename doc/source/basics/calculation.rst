============
Calculations
============

The iprPy framework is designed around calculations.  In design, all
implemented calculations behave the same way:

#. Every calculation is an independent and self-contained unit of work.  In
   other words, it can run in isolation from all other calculations.

#. Each calculation exists as or is executed by calling a Python script.

#. The calculation reads in all variable inputs from an input parameter file.

#. Upon successful completion, the calculation generates an XML- or
   JSON-formatted results record.
   
Location of Calculations
========================

The calculations are located in the iprPy/calculations directory. This
location lets the iprPy package identify the calculations and load them as a
calculation style. Doing so makes it possible for objects of the
:any:`Calculation class <../highthroughput/classes>` to access components and 
interact with the different calculation styles in a common way.

Within the iprPy/calculations directory, each calculation is placed in a
subdirectory matching the calculation's name.  Collecting all files for a
given calculation together into a single folder allows for the calculations
to be treated modularly.

Run a Calculation
=================

A calculation can be performed in one of three ways

#. `Run the Jupyter Notebook`_

#. `Run the calculation script`_

#. `Prepare and run in high-throughput`_

Run the Jupyter Notebook
------------------------

The demonstration directory has a Jupyter Notebook for every calculation.
Each Notebook combines the calculation’s documentation and calculation script
functions and methods into a single stand-alone file.  This is perhaps the
most convenient way to learn about the methods, theory and parameters of a
given calculation and to test it out yourself.

Run the calculation script
--------------------------

Alternatively, you can run the calculation's script.  Text documentation for
the calculation can be found in the ".md" files in the calculation folder.
Equivalent HTML documentation is also provided in the
:any:`calculation_styles`.

#. Copy the calculation folder to another location (this keeps the original
   folder from becoming cluttered).

#. Create an :any:`inputfile`.

#. In a terminal, cd to the calculation folder you created, and enter::
        
        python calc_[calcname].py [inputfile]
     
#. When the calculation finishes successfully, a "record.json" record file
   will be created containing the processed results.

Prepare and run in high-throughput
----------------------------------

Multiple instances of the same calculation can also be prepared and executed
in a high-throughput manner using the :any:`../highthroughput/prepare` and 
:any:`../highthroughput/runner` methods and scripts. Before doing so, it is 
suggested that you try running a single instance of the calculation using 
either the Jupyter Notebook or the calculation script as the calculation’s 
prepare uses most of the same input parameters as the calculation itself. 
When ready, check out the :any:`../highthroughput/index` tutorial.