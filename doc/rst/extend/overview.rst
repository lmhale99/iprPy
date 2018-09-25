
iprPy Package Overview
**********************

It is helpful to understand what the different components of the iprPy
package are before going into how to add to them.  This page provides
a brief explanation of the conceptual and computational components of
the framework.


Conceptual Components of iprPy
==============================

The iprPy computational framework consists of four primary conceptual
components: records, calculations, databases, and supporting code.

* **Records** collect reference input information and calculation
  results as structured data.  The information exists in an XML/JSON
  equivalent form.

* **Calculations** are the heart of the iprPy framework.  Each
  calculation is a Python script that performs an independent unit of
  work in isolation from any other calculation.  A calculation reads
  in all variable input parameters from a simple key-value format, and
  generates a results record upon successful completion.

* **Databases** are where the input and calculation records are
  stored.  Interactions with a database allow for calculations to be
  prepared and executed in a high-throughput fashion, and for the
  produced records to be accessed, explored, and analyzed.

* **Supporting code** provides tools for interacting with different
  records, calculations, and databases in a similar manner.  It also
  provides common functions for interpreting specific parameter inputs
  that can be shared across similar calculations.


Modular Components of the iprPy Package
=======================================

The supporting code is provided by the iprPy Python package.  The
components of the package are modular to provide generality of the
method and allow for new content to be easily added.  In particular,
there are three class types and two functions that are modular and
allow for new “styles” to be implemented.  For the classes, each
implementation style exists as a subclass of the parent class.  For
the functions, each implementation style takes input parameters and
performs actions in a common manner.  Additionally, the record entries
themselves can be thought of as modular components that define
parameter sets used by the various calculations.

* **Reference records** can be found in the iprPy/library directory.
  Each reference entry corresponds to a defined calculation style and
  defines a set of parameters that can be interpreted by one or more
  calculations.

* The **Record class** defines methods for generating, comparing, and
  interacting with records of different styles.  Each Record style
  corresponds to a unique schema, i.e. data and metadata fields.

* The **Calculation class** defines methods for accessing metadata
  associated with a calculation, such as the allowed input parameters
  and the Record style the results are saved as.  Each Calculation
  style corresponds to a different implemented calculation.

* The **Database class** defines methods for interacting with records
  stored in a database.  This includes simple interactions, such as
  adding and accessing records, as well as complex interactions, such
  as preparing and running calculations in a high-throughput manner.
  Each Database style corresponds to a different type of database,
  such as a local directory, an MDCS database or a MongoDB database.

* The **input.interpret functions** interpret a collection of
  calculation input parameters in a specific manner that can be shared
  across multiple Calculation styles.  These help in the development
  of new Calculation styles and provide consistency in input
  parameters across calculations.  They also provide a means of
  interpreting information from records that can be used for
  calculation inputs.  Each input.interpret style is associated with
  interpreting a specific set of calculation input parameters.

* The **input.buildcombos functions** support preparing calculations
  for high-throughput runs by defining combinatorial logic specific to
  multiple calculation input parameters.  These make it easier to
  prepare new simulations based on available reference and calculation
  records.  Each input.buildcombos style generates lists of values for
  a set of calculation input parameters based on a Record style stored
  in the database.
