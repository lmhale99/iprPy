# cdcs database style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

Description updated: 2019-12-23

## Introduction

The cdcs database style interacts with an instance of the Configurable Database Curation System (CDCS).  Records are stored in the CDCS instance as validated XML.

- With this method, a remote CDCS instance can be accessed by multiple computing resources.
- Adding records to an CDCS instance requires a valid XSD schema for each record style, and that each corresponding XML record be consistent with that schema.

### Version notes

### Additional dependencies

- Access to a working 2.X CDCS instance.
- [pycdcs](https://github.com/lmhale99/pycdcs)
  
## Initialization arguments

- __host__: the URL for accessing the CDCS instance.
- __user__: the username to use to access the CDCS instance.
- __pswd__: the corresponding password for user, or path to a file containing the password.
- __cert__: the directory path to a web certification file, if required by the CDCS instance.
