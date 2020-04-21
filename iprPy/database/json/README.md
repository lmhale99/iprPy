# local database style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

Description updated: 2019-07-26

## Introduction

The local database style stores and accesses JSON records from a local directory.

- With no active server requirements, these are trivial to set up and use but lack sophisticated, quick querying abilities.
- Using a local Database is useful for testing purposes as the records can be accessed directly through the operating system's file explorers.
- Multiple local Databases can be defined on one computer allowing for groups of calculations to be stored separately.  An example of when this is useful is to run parameter sensitivity tests without the test results being mixed in with the primary data.

### Version notes

### Additional dependencies

## Initialization arguments

- __host__: the path to the local directory to use for the database.
