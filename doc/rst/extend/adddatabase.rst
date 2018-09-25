
Databases
*********

This section describes the components of a Database style in more
detail as well as tips for those wanting to add a new Database style
to the framework.


Database directories
====================

All databases styles are stored in subdirectories of the
iprPy/database directory, with directory named for the database type,
i.e. [databasename].  Each directory contains:

* **[DatabaseName].py**: Includes the definition of a Python class
  that is a subclass of iprPy.database.Database.  This defines how the
  iprPy codebase interacts with the database type.

* **README.md**: Descriptions of what the database type is and how to
  define the access parameters.

* **__init__.py**: The Python init file allowing Python to interpret
  the database directory as a submodule of the iprPy package.

* Any other supporting files.


Database classes
----------------

The Database classes handle interactions with different types of
databases in a common way.  The methods can be divided into two
categories:

* Methods for adding and accessing content stored in the database.
  The underlying code for these methods need to be defined for each
  Database style to properly interact with a type of database.

* Methods supporting high-throughput calculations.  These are defined
  by the parent Database class and do not need to be redefined.
