
Calculations
************

This section describes the components of a Calculation style in more
detail as well as tips for those wanting to add a new Calculation
style to the framework.


Calculation directories
=======================

All calculations are stored in subdirectories of the iprPy/calculation
directory, with directory named for the calculation, i.e. [calcname].
Each directory contains:

* **calc_[calcname].py**: The Python calculation script.

* **calc_[calcname].template**: A template version of the input
  parameter file that the calculation script reads.

* **[CalcName].py**: Includes the definition of a Python class that is
  a subclass of iprPy.calculation.Calculation.  This defines how the
  iprPy codebase interacts with the calculation.

* **README.md and THEORY.md**: Descriptions of the calculation and
  underlying theory.

* **calc_[calcname]_template.ipynb**: A template version of the
  demonstration Jupyter Notebook with fields for auto-filling content.

* **__init__.py**: The Python init file allowing Python to interpret
  the calculation directory as a submodule of the iprPy package.

* Copies of any other files required by the calculation.


Calculation script
==================

The calculation script is the primary component of the calculation
file as it contains the code for performing the calculation.  To work
within the iprPy framework, the calculation script needs to have the
following requirements.

* It needs to be called “calc_[calcname].py”, where [calcname] matches
  the name of the calculation directory that it is within.

* All variable parameters are read in by passing it an input file as a
  command line argument.

* Upon successful completion, it creates a “results.json” results
  record.


Script design
-------------

The currently implemented scripts all follow the same basic internal
design ensuring that they properly work with the iprPy framework.

* The “results.json” file that is produced by the calculation script
  follows the schema of one of the implemented record styles.  This
  “record_style” is defined at the beginning of the calculation
  script.

* Next, the calculation script defines a main() function that

  ..
     * Opens and parses an input parameter file with the
       iprPy.input.parse() function.  This returns a dictionary of the
       key-value terms, with the values as strings.

     * Calls a process_input() function that interprets the string
       values of the input dictionary as Python values and objects.
       The interpreted values are added to the input dictionary.

     * One or more calculation functions are called that use the
       processed terms in the input dictionary as input parameters.

     * The input terms and any results produced by the calculation
       functions are passed to the associated Record style’s
       buildcontent() method.

     * The generated record content is saved to “results.json”.

* The calculation functions are listed next, which take Python objects
  as arguments.  All results are returned within a dictionary such
  that the produced values can be accessed by name.

* The process_input() function is defined next, which processes the
  string input values contained within an input dictionary, and
  assigns default values for any parameters that were not included in
  the input.  The processed values either update the values already in
  the input dictionary, or are added to the dictionary as new keys.
  The iprPy.input submodule contains a number of useful functions for
  interpreting the input files in a common manner.

  ..
     * iprPy.input.boolean() will interpret (ignoring case
       sensitivity) ‘true’, ‘t’, ‘false’, and ‘f’ strings as bools,
       and will pass through values that are already bools.

     * iprPy.input.value() can be used to interpret and set default
       values for parameters that may include units information, e.g.
       “5 nm”.

     * iprPy.input.interpret() functions are modularly defined
       functions that can be used to interpret a set of input
       parameter terms.  Putting these functions in the iprPy codebase
       makes it easy for similar calculations to interpret input
       parameters in a common and consistent manner.  See ASER for
       more information and for a list of implemented interpret
       styles.

* Finally, the script is told to call the main function if executed
  directly, i.e.:

  ::
     if __name__ == '__main__':
         main(sys.args[1:])


Calculation input template
==========================

To work with prepare, a template version of an input parameter file
for the calculation has to be included.  The prepare function will
read this file in and replace any terms surrounded by angular
brackets, e.g. <termname>, with a value that the prepare function
received for the “termname” term.

The key-value format used by the current calculation input files
results in the template file having lines such as:

::

   termname  <termname>

This not only provides the same standard input file format, but it
also ensures that the key names supported by the calculation are the
same as the key names supported by the prepare function for that
calculation.


Calculation class
=================

The iprPy codebase needs to be able to interact with the calculation
and obtain some metadata for the prepare function to work with it.
This is done by defining a subclass of the
iprPy.calculation.Calculation class, and saving the definition as
CalcName.py within the calculation directory.


Common Calculation properties
-----------------------------

* **style** is the Calculation’s style.

* **directory** is the absolute path to calculation directory.

* **record_style** is the style for the Record associated with the
  results file generated by the calculation script.

* **template** is the absolute path to the input parameter template
  file.

* **files** is a list of absolute paths to every single file that
  should be included in each prepared instance of the calculation.

* **singularkeys** is a list of all input parameter keys that are
  restricted to having only one value for the prepare function.

* **multikeys** is a list of all multi-valued key sets for the prepare
  function.

* **allkeys** is a flat list of all keys in singularkeys and
  multikeys.


Common Calculation methods
--------------------------

* **main()** accesses the Python script’s main() function, allowing
  for the calculation to be executed without generating a separate
  instance.

* **process_input()** calls the Python script’s process_input()
  function.  Making this available is important as it allows the
  prepare function to generate incomplete records for the calculation
  instances it creates using the default values that get assigned by
  the calculation.


Defining a new Calculation class
--------------------------------

Many of a Calculation style class’ properties and methods are
inherited from the parent class or inferred based on directory
information.  The only components that need to be overrided by the
subclass are files, singularkeys, and multikeys as their associated
values are unique to each calculation.

The last step is to make it so that the Calculation subclass can be
imported by Python, which is done simply by importing the CalcName
class within the __init__.py file in the calculation directory:

::

   from .CalcName import CalcName
   __all__ = ['CalcName']
