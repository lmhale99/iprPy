=============
iprPy Classes
=============

The iprPy framework handles high-throughput calculations through the
interaction three different classes.  Each class specifies common interaction
methods that are then defined for different styles that can be modularly
added.

The current methods and attributes for the classes can be found in the
:any:`iprPy` documentation.

Calculation
===========

The iprPy.Calculation class allows for information from the implemented
calculations to be accessed by the iprPy package codebase.  The
:any:`calculation_styles` correspond to the names of the implemented
calculations.

The methods and attributes of the Calculation class are primarily centered
around the high-throughput :doc:`prepare <prepare>` step.  In particular, each
calculation defines its own prepare method, and that prepare method requires
information and metadata associated with the calculation script.

Record
======

Objects of the iprPy.Record class represent a single XML/JSON record used or
produced by the framework.  Each record features three primary attributes:
*style*, *content*, and *name*.  Each unique schema is implemented as a
different Record style. The Record’s content is the XML string representation
of the underlying record. Finally, the Record’s name is used in saving the
content to a database and should correspond to the primary “key” or “id” field
in the content.

By making a Record style for each schema, it is possible to define specific
actions in creating and comparing Records, and in converting the multi-tiered
structure to a simpler, flatter structure.

**Note**: Each Calculation style is associated with a single Record style to
represent it, but each Record style does not have to be exclusive to a
particular Calculation style.  As an example, both the LAMMPS_ELASTIC and
refine_structure Calculation styles produce their results as Records of the
calculation_relax_structure style.

Database
========

The iprPy.Database class provides commonly-named database interaction methods
for different styles of databases.  This includes adding, retrieving,
deleting, and modifying records and tar archives to/from a given database. In
the case of record interactions, the Database methods take or return Record
objects.
