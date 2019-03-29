# curator Database style

## Introduction

The mongo Database style interacts with a MongoDB database.

## Style requirements

- A MongoDB server to connect to.

- Install pymongo (pip install works)

## Initialization arguments:

- __host__: The mongo database name or tuple of (client, database).  If client is not given, will use default localhost.

- __user__: the username to use to access the MDCS instance.

- __pswd__: the corresponding password for user, or path to a file containing the password.

## Additional notes:

- Security authentication options still need to be implemented.

- Each iprPy record style corresponds to a collection in the mongo database.  Every mongo document has the form {"name": record.name, "content": record.content}.  Thus, query fields on the record's content need to use "content.content-root.subroot", etc.