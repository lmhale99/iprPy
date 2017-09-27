================
XML/JSON Records
================

The iprPy framework uses reference and results records that have schemas
allowing for equivalent representation in JSON, XML and Python.  This supports
compatibility across different software tools, such as different types of
databases.  Many pre-defined reference records can be found in the library/
directory.

Reusable types
==============

XML and JSON were selected as their tree-like structures allow for the use of
reusable types.  A reusable type can be thought of a mini-schema that
describes a certain concept or object.  These small types can be put together
to form larger, more complex types eventually leading to full schemas.
Constructing schemas from types is advantageous as types can be reused in
multiple schemas.  This makes constructing new schemas faster and easier. It
also allows for the development of more adaptable software for reading records
that can search for and extract information from contained types without
requiring a rigid definition of the full schema.

An example of this in the iprPy framework is that there is a type that defines
an atomic configuration.  This same “atomic-system” type is present in the
“crystal_prototype” reference records as well as many of the calculation
results records.  The same functions can be used for interpreting and loading
the “atomic-system” regardless of which record style that it came from.  Doing
so makes it possible for the results records of one calculation to be used as
a reference for another calculation.

Record identification and hierarchy
===================================

For records in the iprPy Framework:

- The root element’s name/key of a record corresponds to the record’s style.
  The only difference being that words are separated with “-“ in the root name
  and “_” in the the record style name.
- The first subelement within the root element is “key”: a UUID4 unique
  identifier.  This gives each record a unique machine readable name.
- For non-calculation reference records, the next subelement is “id”.  The
  record’s id is a human-readable name which is unique (at least for the
  record style).
- All calculation records (so far) do not use “id” as generating a meaningful
  unique name across all parameter variations is typically not possible or
  practical.
- When a record is saved to a file or database, the record’s name corresponds
  to the record "id" if it has one or the record "key" if it does not.

Ex.1 The A1—Cu—fcc.json crystal_prototype record::

    {
        "crystal-prototype": {
            "key": "d30980ad-ae18-425d-84cb-abf08577bdc8",
            "id": "A1--Cu--fcc", 
            ...
        }
    }
    
Ex.2 The a6b816f2-968b-4c75-8c19-6ac73e86e4a2.json calculation_system_relax
record::

    {
        "calculation-system-relax": {
            "key": "a6b816f2-968b-4c75-8c19-6ac73e86e4a2",
            ...
        }
    }

Assigning unique identifiers to each record provides a means of tracking the
hierarchy of models and calculations.  Child records can indicate any
parent records that they used as references or were derived from by
specifying the parents' "key"s (and "id"s) in subelements. Thus,
hierarchies can be mapped out by following the identifiers upstream.  Using
the concept of reusable types for the subelements, it is even possible to copy
part or all of a parent record to the child saving potential future
descendants from having to track their full lineage.

Consider the LAMMPS implementation of the 1987--Ackland-G-J--Ag interatomic
potential that is hosted by the Interatomic Potential Repository. Contained
within the 1987--Ackland-G-J--Ag--LAMMPS--ipr1.json record are keys and ids
for both the implementation and the fundamental potential model that the
implementation represents::

    {
        "potential-LAMMPS": {
            "key": "59a266da-922c-429c-8633-8d3a8de4cd70", 
            "id": "1987--Ackland-G-J--Ag--LAMMPS--ipr1", 
            "potential": {
                "key": "dc4149ce-3592-4131-8683-ecf654d5a519", 
                "id": "1987--Ackland-G-J--Ag"
            },
            ...
        }
    }
    
This is done as there may be multiple implementations based on the same
potential model.  Different implementations can be due to different formats
for different simulation codes, different interpolations, and updated 
versions.  Identifying both the implementation and the underlying model makes
it possible to track calculations from a single implementation and compare
across and validate different implementations of the same model.

Furthermore, any calculations that use this potential implementation can
indicate that they did so within their own records. Going back to the
a6b816f2-968b-4c75-8c19-6ac73e86e4a2.json record example::

    {
        "calculation-system-relax": {
            "key": "a6b816f2-968b-4c75-8c19-6ac73e86e4a2",
            ...
            "potential-LAMMPS": {
                "key": "8bfd0a48-8558-46f9-9d20-cd9e92cb83ae",
                "id": "2017--Purja-Pun-G-P--Au--LAMMPS--test",
                "potential": {
                    "key": "ef908258-25d1-439e-8223-3bf4df924ed0",
                    "id": "2017--Purja-Pun-G-P--Au"
                }
            },
            ...
        }
    }
   
System families
===============
   
A special "family" element is also used for linking calculations together
based on their atomic system ancestry.  The "family" corresponds to the name
of the original reference file containing atomic configuration information
that was loaded in by the first calculation in a given lineage, and is passed
down from one generation to the next.  Defining a "family" is useful because
otherwise it would be difficult to link the calculation of different
properties to the same base structure.

For an example, consider the calculation workflow currently used by iprPy for
performing the implemented calculations in high-throughput:

1. The cohesive energy versus interatomic spacing is evaluated for the 
   A1--Cu--fcc prototype using some potential.
2. The rough energy minima identified by #1 are used as initial guesses for
   further refinement of possible equilibrium unit cells.
3. Defect formation calculations use the refined unit cells of #2 to generate
   base systems in which the defects are inserted.
4. In-depth analysis calculations are then performed on the defect structures
   produced by #3.
   
All of the calculation records produced by this workflow will have "family" = 
"A1--Cu--fcc" making it easy to relate the calculations together.  This avoids
the effort of having to track the calculation ancestry back in order to
identify calculations on related systems.