# curator Database style

## Introduction

The curator Database style interacts with an instance of the Materials Database Curation System (MDCS).  Records are stored in the MDCS instance as validated XML.

## Style requirements

- Access to a working 1.X MDCS instance.

- The included mdcs.py file, which uses Python to define REST interactions with a database.

## Initialization arguments:

- __host__: the URL for accessing the MDCS instance.

- __user__: the username to use to access the MDCS instance.

- __pswd__: the corresponding password for user, or path to a file containing the password.

- __cert__: the directory path to a web certification file, if required by the MDCS instance.

## Additional notes:

- With this method, a remote MDCS instance can be accessed by multiple computing resources.

- Adding records to an MDCS instance requires a valid XSD schema for each record style, and that each corresponding XML record be consistent with that schema.
  
- There are no functions for update_tar and delete_tar as the current versions of MDCS do not allow the associated files to be deleted.