=============================
Adding new calculation styles
=============================

This page outlines the general steps associated with defining a new calculation style and implementing it into iprPy.

1. Create a directory for the calculation style files
=====================================================

Each calculation style exists as a number of separate files.  So, the first step in creating a new calculation style is to create a directory to store those files.  The default location where iprPy calculations can be found is inside the iprPy/calculation directory.  This is recommended, especially if you wish that your calculation style eventually be included as part of iprPy.

Alternatively, the calculation style folder could exist in a separate Python package that can be imported.  

2. Define a calculation function
================================

At the core of each iprPy calculation style is a single Python function that serves as the primary entrypoint for executing the calculation method.  Note that the method itself need not be a single function or file, only that there be a sole "main" function to call it.

The only other requirement is that iprPy be able to find and import the calculation function.  This typically is done by placing the calculation function and any supporting code inside a Python script that is then placed inside 

However, there are a few recommendations in how the code should be designed to assist with clarity

- The code should be well documented with informational comments every few lines and docscrings for any functions and classes.  The numpy docscring style https://numpydoc.readthedocs.io/en/latest/format.html is preferred for consistency with other calculations.
- The main calculation function should take Python objects and data types as inputs.  These inputs should be meaningful to the calculation method and include as many options that future users may want to modify and explore.
- The main calculation function should return any generated results data inside a Python dict.  This not only provides names for the generated results fields but also makes the returned values extensible either in future versions of the function or by other functions.
- If the new calculation method is similar to already existing ones, try to adhere to some consistency in how input/results terms are named and the order in which they are listed.  This can help avoid possible confusion for those working with multiple calculations.
- If the calculation relies on reading non-Python data files, it is recommended that they be read in using the iprPy.tools.read_calc_file() function.  This function will read the file from the current working directory if it exists there, or will read it from a specified Python package location otherwise.  The utility of this is it makes it possible for anyone interacting with the Notebook version of the calculation to modify the data file in the Notebook.

3. Create documentation files
=============================

Each calculation style has two primary documentation files associated with it.

**README.md** gives a quick overview of the calculation.  This provides simple details such as

- A list of authors for the calculation style.
- A short introduction description of the calculation.
- Version notes.
- Any additional Python package dependencies.
- Disclaimers about usage and limitations of the method.

**theory.md** provides additional "Method and theory" content for the calculation.  This allows for more in-depth descriptions of the theory behind what the calculation is doing as well as any important specifics associated with the current implementation.  When needed, any equations should be represented in the Latex-math-style format supported by MathJax. 

4. Define the Calculation class
===============================

The Calculation class provides the interface for iprPy to find the calculation function and any associated components.  This section provides some basic information for defining a new Calculation class.

The class definition needs to exist in the calculation style directory as it expects that most supporting files can be found in the same folder.

4.1. Core components
--------------------

These are the core class definition settings and attributes.

4.1.1 Class definition
``````````````````````

The Calculation class itself should be named for the calculation style and be a child of iprPy.calculation.Calculation.

4.1.2. Class initializer
````````````````````````

The class initializer should
- Define a class attribute for each Calculation subset that is used.
- Set default values for any calculation-specific attribute values (see Section 4.4).
- Set self.calc to be the calculation function imported from wherever it was defined.
- Call super() for the parent Calculation class' init.  Pass the parent init all of the parameters of the current class init plus a list of the subset objects.

4.1.3. filenames
````````````````

Filenames provides a list of all files, both Python and non-Python, that are required by the calculation.  This lets prepare know what files to copy.

4.1.4. Class attributes
```````````````````````

Most of the universal class attributes are defined by the parent class leaving developers to only worry about the calculation-specific terms.  These typically fall into one of three categories

- subset attributes: these point to the individual subset objects created in the init.  No setter should be defined for these.
- unique input attributes: these are the input terms specific to the calculation that are not included in any subset.  It should be possible to directly set the values or use methods to set the values.
- results attributes: these interpret the results returned by the calculation.  Trying to access these terms when the calculation has not been performed should raise an error.

4.1.5. set_values
`````````````````

The set_values method allows for any of the input attributes, both for the class and any subset, to be set at the same time.

4.1.6. isvalid
``````````````

