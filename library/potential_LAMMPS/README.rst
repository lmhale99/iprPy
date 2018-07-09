==================================
potential_LAMMPS Reference Records
==================================

The potential_LAMMPS records represent an implementation of an interatomic potential that has been designed for use with the LAMMPS molecular dynamics software.  The information in the record allows for the code to dynamically generate the necessary LAMMPS input command lines for performing simulations with the potential implementation.

Note that we make a distinction between a potential and a potential implementation.

- A "potential" is the conceptual model for an atomic interaction as described by the potential's creators.

- A "potential implementation" is a representation of the potential, i.e. parameter files, computational code, publication, or a list of equations.  Multiple implementations may exist for the same potential.

Tools are being added to the iprPy/library/potential_LAMMPS directory to assist in generating new potential_LAMMPS records.

Record elements
---------------

"potential-LAMMPS" - The root element.

- "key" - A UUID4 tag assigned to the record.

- "id" - A unique human-readable name based on the potential's id and the implementation version.  The record should be saved to a json file named by this id.

- "potential" - Gives identifiers for the potential the implementation is for.

    - "key" - A UUID4 tag assigned to the potential.
    
    - "id" - A unique human-readable name based on the potential's publication or developer information.
    
- "units" - The LAMMPS units parameter option to use.

- "atom_style" - The LAMMPS atom_style parameter option to use.

- "atom" - A list of each element model included in the implementation and associated information.

    - "symbol" - The unique symbol associated with the element model.  Only needed if different than "element".
    
    - "element" - The element/isotope tag associated with the element model.
    
    - "mass" - The atomic mass to use for the element model.  Optional if element is a standard element/isotope tag.
    
- "pair_style" - Defines the LAMMPS pair_style line.

    - "type" - The pair_style type.
    
    - "term" - Specifies terms to include in the input line.  See below.
    
- "pair_coeff"- Defines each LAMMPS pair_coeff line.

    - "interaction" - Specifies the element models to include in the interaction.  Optional if only one pair_coeff line is needed.
    
        - "symbol" - A list of the element model symbols included in the interaction.
        
    - "term" - Specifies terms to include in the input line.  See below.
        
"command" - Allows any additional LAMMPS input commands that are required by the potential to be included.

    - "term" - Specifies terms to include in the input line.  See below.

The term element is used in a few different places.  It classifies any parameter terms that make up the LAMMPS input line.  Each "term" has only one subelement of the following

- "option" - Indicates an input line option.

- "parameter" - Indicates a value assigned to an input option.

- "file" - Indicates a value which is a file name.

- "symbols" - If "True" indicates that a list of symbol models should be given.  This is for some potential styles which require the symbol model for each integer atom type of a system to be specified.

- "symbolList" - This was used by earlier implementations, but shouldn't be used for new ones.

Comments on pair_coeff specific to different pair_styles
--------------------------------------------------------

The record's schema was developed to be able to handle any LAMMPS pair_style.  This section gives some extra information related to adding a record for certain pair_styles.

Pair potentials
~~~~~~~~~~~~~~~

This is for all true pair potential styles (lj, morse, born, etc) as well as the original eam style.  There needs to be a "pair_coeff" element for each distinct set of two element model interactions, with the "interaction" subelement listing the two symbols.

.. code-block:: json
    {
        ...
        pair_coeff: [
            {
                "interaction": {
                    "symbol": ["Ag", "Ag"]
                },
                "term": [
                    {
                        "option": "cutoff"
                    },
                    {
                        "parameter": "6.42"
                    },
                ]
            },
            ...
        ]
        ...
    }

File-based many-body potentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is for pair_styles that read in parameters from a single parameter file (eam/alloy, sw, tersoff, etc).  Only one "pair_coeff" element is needed, and the "interaction" subelement is optional as all atom model interactions are defined in the file.  The terms would then list the filename and symbols being True.

.. code-block:: json
    {
        ...
        pair_coeff: [
            {
                "term": [
                    {
                        "file": "Ag.eam.alloy"
                    },
                    {
                        "symbols": "True"
                    },
                ]
            },
            ...
        ]
        ...
    }

Library-based potentials
~~~~~~~~~~~~~~~~~~~~~~~~

This is for pair_styles that read in parameters from a two files: a library file and a parameter file (meam, snap, etc). Note that the option term is a specifically ordered list of atom models based on how the parameters in the second file are defined.

.. code-block:: json
    {
        ...
        pair_coeff: [
            {
                "term": [
                    {
                        "file": "lib.meam"
                    },
                    {
                        "option": "Ag Au Cu"
                    },
                    {
                        "file": "lib.param"
                    },
                    {
                        "symbols": "True"
                    },
                ]
            },
            ...
        ]
        ...
    }

hybrid and hybrid/overlay pair_styles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implementing the hybrid formats requires a few extra conditions on the record

- Order of the pair_coeff lines matter with the hybrid styles.  The pair_coeff elements need to be in the same order that the associated lines would appear in a LAMMPS input script.

- "Interaction"-"symbol"s will need to be defined for a file-based component pair_style if the file's parameters are not applied to all atomic models.

.. code-block:: json

    {
        ...
        "pair_style": {
            "type": "hybrid/overlay", 
            "term": {
                "option": "zbl 4 4.8 snap"
            }
        }, 
        "pair_coeff": [
            {
                "term": [
                    {
                        "option": "zbl"
                    }, 
                    {
                        "parameter": "73"
                    }, 
                    {
                        "parameter": "73"
                    }
                ]
            }, 
            {
                "term": [
                    {
                        "option": "snap"
                    }, 
                    {
                        "file": "Ta06A.snapcoeff"
                    }, 
                    {
                        "option": "Ta"
                    }, 
                    {
                        "file": "Ta06A.snapparam"
                    }, 
                    {
                        "symbols": "True"
                    }
                ]
            }
        ]
        ...
    }