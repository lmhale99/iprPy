=============================================
iprPy High Throughput Computational Framework
=============================================

Description
===========

The iprPy package is a computational framework supporting open source
calculation methods.  The framework focuses on making the barriers for usage
as low as possible for both users and developers of calculations.  In
particular, the methods are 

- fully documented, 
- designed to be transparent to end users,
- produce results in formats that are both human and machine readable,
- modular in design supporting the incorporation of new methods, 
- and can be easily integrated into workflows.

The framework consists of the following major components

1. Calculation methods, which exist as Python scripts and fully detail how to
   perform a single independent calculation.
2. Calculation classes that manage metadata associated with the calculations.
   These classes integrate the calculation method scripts into the framework
   and allow for the calculations to be accessed and executed in a variety of
   ways.
3. Calculation subsets that provide common handling of input/output parameter
   sets that are shared by multiple calculations.
4. Built-in workflow tools that make it possible to run the implemented
   calculations in high throughput and store/access the results in databases.

iprPy was originally created for the NIST Interatomic Potentials
Repository (i.e. I.P.R. Python) for collecting and performing calculation
methods that evaluate how different classical interatomic potentials predict A
variety of basic materials properties.  As such, the majority of included
methods are centered around performing classical atomistic calculations.  It
should be noted, however, that the framework design can support any type of
underlying calculation as long as the calculation method can be represented
as a python function that can be executed independently from any other
calculation method.

Documentation Sections
======================

:any:`intro`

A quick introduction describing why you would want to use the iprPy framework.

:any:`setup`

Gives details on how to install and set up iprPy.

:any:`overview`

Describes the basic components of iprPy.

:any:`run/index`

Learn about the different components of the iprPy framework and how to run
calculations.

:any:`calculation_styles`

Describes the implemented calculations and what input parameters the
calculation scripts use.

:any:`notebook_styles`

Provides demonstration Jupyter Notebooks for the implemented calculations.

:any:`extend/index`

This describes the components of iprPy in more detail for those who want to
contribute to the package by adding content.

:any:`iprPy/index`

The Python docstring information for the functions and classes of iprPy.

Package Tutorials
=================

.. toctree::
    :maxdepth: 4
    :caption: Contents:

    intro
    setup
    overview
    run/index
    extend/index

Implemented Content
===================

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    calculation_styles
    notebook_styles

Code Documentation
==================

.. toctree::
    :maxdepth: 3

    iprPy/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
