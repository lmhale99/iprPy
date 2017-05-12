# curator Database style

--------------------------------------------------------------------------------

**Lucas M. Hale**, 
[lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), 
*Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, 
[chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), 
*Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, 
[zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), 
*Materials Measurement Science Division, NIST*.

Version: 2017-05-01

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
--------------------------------------------------------------------------------
## Introduction

The curator Database style interacts with an instance of the Materials Database
Curation System (MDCS). Records are stored in the MDCS instance as validated 
XML. With this method, a remote MDCS instance can be set up and accessed by 
multiple computing resources.

## Additional style requirements

Using this style requires access to a working MDCS instance, and for the Python 
MDCS-api-tools to be installed as the mdcs Python package. 

## Initialization arguments:

- __host__: the URL for accessing the MDCS instance.

- __user__: the username to use to access the MDCS instance.

- __pswd__: the corresponding password for user, or path to a file containing 
  the password.

- __cert__: the directory path to a web certification file, if required by the 
  MDCS instance.

## Additional style notes:

- Adding records to an MDCS instance requires a valid XSD schema for each record 
  style, and that each corresponding XML record be consistent with that schema.
  
- The current version does not support the delete_tar() method. This will be 
  updated when the curator style is adapted for a newer stable MDCS version.