The isvalid() method returns a bool that indicates if the set input attributes have valid and non-conflicting values.  This is used by prepare to filter out any calculations that could have invalid combinations of input parameters.  The parent Calculation.isvalid() always returns True so defining the function is optional if no checks need to be performed.

4.2. Parameter file interactions
--------------------------------

These manage the input parameters that the calculation can read in from the key-value input parameter text file.

4.2.1. load_parameters
``````````````````````

The load_parameters method loads and interprets a key-value input parameter file for the calculation and updates the associated class attributes based on the values read in.  How this is done for each input parameter term depends on if the term is part of a subset and the parameter's data types

- The method should start by calling super().load_parameters.  This will convert the input file into a dict (input_dict) and set any universal terms.
- Any values associated with a subset can be set by calling the subset's load_parameters() method and passing it the input_dict of.
- NOTE that the order of subsets called can be important as some subsets rely on values interpreted by others.
- All terms in the input_dict are initially strings.  Be sure to use int() or float() when interpreting integer or unit-less float values.
- Boolean terms can be interpreted with iprPy.input.boolean().  This will properly convert the str representation to a bool.
- For floating point terms with units, use iprPy.input.value().  This makes it possible to interpret strings that contain units, define default units, and define a default value with units for the term.  

4.2.2. templatekeys
```````````````````

templatekeys is a dict that specifies all of the terms recognized by the calculation's input parameter file that are unique to the calculation, i.e. not universal or part of a subset.  The dict's keys give the names of the terms and the dict's values provide descriptions for the terms.  This is used to generate the template and templatedoc fields associated with the unfilled input file and the accompanying documentation.

4.2.3. singularkeys and multikeys
`````````````````````````````````

These categorize the recognized input keys according to how prepare should treat them if multiple values are given.  Note that each subset has a keyset attribute that lists all associated input terms. 

- singularkeys lists all keys that are limited to a single value when preparing.  In other words, these are not looped over.
- multikeys lists which terms can have multiple values and how they are grouped into parameter sets.  Each parameter set indicates that the values for all included terms should be iterated over together.

4.2.4. master_prepare_inputs
````````````````````````````

The master_prepare_inputs() method builds a dict of prepare input parameters based on a pre-defined standard.  Using a "master_prepare" can be convenient as it only requires the end users to specify modifications to the prepare terms rather than fully defining the prepare terms from scratch.

Multiple different standard prepare settings can be defined for the same calculation by associating the settings with different "branch" values.  For instance, there may be different branches based on the style of input records used or to target multiple specific input parameter combinations.

For each branch, a dict of prepare parameters is constructed that defines the initial default values for that master_prepare branch.  Then, any kwargs given to master_prepare_inputs() are added to the dict which either extends it or changes the default values.  Once done, the dict is returned and can immediately be passed to the prepare method of a Database.

4.3. Data model interactions
----------------------------

These manage how the data is represented as a tree-like data model that can be equivalently stored as JSON or XML. 

4.3.1 modelroot
```````````````

To be XML-compatible, all calculation data models have a single root element.  The modelroot attribute specifies what the root element name is.  Defining this allows for associated content to be discoverable in a record and allows for the subset data model operations to work across all calculations.

4.3.2. build_model
``````````````````

The build_model() method constructs a data model for the calculation instance based on the current set input and results attributes.  Subelements can be built based on the calculation subsets using their build_model() methods.  This leaves only the unique calculation parameters to need to be defined.  The generated data model will will be both returned and set to the calculation object's model attribute.  The data model is generated as a DataModelDict which has built-in tools for converting to JSON or XML.

One useful tool for constructing the data model terms is atomman.unitconvert.model.  This allows for any parameter to be output in a small DataModelDict consisting of a value and the specified units that the value is in.  The value can be a single float or an array of values of any shape.  It also has the option to specify an error associated with the value.

4.3.3. load_model
`````````````````

The load_model() method reads in the data model contents of a record and saves the extracted values to the object's attributes.  Any defined subsets are automatically interpreted by calling the super().load_model() method leaving only the conversions for the calculation-specific terms to be defined.

Useful tools for loading the model are atomman.unitconvert.value_unit and atomman.unitconvert.error_unit.  These are the reverse of atomman.unitconvert.model in that they read in the values and convert them from the specified units into working units.  value_unit operates on the primary value of the value models, while error_unit operates on the error field.

