=======
Prepare
=======

Introduction
============

The first step in performing a calculation method in high-throughput is to
prepare instances of it. The process of preparing a calculation is that:

1. All records in a database corresponding to the calculation’s record style
   are accessed and collected into a table.
2. Based on supplied parameter values, all meaningful combinations of
   calculation input parameters are iterated over.
3. Each iteration is compared to the table of existing calculations.
4. If no match is found, then the corresponding calculation instance is
   prepared by
   
    a. Creating a calculation folder in a run_directory
    b. Copying the calculation script and any other required calculation files
       to the run_directory.
    c. Copying all required parent records from the database to the
       run_directory.
    d. Generating an input parameter file for the calculation using the
       iteration parameters
    e. Adding a corresponding incomplete calculation record to the database.

Every single calculation style defines its own prepare function, which is
contained in a prepare_<calcname>.py script within the calculation style’s
directory. This is necessary as the meaningful combinations of input
parameters to iterate over are specific to a given calculation.

**Note**: The table of existing records is only compiled once at the beginning
of the prepare method and the information associated with instances being
prepared are *not* appended.  Not updating the table makes preparing
noticeably faster, but also makes it possible that matching instances can end
up being prepared. To avoid this, there should never be more than one active
prepare operating on a specific calculation style at any time. 

Notes on run_directory naming
=============================

The suggested manner of naming run_directories should be some combination of a
database name and a number of computational cores.  This is because prepared
calculation instances are associated with the database used to prepare them,
and runners can only access a single database and are limited by the number of
cores available.  For example, if your database is named "mydbase", then
prepare serial calculations in a "mydbase1" run_directory and 4 core
calculations in a "mydbase4" run_directory.  How many processors that a
specific calculation instance will try to use should be given by one of the
input parameters for the prepare function and for the calculation.

How to prepare
==============

Calculations can be prepared in one of three ways:

1. Use the inline iprPy prepare command.
2. Run a prepare Python script.
3. In Python, call the prepare method of a Calculation object. 


All three of these ways effectively do the same thing in that they access a
calculation’s prepare function. How they differ is in the handling of the
necessary inputs.

Inline prepare
--------------

Calculations can be prepared using the following inline iprPy terminal
command::

    ./iprPy prepare <database> <run_directory> <inputfile>
    
<database> and <run_directory> are the names associated with a database and
run_directory that were defined using the iprPy set command.  <inputfile> is
the name/path to an input parameter file for the prepare command. When
preparing in this way, the input parameter file must contain a
“calculation_style” term that lists the calculation’s style.

Running a prepare script
------------------------

The calculation’s prepare script can be executed directly from the calculation
style’s folder with::

    ./prepare_<calcname>.py <inputfile>
    
Where <calcname> is the calculation style and <inputfile> is the name/path to
an input parameter file for the prepare command. When preparing in this way,
the input parameter file must contain a “run_directory” term, a “database”
term, and any extra “database_*” access terms defining the run_directory and
database to use.

Calculation.prepare() method
----------------------------

Within Python, a calculation can be prepared by initializing a Calculation
object, then calling the Calculation’s prepare method::

    calc = iprPy.Calculation(<calcstyle>)
    calc.prepare(<dbase>, <run_directory>, **kwargs)
    
Here, <calcstyle> is the Calculation style to use given as a string, <dbase>
is an iprPy.Database object, <run_directory> is the string path to a
run_directory, and kwargs are the calculation-specific parameters.  Most of
the kwargs correspond to the terms allowed in the input files used by the
inline prepare command and the prepare scripts. However, there can be
additional kwargs that provide more functionality and control than is allowed
by the other ways of preparing.

Prepare parameters
==================

While the parameters used in preparing a calculation are specific to that
calculation, they can be classified into a few categories:

- Calculation parameters – These are parameters of the calculation that can be
  directly assigned one or more values using correspondingly named prepare
  parameters.
- Limiting parameters – These are parameters that allow for limitations to be
  used in iterating over the possible combinations. If a limiter is given,
  then only the cases that correspond to the limiter’s values will be
  included. If a limiter is not given, then there is no restriction placed
  relative to the limiting parameter.

