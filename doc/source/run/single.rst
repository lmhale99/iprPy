============================
Running a single calculation
============================

This page outlines the general steps associated with setting up and running a
single calculation.  The general order of these steps holds true regardless of
if you are only working with command line and text files or are running in a
Python environment.  As such, the various alternate ways of accessing the steps
are described together.

**NOTE:** In the descriptions below, the commands will be used relative to the
"isolated_atom" calculation style.  To use any other calculation style, simply
replace "isolated_atom" with another calculation style.
 
1. Check available calculations
===============================

The check_modules command will output information associated with which module
components of iprPy successfully loaded or encountered an issue.  This allows
for users to see which calculations are currently available and what additional
packages may be required in order to use some of the calculations.

1.1. Command line
-----------------

.. code-block:: bash

    $ iprPy check_modules

1.2. Python
-----------

.. code-block:: python

    import iprPy
    iprPy.check_modules()

2. Create new directory
=======================

It is recommended but not required that you create a new empty directory for
running the calculation.  This is because a number of files are created both in
setting up and performing the calculation and starting with a clean directory
will help keep things organized.

3. Check a calculation's documentation
======================================

Each calculation has documentation broken into two major components: main
documentation and methods and theory.  The main documentation gives a general
overview of what the calculation does and who created it, while methods and
theory give a more detailed description of the underlying theory and how it is
implemented in the calculation's code.  Note that all variations described
below are based on the same underlying documentation files and therefore should
be providing the same content.

3.1. Online
-----------

Each supported calculation style is described in the online documentation found
at https://www.ctcms.nist.gov/potentials/iprPy/calculation_styles.html.  There,
you can click on a specific style and see a small list. The first two bullets,
"Introduction" and "Method and Theory" link to the related web pages for the
two types of documentation.

3.2. Command line
-----------------

.. code-block:: bash

    $ iprPy maindoc isolated_atom
    $ iprPy theorydoc isolated_atom

3.3. Python
-----------

.. code-block:: python

    calc = iprPy.load_calculation('isolated_atom')
    print(calc.maindoc)
    print(calc.theorydoc)

If you are in a Jupyter or iPython environment, the raw markdown can be
automatically converted to pretty HTML

.. code-block:: python

    from IPython.display import display, Markdown
    display(Markdown(calc.maindoc))
    display(Markdown(calc.theorydoc))

3.4 Source files
----------------

You can also view the documentation files directly if you have downloaded a
copy of the source code.  Inside iprPy/calculation are subdirectories for each
calculation style.  Each one of those then contains "README.md" and "theory.md"
files that contain the documentation.

4. Calculation input parameters
===============================

Each calculation has its own set of input parameters that it recognizes which
can be specified inside a text file consisting of key-value input command
lines.  The rules of the input parameter files are simple:

- Each line is treated independently and split into white-spaced delimited
  terms.

- Any terms listed after a "#" will be treated as comments and ignored.

- The first term on any given line corresponds to a parameter name, i.e. a key.
  Any other terms following it are interpreted as the value(s) to assign to
  that parameter.

- If only a parameter name appears on a line with no values (i.e. there is only
  one term) then the line is ignored.

- Each parameter can be assigned at most one set of values.  In other words,
  there can only be one line per parameter name that has more than one term in
  it.

- Any parameters not assigned values will be given default values if the
  calculation allows it or will issue an error for required parameters.

4.1. Command line
-----------------

The template command will create an empty version of a calculation's input
script consisting of only the recognized parameter names and no values.  The
generated file will be named calc_<calc_style>.in and can be opened using any
text editor.

.. code-block:: bash

    $ iprPy template isolated_atom

A description of the terms in the input parameter file can be viewed using the
templatedoc command.

.. code-block:: bash

    $ iprPy templatedoc isolated_atom

4.2. Python
-----------

Similarly, the template and templatedoc content can be viewed from within
Python by using the template and templatedoc attributes of a Calculation
object.

.. code-block:: python

    print(calc.template)
    print(calc.templatedoc)

or in Jupyter/iPython

.. code-block:: python
    
    display(Markdown(calc.templatedoc))

If you wish, the input file content can alternately be specified as a Python
dict containing the parameter names and values to use.  This makes it possible
to run the calculation without needing to generate the input file.

Alternatively, the underlying calculation methods can be directly executed in
Python.  For each calculation class, the primary calculation function is
accessible by the calc() method.  The full docstring for that function can be
viewed in many Python editors or can be viewed with

.. code-block:: python

    print(calc.calc.__doc__)

Currently, work is being done to support a more Pythonic approach to performing
the calculations in which all parameters can be directly set to a calculation
object as attributes prior to running.

5. Running the calculation
==========================

Once the calculation's input values are set, you can run the calculation.

5.1. Command line
-----------------

The run command will run the calculation using the input script you filled in.
If you used the default input script name (calc_<calc_style>.in) then you can
simply pass the input file in

.. code-block:: bash

    $ iprPy run calc_isolated_atom.in

If you renamed the input file to something else, then you will also need to
specify the calculation style.

.. code-block:: bash

    $ iprPy run input_set_1.in isolated_atom


When the calculation finishes successfully, a **record.json** record file will
be created containing the processed results.  This can then be viewed in any
text editor or imported into any software that can interpret JSON. 

5.2. Python
-----------

The Calculation classes contain a number of methods that allow for the
associated calculations to be performed.

- **run()** is the primary method for running the calculation.  It will run the
  calculation based on a provided input parameter file or dict, or based on the
  input parameter attributes currently set to the Calculation object.  Upon
  completion, the calculation results will be set as class attributes. A
  "results.json" file can be automatically generated if requested.

- **calc()** is an alias for the underlying calculation function allowing for
  it to be directly accessed and called.  This makes it possible to manually
  set up the calculation's inputs and work with the function itself.  When
  completed, the function will return a Python dict containing computed
  results terms.

- **load_parameters()** will read a input parameter file or dict and interpret
  the provided values into attributes of the current Calculation object.  In
  short, this interprets and manages the calculation's inputs without running
  it.

- **process_results()** takes the dict returned by calc() and interprets the
  contained values into attributes of the current Calculation class.  This
  makes the results directly accessible in a Pythonic way and allows for
  analysis methods to be built into the Calculation classes themselves.  Note
  that run() will automatically call this.

- **build_model()** will construct a JSON/XML equivalent data model based on
  the Calculation object's current set attributes.  This makes it possible to
  generate JSON/XML records for a calculation both before and after it has been
  ran.  Note that the required attributes will not be set if calc() is accessed
  directly rather than using the other methods listed above.

.. code-block:: python

    calc.run(params=filename, results_json=True)

or equivalently

.. code-block:: python
    
    calc.load_parameters(params=filename)
    calc.run()
    with open('results.json', 'w', encoding='UTF-8') as f:
        calc.build_model().json(fp=f, indent=4, ensure_ascii=False)

or (assuming lammps_command and potential are defined for the calculation)

.. code-block:: python
    
    results_dict = calc.calc(lammps_command, potential)
    