4.3.4. mongoquery and cdcsquery
```````````````````````````````

These methods construct Mongo-style queries that are designed to limit returned results according to specified values.  A specific query style is associated with each allowed parameter that then operates on an element in the record.

These rely on the yabadaba.query options and can be specified in the method descriptions or defined as Query objects in a separate queries attribute.

4.4. Metadata interactions
--------------------------

These manage the terms that appear in the metadata dict that can be generated for the calculation to provide a quick means of comparing multiple instances of the same calculation.

4.4.1. metadata
```````````````

The metadata method returns a dict containing terms for the calculation that can be represented as basic Python data types.  The dict should also be flat or at most one level of embedding.  These metadata dicts allow for quick comparisons between different instances of the same calculation.  The included terms and structure should be simple to minimize conversion time and allow for simple comparison operations.

4.4.2. compare_terms and compare_fterms
```````````````````````````````````````

These are used by prepare to compare proposed calculation instances with the existing ones.  If all listed terms are deemed to match with an existing record, then it is considered a duplicate and skipped.

- compare_terms lists the metadata terms that must have exactly the same values to be considered a match.  These are typically str, bool or int values.
- compare_fterms is a dict that specifies metadata float values to compare.  The dict's keys are the term names and the dict's values are absolute tolerances to use when comparing the values.

4.4.3. pandasfilter
```````````````````

The pandasfilter() method defines operations that filter a pandas.DataFrame based on values given for metadata terms.

These rely on the yabadaba.query options and can be specified in the method description or defined as Query objects in a separate queries attribute.


4.5. Calculation interactions
-----------------------------

These provide functions that manage how to convert terms between the class attributes and the calculation function inputs/results.

4.5.1. calc_inputs
``````````````````

The calc_inputs method transforms the set class attribute values into the input parameter terms for the calculation function.

4.5.2. process_results
``````````````````````

The process_results method takes the dict of results returned by the calculation function and interprets them into class attributes.

5. Link the calculation to the calculation manager
==================================================

Once a Calculation class has been defined, it can be incorporated into iprPy by importing it with iprPy.calculationmanager.import_style().  import_style takes the following parameters:
- The style name to associate the calculation with.
- The file name that contains the class definition.
- The module where the class definition file is located.
- Optionally, if the file name is different from the class name, the class name is given here.

6. Make a Jupyter Notebook and demo script
==========================================

The final step is to create demonstrations so that users can see the calculation in operation.  This is done by creating a Jupyter Notebook for the calculation and a demonstration input script.

6.1. Jupyter Notebook
---------------------

Jupyter Notebooks for each of the calculations can be found in the notebook directory of the iprPy repository.  When creating a new one, it is highly recommended to start from an existing one.  

6.1.1. Initial information
``````````````````````````

The first cells in the Notebook should load the calculation from iprPy and display the calculation's maindoc and theorydoc.  This tests that the calculation was successfully imported and provides the general knowledge about what the method does.

6.1.2. Copy calculation code
````````````````````````````

The next cells should contain a copy of the primary calculation function as well as any other required functions and data files.  Copying the code and data files into the Notebook not only lets users see how the calculation is implemented but also makes it possible for them to easily modify the calculation should they wish. 

6.1.3. Define input parameters
``````````````````````````````
Input parameters for the calculation function are then set up and defined.  These should be the parameters that the function itself takes and not the input parameter file terms.  BE sure to check other existing Notebooks and copy any related parameter definitions from them as appropriate for consistency.

6.1.4. Run the demo and display results
```````````````````````````````````````

Using the defined calculation inputs, call the calculation function directly and show what terms are in the returned results dict.  Then, provide formatted interpretations of the results data.

6.2. Demo script
----------------

The demo directory in the iprPy repository contains a demonstration input script for each fully implemented calculation.  Users should be able to go into any of the calculation-specific subdirectories and run the demo script for that calculation style simply by typing iprPy run <calcscript>.

If any of the calculation inputs are separate files, put those files in the "0-files" directory.  This allows for git to identify those files and makes it easy for the same input files to be shared by multiple demo scripts.