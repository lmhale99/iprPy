========================
iprPy Package Components
========================

This page provides a general overview of the different components of the iprPy
framework and how they work together.

Calculations
------------

Calculations are the heart of the iprPy framework.  Each unique calculation
methodology is referred to as a *calculation style*, and exists as a
Python script that performs an independent unit of work in isolation from any
other calculation style.  Calculations can be accessed and executed in a
variety of ways:

- The Python calculation scripts can be directly executed by passing in an
  input parameter file.  Upon completion, the generated results will be
  collected in results.json.

- A demonstration Jupyter Notebook exists for the implemented calculation
  styles which contains copies of the calculation functions from the Python
  script, documentation on the calculation style's theory, methodology and
  parameters, and a working example.

- The iprPy package contains a Calculation subclass for each calculation
  style.  These Calculation classes define metadata associated with each
  style and provide a means of accessing the different underlying functions.

New calculation styles can be added to the iprPy framework in a modular fashion
by defining a Calculation subclass and placing the subclass script and the
calculation script in a subdirectory of iprPy/calculation.

Records
-------

Performing calculations in high-throughput requires collecting and managing
data sets associated with a variety of different concepts.  Meaningful inputs
for calculations are often best collected together as parameter sets.  Also,
each calculation style produces a different set of results.  In iprPy, each
unique data set (reference and results) is associated with a different
*record style*.

Each record style has a Record subclass defined for it.  These Record classes
provide details of the contained data, and conversion tools between different
representations.  The primary representation is as a tree-like data model that
is equivalently expressed as JSON, XML, and a Python dictionary.  Class methods
convert raw calculation data into the data model format, and allow for the data
model content to be transformed to a flat dictionary representation.

New record styles can be added to the iprPy framework in a modular fashion
by defining a Record subclass and placing the subclass script in a subdirectory
of iprPy/record.

Databases
---------

The various records need to be collected and stored within databases allowing
for the high-throughput tools to find and access the information.  In iprPy,
multiple databases of the same or different styles can be used allowing for
the results of different investigations to be kept together or separate.  A
*database style* refers to a specific type of database, such as a MongoDB or a
local collection of files.  Each database style is associated with a Database
subclass that defines how to perform common interactions with that type of
database.

The parent Database class also defines methods for the high-throughput actions
as these actions all require accessing and/or changing the records in a
database.  These high-throughput methods can be accessed from within Python,
or by using the iprPy command line available in the bin/ directory.

New database styles can be added to the iprPy framework in a modular fashion
by defining a Database subclass and placing the subclass script in a
subdirectory of iprPy/database.

Reference library
-----------------

The iprPy/library directory is meant to provide a central location of reference
records that can be copied to any database.  The reference library
automatically contains some reference records, and more can be easily imported
and/or built from other sources.

Subsets
-------

Related calculation methods often require similar inputs.  To help with the
development of new calculation styles and provide consistency in input
parameters across calculations, sets of inputs are collected together as
*subset styles*.  A Subset subclass is defined for each subset style that
defines methods for interpreting the associated input terms, and for how the
input terms get handled by the records.

New subset styles can be added to the iprPy framework in a modular fashion
by defining a Subset subclass and placing the subclass script in a
subdirectory of iprPy/input/Subset_classes.

buildcombos
-----------

High-throughput calculation runs require iterating over combinations of
calculation input values.  The default behavior of iprPy is that the different
values of a given input to iterate over are supplied as a list when the
high-throughput calculations are prepared.  However, this can be impractical
when multiple inputs all need to be set simultaneously and/or a large number of
input values need to be iterated over.

To address this problem, buildcombos functions can be defined that can then be
used within prepare input files.  Each *buildcombos style* is a function that
allows for the generation of multiple prepare input lines based on the
available records within a database.  By generating inputs based on existing
database records, the buildcombos functions make it possible to develop
calculation workflows with the results of one calculation being used as input
for others.

New buildcombos styles can be added to the iprPy framework in a modular fashion
by defining a buildcombos function and placing the function script in a
subdirectory of iprPy/input/buildcombos_functions.

Workflow scripts
----------------

The IPR workflow directory contains Jupyter Notebooks and scripts that perform
calculations using the same workflow as is done for the Interatomic Potentials
Repository.  These scripts perform the calculations in a set order using
default input parameter values.

Other supporting code
---------------------

The iprPy package also contains other support functions for developing,
running, and analyzing calculations.  The submodules of the iprPy package are

- analysis: tools for analyzing and processing calculation records.

- calculation: defines the Calculation class and subclasses.

- database: defines the Database class and subclasses.

- input: support functions for handling input files and values.  Includes the
  definition for the Subset class and subclasses, as well as the buildcombos
  functions.

- record: defines the Record class and subclasses.

- tools: utility functions that don't have homes elsewhere.

- workflow: functions that support the IPR workflow scripts by preparing
  calculations with default inputs, and processing the results in the same way.


