# Introduction

The curator Database style interacts with an instance of the Materials Database
Curation System (MDCS). Records are stored in the MDCS instance as validated 
XML. With this method, a remote MDCS instance can be set up and accessed by 
multiple computing resources.

## Style requirements

- Access to a working MDCS instance.

- The [Python MDCS-api-tools](https://github.com/lmhale99/MDCS-api-tools)
  package needs to be installed. Note that this is still early development.

## Initialization arguments:

- __host__: the URL for accessing the MDCS instance.

- __user__: the username to use to access the MDCS instance.

- __pswd__: the corresponding password for user, or path to a file containing 
  the password.

- __cert__: the directory path to a web certification file, if required by the 
  MDCS instance.

## Additional notes:

- Adding records to an MDCS instance requires a valid XSD schema for each record 
  style, and that each corresponding XML record be consistent with that schema.
  
- The current version does not support delete_tar() or update_tar().