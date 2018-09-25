Introduction
============

The curator Database style interacts with an instance of the Materials
Database Curation System (MDCS). Records are stored in the MDCS instance
as validated XML.

Style requirements
------------------

-  Access to a working 1.X MDCS instance.

-  The included mdcs.py file, which uses Python to define REST
   interactions with a database.

Initialization arguments:
-------------------------

-  **host**: the URL for accessing the MDCS instance.

-  **user**: the username to use to access the MDCS instance.

-  **pswd**: the corresponding password for user, or path to a file
   containing the password.

-  **cert**: the directory path to a web certification file, if required
   by the MDCS instance.

Additional notes:
-----------------

-  With this method, a remote MDCS instance can be accessed by multiple
   computing resources.

-  Adding records to an MDCS instance requires a valid XSD schema for
   each record style, and that each corresponding XML record be
   consistent with that schema.

-  There are no functions for update\_tar and delete\_tar as the current
   versions of MDCS do not allow the associated files to be deleted.
