=====================
High-Throughput Tools
=====================

Designing the calculations to be independent units of work that read standard
input files makes performing the calculations in high-throughput incredibly
simple.  All you have to do is execute the same calculation scripts with
different input files.  And with the calculation results being reported in
XML/JSON, the accumulated data can automatically be uploaded into a database.

With iprPy, performing calculations in high-throughput is a two-step process.

1. You :doc:`prepared <prepare>` a calculation.  This creates multiple
   instances of the calculation within a specified "run_directory".  Each
   instance is a folder containing a copy of the calculation's script, a
   unique input parameter file, and any other files required to perform the
   calculation.  Additionally, an incomplete record associated with each
   calculation instance is added to a database.
2. You start one or more :doc:`runners <runner>`.  Each runner operates on a
   single "run_directory" systematically performing one prepared calculation
   instance after another.  When each calculation finishes, successfully or
   unsuccessfully, the corresponding record in the database is updated and the
   calculation instance’s folder is archived and added to the database.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    quickstart
    classes
    prepare
    runner
    inline
    analysis








