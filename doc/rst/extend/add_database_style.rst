
Constructing Database Styles
****************************

The Database class is meant to define common interaction methods that
work similarly for multiple types of databases.  The basic idea is
that the calculations and high-throughput tools should be able to
interact with a database whether it exists locally as a series of
directories or is a full-fledged database on an external host.

The full list of allowed Database methods can be found in the iprPy
package documentation.  Interactions are kept simple, with the ability
to add, delete, get, and modify both records and tar archives.
