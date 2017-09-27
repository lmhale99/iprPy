
Creating Calculation Styles
***************************

**Note**:  The easiest way to start creating a new calculation is to
copy an existing one and then modify its contents. Then, this
documentation can serve as a guide for describing the various
components.


Calculation scripts
===================

Each calculation style is centered around the corresponding
calculation script.


Requirements
------------

There are only a few basic requirements for the calculation scripts.

* The script’s file name is ‘calc_<calc_name>.py’, where <calc_name>
  is the name of the calculation style.

* The script is directly executable and reads in all variable inputs
  from an input file given as a command line argument.

* Upon successful completion, it generates a ‘results.json’ file
  consistent with a Record style.


Design guidelines
-----------------

While nothing else is required, there are a few additional guidelines
towards the design of the calculation scripts. These guidelines help
make the contents of the calculation scripts clear, and their
behaviors consistent with the other calculations.  Additionally, it
allows for new scripts to take advantage of some of the pre-existing
tools.


Style definitions
~~~~~~~~~~~~~~~~~

Variables *calc_style* and *record_style* define the Calculation style
and Record style associated with the calculation script.   These
definitions should be placed after the imports but before any defined
functions.


*main()* function
~~~~~~~~~~~~~~~~~

The first defined function is *main(*args)*.  This is the primary
function for the calculation.  It should be called when the script is
executed by placing at the very bottom of the script:

::

   if __name__ == '__main__':
       main(*sys.argv[1:])

The *main()* function should

* Read the input file and convert to a dictionary with parseinput:

  ::
     with open(args[0]) as f:
         input_dict = iprPy.tools.parseinput(f, allsingular=True)

* Interpret and process input parameters with the *process_input()*
  function:

  ::
     process_input(input_dict, *args[1:])

* Call any calculation functions using the processed input parameters.

* Generate the “results.json” file with:

  ::
     results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict,
                                results_dict)
     with open('results.json', 'w') as f:
         results.json(fp=f, indent=4)

This design allows for the separation of the input-output control from
the code that does the actual calculation work.


Calculation functions
~~~~~~~~~~~~~~~~~~~~~

The calculation functions are where the calculation is performed.
These are separated from the *main()* function so that they can also
be used without modification outside of the calculation scripts.  To
achieve this

* The calculation functions’ arguments should explicitly list
  parameters, i.e. take specific terms from the generated input_dict
  rather than the input_dict itself.

* If a calculation function returns multiple terms to the *main()*
  function, they should be returned within a dictionary as opposed to
  within a list/tuple so that the terms can be properly named.

* The actions of a calculation function, all input parameters and
  returned terms should be documented and described in the function’s
  docstring.  The currently implemented calculation’s use numpy’s
  docstring format.


*process_input()* function
~~~~~~~~~~~~~~~~~~~~~~~~~~

The handling of the input parameter files is a two-step process

* *iprPy.tools.parseinput()* parses the input file converting it into
  a dictionary with string values

* The calculation’s *process_input()* function interprets input_dict’s
  terms into meaningful arguments for the calculation function.

The *process_input()* function modifies the *input_dict* generated
from *iprPy.tools.parseinput()* by converting the string values to
other data types, assigning default values to any missing terms, and
adding new terms with complex values.  For simple terms, this can
easily be handled with the dict.get() method, e.g.:

::

   input_dict[<key>] = int(input_dict.get(<key>, <default>))

The iprPy.input submodule contains functions for more complex and
challenging conversions.  Two of the basic functions of this module
are

* iprPy.input.boolean(value) which converts a str value of ‘t’,
  ‘true’, ‘f’, or ‘false’ to the corresponding bool.

* iprPy.input.value(input_dict, key, default_unit=None,
  default_term=None) which allows for the handling of input parameters
  for floats that may have specific units specified.

Additional functions in the iprPy.input module are focused around
common handling of atomistic inputs for LAMMPS simulations using the
atomman package. More information can be found on the `LAMMPS
Calculations Using atomman <calc_atomman.rst>`_ page.


Results generation
~~~~~~~~~~~~~~~~~~

When first creating a calculation, it is probably helpful to print the
generated calculation results in a simple format for testing and
verification of the methodology.  Once the calculation method is
stable and the result terms produced by the calculation functions are
defined, then check out the `add_record
<../modules/iprPy.rst#iprPy.Database.add_record>`_ page for how to
create a Record style for the calculation. The generation of the
“results.json” file is handled by the Record style rather than the
Calculation style as the results file is a complete record.


Implementing a Calculation Style into iprPy
===========================================

A working calculation script can be implemented into the framework as
a calculation style by

* Creating a folder in the iprPy/calculation directory named for the
  calculation style.

* Placing the calculation script inside the calculation folder as well
  as any other files that the calculation script needs to run
  (excluding inputs).

* Creating a __init__.py file in the calculation folder that defines
  the various functions and values that are to be accessed as methods
  and attributes of the Calculation class.

Simply creating a calculation folder and an __init__.py file with
valid Python code is enough for iprPy to recognize and load it as a
Calculation style. Interactivity through the Calculation class then
comes from defining the components of the class in the __init__.py
file.  The components recognized by the Calculation class are

* process_input() : The process_input function used to process the
  calculation script’s input parameters.

* files() : A function that yields the absolute path to all
  non-variable files required by the calculation.  This includes the
  calculation script and any data files accessed by the calculation
  script regardless of the input parameters.

* template() : A function that returns a template version of the
  calculation’s input parameter file as a str.

* prepare_keys : A dictionary listing all single- and multi-valued
  input keys recognized by the calculation’s prepare function.

* prepare() : The calculation’s prepare function.

More information on template, prepare_keys and prepare is given in the
:*any:calc_prepare* documentation.

A working __init__.py file for the calculation is easiest to create by
copying one from an already implemented calculation. By default, it
will expect

* The calculation script’s name to be “calc_<calc_style>.py”.

* The calculation script to contain the *process_input()* function.

* The template input file to be saved as “calc_<calc_style>.tempate”
  in the calculation folder.

* The calculation’s prepare script to be in the calculation folder and
  named “prepare_<calc_style>.py”.

* The prepare script to contain functions *prepare()*,
  *singularkeys()*, and *multikeys()*.

If these are all true, then the only change that needs to be made to
the __init__.py file is the list of file names yielded by the
*files()* function. If you want to test calling parts with the
Calculation class before implementing all the parts, you can comment
out the calls to the pieces that don’t exist yet.


Calculation Documentation
-------------------------

Finally, documentation for the calculation should be included in the
calculation folder.  The basic documentation consists of Markdown
formatted text files

* README.md : Provides author information for the calculation and a
  short Introduction describing the calculation and providing any
  disclaimers for when issues may arise due to the method or parameter
  choice.

* theory.md : Provides a detailed description of how the calculation
  Method is implemented and any underlying Theory behind the method.

* *More to come...*

The use of these pre-defined Markdown documentation files is
advantageous as they can be identified by automated scripts for
inclusion in the online documentation and directly copied into
demonstration Jupyter Notebooks.
