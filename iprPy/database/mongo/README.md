# mongo database style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

Description updated: 2019-07-26

## Introduction

The mongo database style interacts with a MongoDB database.

- Security authentication options still need to be implemented.
- Each iprPy record style corresponds to a collection in the mongo database.
- The mongo documents have two root elements "name" and "content" corresponding to the record object's name and content.  Thus, mongo queries on fields inside the records need to start with "content", e.g. "content.content-root.subroot".

### Version notes

### Additional dependencies

- A MongoDB server (local or remote) to connect to.
- [pymongo](https://api.mongodb.com/python/current/)

## Initialization arguments

- __host__: the mongo host to connect to.  Default value is 'localhost'.
- __port__: the connection port to use.  Default value is 27017.
- __database__: the name of the database inside the mongo instance.  Default value is 'iprPy'.
- __\*\*kwargs__: any extra keyword arguments needed to initialize a pymongo.MongoClient object.
