
Analysis
********


Accessing the data
==================

The design of the Record and Database classes make accessing
calculation data for analysis simple.  The easiest way to do so is to
use the get_records_df() method of a Database object to compile all
records of a given style into a pandas.DataFrame:

::

   results_df = dbase.get_records_df(style=calc_style, full=True, flat=False)

The columns of the produced DataFrame are dependent on the record's
style and the values of the *full* and *flat* arguments.  For *full*,
a value of False will only include input parameters and the
calculation's status, whereas a value of True will also contain
results.  For *flat*, a value of True will limit data fields to having
values with simple, single valued data types for easy comparison,
whereas a value of False can have values of any data type or object
better suited for representing complex data.

While the columns do differ from one record style to the next, there
are a few expected common column names for calculation records.

* *calc_key* is the unique UUID key assigned to the calculation
  instance. This corresponds to the name used for identifying the
  calculation record in the database.

* *calc_script* is the name of the calc_*.py file used to perform the
  calculation.

* *iprPy_version* gives the version of iprPy that was used to perform
  the calculation.

* *status* indicates the current calculation status.  Allowed values
  are 'completed', 'error', and 'not calculated'.

* *error* contains the string error message if the calculation issued
  an error.  Otherwise, the value is empty/NULL.

Alternatively, the data can be accessed as Record objects using the
get_record() and get_records() methods of the Database class.  Each
Record object contains the record's XML content, which can be explored
as such.  All three of the get_record methods also allow a single
record or list of records to be given that limits the returned data to
only those corresponding records.

**Note**: The current design places nearly all record filtering and
parsing on the client side, i.e. all matching records are opened/read,
then parsed locally.  This is no issue for local style Databases, but
can be troublesome for accessing curator style Databases that contain
lots of data.  In particular, downloading all records of a given style
at once may take considerable time and/or fail.  Ways to pre-filter
the data on the server side are being investigated.


Analyzing the data
==================

Once the data is loaded as a DataFrame, it can easily be manipulated
using the methods and tools of the pandas package.  How to process,
analyze and compare the resulting data is largely dependent on the
calculation and what is of interest.

Example analysis scripts and Notebooks as used for generating content
on the Interatomic Potential Repository website are included in the
iprPy/analysis subdirectory.  **Note**: This component of iprPy is in
active development and will likely see major changes in the 0.7.x
versions.
