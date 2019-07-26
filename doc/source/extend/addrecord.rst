========================
Adding new record styles
========================

The basic steps associated with implementing a new record style in iprPy are

#. Create a new subdirectory in iprPy/record named for the new record
   style.

#. Create a file that defines the Record subclass.  Name the file
   after the subclass name, typically by converting the style name to upper
   camel case (each word capitalized with no separators).

#. Define the Record subclass contentroot attribute and the todict() method.
   For record styles of calculation results, also define the compare_terms and
   compare_fterms attributes and the buildcontent() method.

#. Create an "\_\_init\_\_.py" file that imports the subclass.

#. Create an XSD schema for the record when represented in XML format.  Save
   the schema to record-[style].xsd, where any underscores in the style name
   are replaced with hyphens.

#. Write documentation for the record style in the README.md file.

Files in the record style directories
-------------------------------------

- **[Style].py**: Defines the Record subclass for the record style.
  This defines how the iprPy codebase interacts with the record.

- **\_\_init\_\_.py**: Allows Python to identify the record directory as
  a sub-package and be able to import the Record subclass into iprPy.

- **record-[style].xsd**: The XSD schema for the record's XML content.

- **README.md**: Descriptions of the record format and what it represents.

[Style].py
~~~~~~~~~~

The iprPy package interacts with the record style through the defined
Record subclass.  Considerable work has gone into making it easy to
define new subclass definitions by modifying values in pre-existing subclass
definitions.  This section describes the different components of defining a
Record subclass.

Inheritance
...........

For general records, like the reference records in the iprPy/library directory,
the class should be a child of iprPy.record.Record.

For records associated with calculations, the class should be a child of
iprPy.record.CalculationRecord.  Note that CalculationRecord is itself a child
of Record, but it contains additional components.

contentroot
...........

Defined for both Record and CalculationRecord subclasses.

The contentroot attribute is the name of the single root element of the record
style's schema.  Typically, this corresponds to the record style but with
underscores replaced with hyphens.

todict()
........

Defined for both Record and CalculationRecord subclasses.

The todict() method converts the tree-like JSON/XML content into a flat
Python dictionary.  Content common to all similar records can be interpreted
by the parent class' todict() method.  Also, any terms associated with inputs
from subsets can be generated in a common way by using the subsets' todict()
methods.

For values with units, the atomman.unitconvert.value_unit() function will
perform the proper unit conversions.  This function is the inverse operation
of the atomman.unitconvert.model() function.

The todict() method has two optional boolean parameters

- full: Primarily used by calculation records.  If True (default), dictionary
  keys associated with the calculation's results will be included.  If False,
  only the keys associated with the calculation's inputs and status will be
  included.

- flat: If True, the returned dictionary will only contain values that are
  basic Python types, like str, int, bool, and float.  If False (default),
  then the dictionary values can be more complex Python objects.  Depending on
  the values, some terms might be excluded for Flat=True.

compare_terms
.............

Defined for CalculationRecord subclasses.

The compare_terms attribute is a list of the terms in the todict()
representation of the record that are to be exactly compared to determine the
record's uniqueness.

compare_fterms
..............

Defined for CalculationRecord subclasses.

The compare_fterms attribute is a dictionary of the terms in the todict()
representation of the record that are to be approximately compared to determine
the record's uniqueness.  The keys of compare_fterms are the terms to compare,
and the corresponding values give the absolute tolerances to use.

buildcontent()
..............

Defined for CalculationRecord subclasses.

The buildcontent() method generates a record's content in the correct format
based on supplied dictionaries of input and results values.  The content is
constructed as a DataModelDict.DataModelDict object.  Content common to all
calculation records can be built by the parent class' buildcontent() method.
Also, any terms associated with inputs from subsets can be generated in a
common way by using the subsets' buildcontent() methods.

For values with units, the atomman.unitconvert.model()  function will output
elements that properly capture the value's shape and units.  This function is
the inverse operation of the atomman.unitconvert.value_unit() function.

\_\_init\_\_.py
~~~~~~~~~~~~~~~

The \_\_init\_\_.py file simply needs to tell Python to include the Database
subclass.  For instance, if the subclass is called "Style", then
\_\_init\_\_.py contains

.. code-block:: python

    from .Style import Style
    __all__ = ['Style']

record-[style].xsd
~~~~~~~~~~~~~~~~~~

The record's XSD schema is saved here.  Currently, all of the record schemas
use a generic format that allows for any terms to be given after the root
element simply because the record schemas are not finalized.  For a new style,
this generic format can be copied, and only the root element and the file name
needs to be changed.  However, a more specific record schema can be included if
available.

Record format
-------------

The iprPy framework uses reference and results records that have schemas
allowing for equivalent representation in JSON, XML and Python.  This supports
compatibility across different software tools, such as different types of
databases.  This equivalent representation does require a few format
restrictions.

XML and JSON were selected as their tree-like structures allow for the use of
reusable types.  A reusable type can be thought of a mini-schema that describes
a certain concept or object.  These small types can be put together to form
larger, more complex types eventually leading to full schemas.  Constructing
schemas from types is advantageous as types can be reused in multiple schemas.
This makes constructing new schemas faster and easier. It also allows for the
definition of the subsets that allow for common interpretation of values across
different records.

Record format limitations
~~~~~~~~~~~~~~~~~~~~~~~~~

This section lists the format limitations to ensure that the record content is
equivalently represented in JSON, XML and Python.

Limitations to XML
..................

- Elements embedded into value fields are not allowed.

  Allowed::

    <?xml version="1.0" encoding="utf-8"?>
    <root>
      <element>This is text without embedded elements</element>
    </root>

  Not allowed::

    <?xml version="1.0" encoding="utf-8"?>
    <root>
      <element>This is text with an <embed>embedded</embed> element.</element>
    </root>

- If an element contains multiple subelements of the same name, they must be
  consecutively placed.

  Allowed::

    <?xml version="1.0" encoding="utf-8"?>
    <root>
      <element>
        <value>1</value>
        <value>2</value>
        <unit>m</unit>
      </element>
    </root>

  Not allowed::

    <?xml version="1.0" encoding="utf-8"?>
    <root>
      <element>
        <value>1</value>
        <unit>m</unit>
        <value>2</value>
        <unit>m</unit>
      </element>
    </root>

- Element attributes are allowed but should be avoided whenever possible.

Limitations to JSON
...................

- There can only be one root key.

  Allowed::

    {
        "root": {
            "element1": 5,
            "element2": 7
        }
    }

  Not allowed::

    {
        "root1": {
            "element1": 5,
            "element2": 7
        },
        "root2": 8
    }

- Elements can be arrays only if they are one-dimensional, i.e. no arrays of
  arrays.

  Allowed::

    {
        "root": {
            "element" = [1,2,3,4,6]
        }
    }

  Not allowed::

    {
        "root": {
            "element" = [[1,2],[3,4]]
        }
    }

Limitations to Python dictionaries
..................................

- All limitations for JSON also apply to the Python representation.

- The data types of element values are limited to dict, list, tuple, unicode
  (str), long (int), float, bool, and None.
