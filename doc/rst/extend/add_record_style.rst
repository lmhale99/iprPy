
Constructing Record Styles
**************************


Limitations to XML
==================

* Elements embedded into value fields are not allowed.

  Allowed:

  ::
     <?xml version="1.0" encoding="utf-8"?>
     <root>
       <element>This is text without embded elements</element>
     </root>

  Not allowed:

  ::
     <?xml version="1.0" encoding="utf-8"?>
     <root>
       <element>This is text with an <embed>embedded</embed> element.</element>
     </root>

* If an element contains multiple subelements of the same name, they
  must be consecutively placed.

  Allowed:

  ::
     <?xml version="1.0" encoding="utf-8"?>
     <root>
       <element>
         <value>1</value>
         <value>2</value>
         <unit>m</unit>
       </element>
     </root>

  Not allowed:

  ::
     <?xml version="1.0" encoding="utf-8"?>
     <root>
       <element>
         <value>1</value>
         <unit>m</unit>
         <value>2</value>
         <unit>m</unit>
       </element>
     </root>


Limitations to JSON
===================

* There can only be one root key.

  Allowed:

  ::
     {
         "root": {
             "element1": 5,
             "element2": 7
         }
     }

  Not allowed:

  ::
     {
         "root1": {
             "element1": 5,
             "element2": 7
         },
         "root2": 8
     }

* Elements can be arrays only if they are one-dimensional, i.e. no
  arrays of arrays.

  Allowed:

  ::
     {
         "root": {
             "element" = [1,2,3,4,6]
         }
     }

  Not allowed:

  ::
     {
         "root": {
             "element" = [[1,2],[3,4]]
         }
     }


Limitations to Python dictionaries
==================================

* All limitations for JSON also apply

* The data types of element values are limited to dict, list, tuple,
  unicode (str), long (int), float, bool, and None.
