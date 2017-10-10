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

:any:`basics/index`

Learn about the different components of the iprPy framework, how to run
calculations, and how to add your own content.

`Jupyter Notebooks <../../demonstrations/README.md>`_

Jupyter Notebooks are provided for all implemented calculations that fully
document the calculation methodologies, contain identical Python code to the
calculations, and demonstrate a single run.

:any:`modules/index`

The Python docstring information for the functions and classes of iprPy.

Contents
========

.. toctree::
    :maxdepth: 4
    :caption: Contents:

    intro
    setup
    basics/index
    highthroughput/index
    extend/index
    calculation_styles
    record_styles
    database_styles
    modules/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`