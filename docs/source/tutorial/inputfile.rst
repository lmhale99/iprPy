====================
Input Parameter File
====================

The executable scripts contained within the iprPy framework all read in
input parameters from similarly formatted input parameter fies.  These files
are simple text files that provide values to parameter names in a simple
key-value manner. Each script has its own set of recognized variable names,
which are described in the associated documentation for the calculation or
script method.

Formating rules
---------------

The iprPy.tools.parseinput function is used for reading in the input
parameter files.  The parseinput function follows these simple rules for
interpreting the files

#. Each line is read separately, and divided into whitespace-delimited terms.

#. Comments are allowed by starting terms with #. The # term and any
   subsequent terms on the same line are ignored.

#. The first term in each line is a variable name.

#. All lines with less than two terms are skipped.  This means that blank
   lines are allowed, and variable names without values are ignored.

#. All content after the variable's name is taken as the variable's value
   (with leading and trailing whitespace stripped away).

#. For prepare scripts and methods, some variables can be given multiple
   values by listing the variable name followed by a value on more than one
   line.  See a given calculation's documentation to learn which prepare
   variables can be multi-valued.

Formatting example
------------------

Script::
    
    # This is a comment and will be ignored
    
    firstvariable    singleterm
    
    secondvariable   multiple terms   using    spaces
    thirdvariable    term #with comments
    thirdvariable    again!
    
    fourthvariable
    
Gets interpreted as a Python dictionary::
    
    {'firstvariable': 'singleterm',
    'secondvariable': 'multiple terms   using    spaces',
    'thirdvariable': ['term', 'again!']}
     
Easy creation
-------------

Generating a calculation script input file from scratch can be challenging
as the calculation scripts take numerous parameters.  But, there is an easy
way to build an input parameter file: use the "calc_[calcname].template"
file!  The templates are used by the prepare functions and list all input
parameters allowed by a calculation.  All you have to do is

#. Copy "calc_[calcname].template" to "calc_[calcname].in", or some other
   name.
   
#. Open the input file in a text editor and delete all the <terms>.

#. Fill in values for the necessary parameters.

As for prepare script input files, there are no templates to build from, but
there are examples in the bin directory.