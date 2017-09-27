
Adding new library parameter records
************************************

Existing calculations can be extended to analyzing new systems and
configurations by adding pre-defined reference records to the
iprPy/library. Each style of record has its own schema, but is
designed to be straight forward and simple.  The simplest place to
start is by looking through existing records of a given style and
altering the values to form a new record.


crystal_prototype record style
==============================

Here's a descriptive template for a crystal_prototype record:

::

   {
       "crystal-prototype": {
           "key": "<UUID4 for the record>",
           "id": "<unique name for the record>",
           "name": "<full name>",
           "prototype": "<prototype element>",
           "Pearson-symbol": "<Pearson symbol>",
           "Strukturbericht": "<Strukturbericht symbol>",
           "space-group": {
               "number": "<Space group #>",
               "Hermann-Maguin": "<Hermann-Maguin space group code>",
               "Schoenflies": "<Schoenflies space group code>",
               "Wykoff": "<list of Wykoff letters and multiplicities>"
           },
           "atomic-system": {
               "cell": {
                   "<cell family>": {
                       "a": {
                           "value": 1.0,
                           "unit": "scaled"
                       },
                       "b": {
                           "value": "<b/a ratio>",
                           "unit": "scaled"
                       },
                       ...
                   }
               },
               "atom": [
                   {
                       "component": "integer atom type (unique site type)",
                       "position": {
                           "value": "<relative 3D  atomic vector position>",
                           "unit": "scaled"
                       }
                   },
                   ...
               }
           }
       }
   }


Defect record styles
====================

Other reference records define parameter sets associated with
generating crystal defects according to methods used by or defined in
the calculation scripts.  While each record style is different, they
tend to follow the same basic format:

::

   {
       <record style>: {
           "key": "<UUID4 for the record>",
           "id": "<unique name for the record>",
           "system-family": "<family (prototype) the defect is for>",
           "<additional metadata field>": "<metadata for defect>",
           ...
           "calculation-parameter": "<list(s) of defect generation parameters>"
           }
       }
   }
