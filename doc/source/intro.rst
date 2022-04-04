=====================
Introduction to iprPy
=====================

What problems does iprPy attempt to address?
============================================

The iprPy package is designed to provide a means for sharing both the knowledge
and capabilities associated with calculation methods.  This is important for
verification, validation and reproducibility of research results as anyone
wishing to check someone else's work needs to both know how the calculations
are done as well as being able to do it themselves.

Here are some examples of issues that often arise that can in part be addressed
through the use of iprPy or similarly designed works

- Traditional publications are the classic way of sharing scientific knowledge.
  However, they are static documents and any associated methodologies are
  described in an abstract sense using the human language of the paper.  Anyone
  wishing to use the methods either needs to create an implementation
  themselves or obtain one from an external source.  If the description
  contains one or more critical typos would it make reproducing the work
  impossible?

- Research practices often focus on the traditional publication being the final
  end product of any research work done.  To this end, the methodologies used
  to generate the data for the paper often exist in forms that only the
  researcher involved in the work knows how to use it.  In this situation,
  how does the current researcher pass their work on to others in their group
  when they move to a different job or subject area?  If the researcher leaves
  the work alone and attempts to revisit years later, can they figure out what
  their past selves had done?  Can they even find all of the necessary files to
  do the work after transferring between computers and/or archiving?

- Many methodologies and tools exist as so-called "black boxes" in which
  a compiled program accepts a set of inputs, does some hidden work, and then
  returns processed results.  While this provides a means of sharing the
  capability, it obscures the methodology making it difficult for users to work
  out exactly what the method is doing.  How do external users know that the
  black box method is doing what it claims to be doing?  If there is an issue
  or bug with the code, is there an easy means of fixing it?

It's all in the design
======================

With iprPy, the idea is to avoid these complications beforehand through
proper calculation design.  In short, a little extra work now will result in
much benefit later on as users can understand, share and revisit methods
with ease.

- All calculation methods are represented in Python.  Python is a scripting
  language meaning that the Python scripts simultaneously represent the
  programming code and detail the workflow associated with a specific
  calculation.  By sharing the Python scripts as open source tools, users can
  access and explore how the methods work.

- Each calculation method exists as a Python function that serves as a
  self-contained and independent unit of work.  It should represent the
  workflow associated with a single run of the specific calculation method and
  be minimally dependent on the framework in which it is contained.
  Additionally, it should be possible to independently execute each calculation
  function by providing only Python objects and simple data types as inputs.
  These design considerations form the basis of making it possible for the
  calculation functions to be individually ran or incorporated into a variety
  of external workflows.
  
- The calculations are incorporated into the iprPy framework using so-called
  Calculation classes.  Each Calculation class defines metadata
  associated with the calculation so that the class

  - Connects to the underlying calculation function.
  
  - Specifies data transformations and schemas allowing for the inputs and
    results to be represented in a variety of formats.
  
  - Links to extra files associated with the calculation, such as
    documentation, data files required by the calculation function, and schema
    files for validating generated data.
    
- Users in a Python environment can load a Calculation class from iprPy.  The
  class provides methods for exploring the calculation's documentation and list
  of supported inputs, as well as a means of calling the calculation function.
  The class can also have built-in methods for processing and interpreting the
  generated results in a user-friendly manner, such as methods that generate
  standard plots.

- The Calculation classes also make it easy to build Jupyter Notebooks for the
  calculations that display documentation, contain a copy of the calculation
  function and any data files, and a working demonstration.  This provides a
  single file that fully documents the knowledge, capabilities, and code of
  the method that can easily be shared with others.  It also allows for curious
  users to test modifications of the methods without any fear of breaking the
  official versions.

- Additionally, the input/output conversions specified in the Calculation
  classes makes it possible for the calculations to be executed using only text
  input files and terminal command lines.  This allows for trusting users to
  execute the calculations as box methods without needing to know any Python.
  Upon successful completion, the calculations will generate JSON results files
  that can either be viewed in a text editor, uploaded to a database, or
  interpreted by other programs. 

- Larger workflows can be built that link and loop over multiple calculations
  either by loading and executing the functions from a Python environment or
  by automating the construction of the text input files.  The iprPy framework
  contains its own workflow tools that allow for outputs from one calculation
  to be passed into another, and for all results to be automatically added to
  a database.

How much extra work?
====================

One of the greatest challenges for any infrastructure such as iprPy is that
any potential users need to evaluate the worth of using the framework to be
larger than the cost associated with learning how to use it.  To this end,
much of the improvements to iprPy over the years have focused on lowering the
barriers for usage.

- For users who simply want to use the implemented calculations, iprPy can
  easily be installed using pip or conda through conda-forge.

- For individuals who want to see how the calculations are done, the
  code is readily available on github.  This includes the Jupyter Notebook
  versions of the calculations, which can be downloaded and executed.
  Alternatively, the Notebook versions are also included in the online
  documentation making it possible for users to see the code and methods
  prior to any downloading.

- For method developers, they can download the code from github then add their
  own calculation methods or modify any of the existing ones.  Each calculation
  is treated in a modular fashion making it easy to incorporate new methods
  into the framework.  The above design also means that people can contribute
  just calculation functions with no specific knowledge of the iprPy framework
  design, and then others can work with them to define the Calculation classes.