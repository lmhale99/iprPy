============================
Execute a Calculation Script
============================

Each calculation exists in two forms: a Python script and a Jupyter Notebook.  Both versions of the calculation contain the same underlying calculation methods and functions, but differ with input/output interfaces and how the information is presented.

Calculation directories
-----------------------

All calculations are stored in subdirectories of the iprPy/calculation directory, with directory named for the calculation, i.e. [calcname].  Each directory contains:

- **README.md**: A short description of what the calculation does.

- **THEORY.md**: A more in-depth discussion of the calculation's methodology and the underlying theory.

- **calc_[calcname].py**: The Python calculation script.

- **calc_[calcname].template**: A template version of the input parameter file that the calculation script reads.

- **[CalcName].py**: Defines a subclass of iprPy's Calculation class so that iprPy can find the calculation and set up runs.

- Copies of any other files required by the calculation.

Calculation input/template file
-------------------------------

The input parameter files that the calculations read in all follow the same simple format.

- The parameters are given in key-value format, with each line listing a parameter followed by its assigned value.

- Any parameters that are not listed or not given values will be ignored and be given default values, if allowed by the calculation.

- Any terms listed after a # will be treated as comments and ignored.

- Only one value can be assigned to each parameter, i.e. each key can only appear on one non-comment line with a corresponding value.

The calc_[calcname].template files serve as template input parameter files used when preparing the calculation for high-throughput runs.  These template files list all available parameters, and have values corresponding to the parameter name surrounded by angular brackets '<' and '>'.  A list of all terms allowed by the calculation can also be accessed from Python by loading the calculation's associated class and calling the Calculation object's allkeys attribute.

Running the calculation script
------------------------------

The easiest way to perform a calculation is to:

#. Copy the calculation directory to another location (this keeps the original directory from becoming cluttered).

#. Copy the calc_[calcname].template file to calc_[calcname].in.

#. Edit calc_[calcname].in by deleting all terms surrounded by angular brackets '<' and '>', and providing any necessary values to parameters.

#. In a terminal, cd to the calculation folder you created, and enter::
        
        python calc_[calcname].py calc_[calcname].in
     
#. When the calculation finishes successfully, a "record.json" record file
   will be created containing the processed results.

Looking at the results
----------------------

The results.json file contains metadata and the calculation's results in a structured format.  Values can be manually extracted by opening the file in a text editor, or can be processed by any computer language that supports json parsing.  In Python, the iprPy supporting code can load the results file as a Record object which has methods for comparing calculations and simplifying the complex tiered format down to a simple single level dictionary.