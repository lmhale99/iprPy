Introduction
============

The curator Database style interacts with an instance of the Materials
Database Curation System (MDCS). Records are stored in the MDCS instance
as validated XML. With this method, a remote MDCS instance can be set up
and accessed by multiple computing resources.

Style requirements
------------------

-  Access to a working MDCS instance.

-  The `Python
   MDCS-api-tools <https://github.com/lmhale99/MDCS-api-tools>`__
   package needs to be installed. Note that this is still early
   development.

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

-  Adding records to an MDCS instance requires a valid XSD schema for
   each record style, and that each corresponding XML record be
   consistent with that schema.

-  The current version does not support delete\_tar() or update\_tar().
