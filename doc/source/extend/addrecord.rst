=======
Records
=======

The iprPy framework uses individual record files for representing reference information and calculation results.

Record directories
------------------

All records are stored in subdirectories of the iprPy/record directory, with directory named for the record, i.e. [recordname].  Each directory contains:

- **record-[record-name].xsd**: The XSD schema for the record's XML content.

- **[RecordName].py**: Includes the definition of a Python class that is a subclass of iprPy.record.Record.  This defines how the iprPy codebase interacts with the record.

- **README.md**: Descriptions of the record format and what it represents.

- **\_\_init\_\_.py**: The Python init file allowing Python to interpret the record directory as a submodule of the iprPy package.

Record format
-------------

The iprPy framework uses reference and results records that have schemas allowing for equivalent representation in JSON, XML and Python.  This supports compatibility across different software tools, such as different types of databases.  This equivalent representation does require a few format restrictions.

Many pre-defined reference records can be found in the iprPy/library/directory.

Reusable types
~~~~~~~~~~~~~~

XML and JSON were selected as their tree-like structures allow for the use of reusable types.  A reusable type can be thought of a mini-schema that describes a certain concept or object.  These small types can be put together to form larger, more complex types eventually leading to full schemas.  Constructing schemas from types is advantageous as types can be reused in multiple schemas.  This makes constructing new schemas faster and easier. It also allows for the development of more adaptable software for reading records that can search for and extract information from contained types without requiring a rigid definition of the full schema.

An example of this in the iprPy framework is that there is a type that defines an atomic configuration.  This same “atomic-system” type is present in the “crystal_prototype” reference records as well as many of the calculation results records.  The same functions can be used for interpreting and loading the “atomic-system” regardless of which record style that it came from.  Doing so makes it possible for the results records of one calculation to be used as a reference for another calculation.

Common components and design
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The schemas for all of the Record styles share some common components and design choices.

Root element
````````````

To be XML-compliant, each Record style must have exactly one root element.  For simplicity, the root element should match the calculation style, just with underscores replaced with dashes, e.g. the potential_LAMMPS Record style has root element "potential-LAMMPS".

Unique identifiers
``````````````````

The first subelement within the root element is “key”: a UUID4 unique identifier.  This gives each record a unique machine-readable name.  For non-calculation reference records, the next subelement is “id”.  The record’s id is a human-readable name which should also be unique (at least for the record style).  When a record is saved to a file or database, the record’s name corresponds to the record "id" if it has one or the record "key" if it does not making it possible to easily search for and identify matches.

System family
`````````````

A special "family" element is also used for linking calculations together based on their atomic system ancestry.  The "family" corresponds to the name of the original reference file containing atomic configuration information that was loaded in by the first calculation in a given lineage, and is passed down from one generation to the next.  Defining a "family" is useful because

- It helps identify calculations that share the same base structure.  Without the family element, classifying a calculation's system would require retracing the calculation lineage.

- It supports intelligent high-throughput calculation preparation by avoiding meaningless calculations.  For example, the dislocation_monopole calculation takes a reference structure and elastic constants, and parameters for a specific dislocation type.  It would be pointless to use the parameters for a bcc a/2<111> dislocation with an hcp reference crystal.

Record Classes
--------------

A Record class contains methods for generating, comparing and evaluating records.  The root class, from which all Record styles are subclasses of, is iprPy.record.Record.  The code containing the class is saved in the Record directory in a RecordName.py file.

Common Record properties
~~~~~~~~~~~~~~~~~~~~~~~~

- **style** is the Record's style.

- **directory** is the directory path to where the Record definition is located.

- **name** is the name assigned to the specific implementation of the Record, i.e. file name or id.

- **contentroot** is the name of the record model's root element.

- **content** is the content of the record as a DataModelDict.

- **schema** returns the path to the XSD file that defines the record style's schema.

- **compare_terms** lists the terms in the dictionary representation (see todict() below) that are to be checked for exact equivalence when determining if two records are identical.

- **compare_fterms** lists the floating point terms in the dictionary representation (see todict() below) that are to be checked for near-equivalence  when determining if two records are identical.

Common Record methods
~~~~~~~~~~~~~~~~~~~~~

- **buildcontent()** generates a calculation record's content based on input parameters (and calculation results).

- **todict()** returns a flattened dictionary representation of the record in which all key-values are at the same level as opposed to the tiered tree-like structure of the XML/JSON format.

- **isvalid()** performs a self-consistency check on the record to determine if any terms associated with input parameters are incompatible.  Returns True if the combination of input parameters is allowed, and False otherwise.

- **isnew()** compares the record in question to a database/list of records to determine if a matching record already exists.  Returns True if no match is found, and False otherwise.

- **match_df()** compares the record in question to a database/list of records and returns all matching records from the database/list.

Defining a new Record class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many of a Record style class' properties and methods are inherited from the parent class or inferred based on directory information.  For reference records, the only components that need to be overrided by the subclass are contentroot, schema, and todict().  For calculation results records, those components as well as compare_terms, compare_fterms, buildcontent(), and optionally isvalid() also need to be defined.

- **buildcontent()**: The function takes two dictionaries as parameters: one containing inputs for a calculation and one containing results for the calculation.  If the results dictionary is not given, then the record content should be for an incomplete record containing only the input information and a status element with value "not calculated".  The current records all use DataModelDict to build a Python dictionary that can be easily converted into either JSON or XML.

- **todict()**: This extracts terms from the tiered record content and returns a single-tiered dictionary of values.  How the results are represented depend on two options: full and flat.  If full is False, then only the input terms, status and error should be included in the dictionary, while Full is True will also include results terms.  If flat is True, then the values for all terms in the returned dictionary should be simple, single-valued types that can easily be displayed in a spreadsheet.  With flat being False, the values can be more complex objects that are easier to work with in Python.

- **isvalid()**: This looks at specific elements in the record content and returns False if the values of the elements are incompatible for proper/valid calculations.  The parent Record.isvalid() method always returns True, so the subclass' method only needs to be defined if prepare can build invalid calculations.

The last step is to make it so that the Record subclass can be imported by Python, which is done simply by importing the RecordName class within the __init__.py file in the calculation directory::

    from .RecordName import RecordName
    __all__ = ['RecordName']

Record format limitations
-------------------------

This section lists the format limitations to ensure that the record content is equivalently represented in JSON, XML and Python.

Limitations to XML
~~~~~~~~~~~~~~~~~~

- Elements embedded into value fields are not allowed.

  Allowed::

    <?xml version="1.0" encoding="utf-8"?>
    <root>
      <element>This is text without embded elements</element>
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
~~~~~~~~~~~~~~~~~~~

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
    
- Elements can be arrays only if they are one-dimensional, i.e. no arrays of arrays.

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- All limitations for JSON also apply to the Python representation.

- The data types of element values are limited to dict, list, tuple, unicode (str), long (int), float, bool, and None.