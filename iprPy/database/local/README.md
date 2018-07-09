# local Database style

## Introduction

The local Database style stores and accesses XML records from a local directory.

## Style requirements

This style has no extra requirements.

## Initialization arguments:

- __host__: the path to the local directory to use for the database.

## Additional notes:

- With no active server requirements, these are trivial to set up and use but lack sophisticated, quick querying abilities.

- Using a local Database is useful for testing purposes as the records can be accessed directly through the operating system's file explorers.

- Multiple local Databases can be defined on one computer allowing for groups of calculations to be stored separately.  An example of when this is useful is to run parameter sensitivity tests without the test results being mixed in with the primary data.