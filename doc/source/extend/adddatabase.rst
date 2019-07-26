==========================
Adding new database styles
==========================

The basic steps associated with implementing a new database style in iprPy are

#. Create a new subdirectory in iprPy/database named for the new database
   style.

#. Create a file that defines the Database subclass.  Name the file
   after the subclass name, typically by converting the style name to upper
   camel case (each word capitalized with no separators).

#. Define the database subclass initialization function to handle any
   style-specific parameters for accessing the database.

#. Define the methods for getting, adding, updating and deleting records and
   tar archives to/from the database style.

#. Create an "\_\_init\_\_.py" file that imports the subclass.

#. Write documentation for the database style in the README.md file.

Files in the calculation style directories
------------------------------------------

- **[Style].py**: Defines the Database subclass for the database style.
  This defines how the iprPy codebase interacts with the database.

- **README.md**: Descriptions of what the database type is and what the
  access parameters are.

- **\_\_init\_\_.py**: Allows Python to identify the database directory as
  a sub-package and be able to import the database subclass into iprPy.

[Style].py
~~~~~~~~~~

The iprPy package interacts with the database style through the defined
Database subclass.  Considerable work has gone into making it easy to
define new subclass definitions by modifying values in pre-existing subclass
definitions.  This section describes the different components of defining a
Database subclass.

All of the high-throughput interaction functions are defined in the parent
class.  Only style-specific functions need to be defined for getting, adding,
updating and deleting stored records and calculation tar archives to/from the
database in the subclass.

Inheritance
...........

The class should be a child of iprPy.database.Database.

\_\_init\_\_()
..............

The \_\_init\_\_() function interprets any parameters needed to access a
database of the given type.  After establishing/defining a connection, the
parameters or objects to interact with the database are saved.  Finally, the
parent class' \_\_init\_\_() method is called to set the database host name and
other common attributes.

Record interaction functions
............................

- get_records() returns a list of Record objects matching the conditions given.

- get_record() returns a single Record object if exactly one uniquely matches
  the conditions given.

- get_records_df() returns a pandas.DataFrame in which the records matching the
  conditions given are transformed into flat dictionaries and then collected
  together.

- add_record() adds a single record to the database.

- update_record() updates a single record stored in the database.

- delete_record() deletes a single record stored in the database.

Archive interaction functions
.............................

- get_tar() returns a tarfile.TarFile object containing the archived
  calculation folder content for a specific record.

- add_tar() archives a calculation folder associated with a single record and
  adds it to the database.

- update_tar() updates the archived content for a single record stored in the
  database.

- delete_tar() deletes the archived content for a single record stored in the
  database.

\_\_init\_\_.py
~~~~~~~~~~~~~~~

The \_\_init\_\_.py file simply needs to tell Python to include the Database
subclass.  For instance, if the subclass is called "Style", then
\_\_init\_\_.py contains

.. code-block:: python

    from .Style import Style
    __all__ = ['Style']
