========================
iprPy Package Components
========================

This page provides a general overview of the different components of the iprPy
framework and how they work together.

Calculations
============

Calculations are the heart of the iprPy framework.  Each unique calculation
methodology is referred to as a *calculation style*.  The calculation itself
exists as a Python function that performs an independent unit of work in
isolation from any other calculation.  Each calculation is implemented into
iprPy by defining an associated Calculation class that specifies metadata
associated with the calculation, and manages and interprets input parameters
and generated results.

Calculations can be accessed and executed in a variety of ways:

- The iprPy package contains a Calculation class for each calculation
  style.  These Calculation classes define metadata associated with each
  style and provide a means of accessing the underlying calculation functions.

- A demonstration Jupyter Notebook exists for the implemented calculation
  styles which contains copies of the calculation functions from the Python
  script, documentation on the calculation style's theory, methodology and
  parameters, and a working example.

- Each calculation style also accepts inputs in the form of key-value text
  files, which can then be passed to iprPy from the command line to be
  executed.  Upon successful completion, the calculation will generate a 
  results.json file.

Records
=======

Performing calculations in high throughput requires collecting and managing
data, which serves both as defining meaningful input parameter sets and
collecting calculation results.  The iprPy framework is designed around NoSQL
databases that store records in XML/JSON formats.  iprPy supports a variety of
*record styles*, with each style being associated with a type of data.  Each
record style exists primarily as a Record class, which defines methods for
loading and/or building record models consistent with a specific schema (i.e.
a defined template that specifies the expected fields in a record).  Note that
Calculation classes are Record classes thereby providing a single point of
entry for managing and interpreting calculation results data. 

Databases
=========

The large amount of data generated by high throughput runs is best managed by
storing it inside a database.  iprPy supports different database
infrastructures, with each infrastructure being managed by a *database style*
and an associated Database class.  In this way, different types of databases
can be interfaced with using the same or similar iprPy commands.

Calculation subsets
===================

Calculations that do similar types of work often take similar inputs.  For
instance, atomistic calculations tend to require an interatomic potential and
an initial atomic configuration.  Calculation subsets are classes that collect
related calculation input parameters together and manage how those parameters
are interpreted and transformed into other representations.  Defining
calculation subsets helps in creating new Calculation classes as the full set
of inputs supported by the calculation can be composed of subsets plus any
calculation-specific terms.  This shortens development time associated with
creating new Calculation classes, reduces code redundancy, and helps ensure
consistency across the different Calculations associated with how the input
terms are represented and interpreted.

Workflow scripts
================

The iprPy framework provides simple tools for setting up and running workflows
of calculations in high throughput.  The tools consist of two primary
components "prepare" and "runner", along with supporting tools for managing
calculation data stored in databases.  Prepare builds instances of a
calculation style that are to be executed by generating unique combinations of
that calculation's input script and copying files as needed.  Runners then
iterate through the prepared calculations and automatically collect the
generated results into a database.

buildcombos functions
=====================

Building calculation workflows consisting of multiple different calculation
styles requires a means of using the results of one calculation run as the
inputs of another.  This is achieved in iprPy by defining "buildcombos"
functions that can be called by the prepare scripts.  Each buildcombos style
is designed to query existing records in the database and tell the prepare
script to iterate over all returned record matches.  This allows for high
throughput workflows to be constructed in which calculations are built from
both previous results and iterations over other input parameter values.