Introduction
============

The local database style stores and accesses JSON records from a local
directory.

-  With no active server requirements, these are trivial to set up and
   use but lack sophisticated, quick querying abilities.
-  Using a local Database is useful for testing purposes as the records
   can be accessed directly through the operating system’s file
   explorers.
-  Multiple local Databases can be defined on one computer allowing for
   groups of calculations to be stored separately. An example of when
   this is useful is to run parameter sensitivity tests without the test
   results being mixed in with the primary data.

Version notes
~~~~~~~~~~~~~

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Initialization arguments
------------------------

-  **host**: the path to the local directory to use for the database.
