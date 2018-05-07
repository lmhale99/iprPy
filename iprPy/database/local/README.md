# local Database style

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

The local Database style interacts with a database consisting of files and 
folders of XML records located in a local directory. This offers a simple means 
of creating a database for running high-throughput calculations, which can be 
directly accessed and analyzed, and uploaded to another (remote) database later.

## Style requirements

This style has no extra requirements

## Initialization arguments:

- __host__: the path to the local directory to use for the database.

## Additional notes:

- Using a local style is useful for testing new calculations as the files
  can be directly modified and deleted.