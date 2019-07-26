=============================================
iprPy High-Throughput Computational Framework
=============================================

Description
===========

The iprPy framework is a collection of tools and resources supporting the
design of scientific calculations that

- are open source with minimum barriers for usage,
- have transparent methodologies supporting knowledge transfer and education,
- produce results that are both human and machine readable,
- allow investigations into method and parameter sensitivity,
- and can be integrated into workflows.

The framework was originally created to support the NIST Interatomic Potential
Repository by evaluating basic materials properties across multiple classical
interatomic potentials.  Because of this, many of the included calculations
and tools are designed towards molecular dynamics simulations.

Documentation Sections
======================

:any:`intro`

A quick introduction describing why you would want to use the iprPy framework.

:any:`setup`

Describes the basics of iprPy for performing calculations.

:any:`run/index`

Learn about the different components of the iprPy framework and how to run
calculations.

:any:`calculation_styles`

Describes the implemented calculations and what input parameters the
calculation scripts use.

:any:`notebook_styles`

Provides demonstration Jupyter Notebooks for the implemented calculations.

:any:`record_styles`

Describes the implemented record formats for storing calculation data.

:any:`database_styles`

Describes the implemented database types that can be interacted with.

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
    record_styles
    database_styles

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
