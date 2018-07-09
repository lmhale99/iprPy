==================
buildcombos styles
==================

This file provides documentation for the various implemented buildcombos function styles/options.

atomicarchive
-------------

The atomicarchive option builds prepare input parameter value sets for loading atomic configurations using data in parent records of a given style.  In particular, this option accesses an atomic configuration file stored in the tar archive calculation folder for each matching record.

For this style to work, the parent record content must contain at least one "atomic-system" element that lists the atomic configuration's file name, format, and any atomman.load() options to properly load the file.

The interatomic potential information will also be extracted from the parent records if required by the child calculations.

Note that this option does not (currently) support preparing based on incomplete parent records.  In other words, the parent calculations must be finished before their records can be used to prepare the child calculations.

Allowed option keys:

- **record**: the parent record style.

- **load_key**: the name of the element within the parent records that contains information on the atomic configuration files to access.  Default value is "atomic-system".

- **query**: a database-style-specific query option for selecting records.

- any other keyword arguments are used to limit which records of the specified style are included.

atomicparent
------------

The atomicparent style builds prepare input parameter value sets for loading atomic configurations using data in a parent record style.  In particular, this option is for parent records that contain at least one "atomic-system" element that represents an atomic configuration using the atomman system_model format.

The interatomic potential information will also be extracted from the parent records if required by the child calculations.

Note that this option does allow for child calculations to be prepared based on incomplete parent records.  For each incomplete parent record, the children will be pointed to the first matching "atomic-system" element in the parent record.  If when the parent record is finished it has more than one matching "atomic-system" element, the prepare script would need to be executed again to prepare children for those.

Allowed option keys:

- **record**: the parent record style.

- **load_key**: the name of the element within the parent records that contains information on the atomic configuration files to access.  Default value is "atomic-system".

- **query**: a database-style-specific query option for selecting records.

- any other keyword arguments are used to limit which records of the specified style are included.


atomicreference
---------------

The atomicreference style builds prepare input parameter value sets for loading atomic configurations within a specified directory, and pairing them with compatible interatomic potentials if needed by the child calculation.  This allows for external (non-record) configurations to be used.  The configuration files should be divided into subdirectories that list the contained element model symbols in alphabetical order.  This allows for quick selection of the files based on the elements that they contain.

The atomman.load() format of the files is inferred using the file extension.

- .xml, .json -> system_model

- .dump -> atom_dump

- .dat -> atom_data

- .poscar -> poscar

- .cif -> cif

Allowed option keys:

- **lib_directory**: the path to the directory containing the reference files.

- **elements**: the name of the element within the parent records that contains information on the atomic configuration files to access.  Default value is "atomic-system".

- any other keyword arguments are used to limit which potentials and which references (by name) to include.

crystalprototype
----------------

The crystalprototype option builds prepare input parameter value sets for loading atomic configurations based on the crystal_prototype reference record style, and pairing them with compatible interatomic potentials if needed by the child calculation.  When paired with potential information, every combination of element model to unique atomic site without repeating element models will be generated.

Allowed option keys:

- **record**: the reference record style.  Default value is "crystal_prototype".

- any other keyword arguments are used to limit which records of the specified style are included.

defect
------

The defect option helps prepare calculations that rely on reference files for defining defect generation parameters.

Allowed option keys:

- **record**: the reference record style.

- **query**: a database-style-specific query option for selecting records.

- any other keyword arguments are used to limit which records of the specified style are included.

interatomicpotential
--------------------

The interatomicpotential option builds prepare input parameter value sets for loading interatomic potentials.  Typically, this option would not be called directly but is called within one of the atomic- options and the crystalprototype option.

Allowed option keys:

- **record**: the reference record style.  Default value is "potential_LAMMPS"

- **currentIPR**: indicates if only the most recent implementation versions within IPR should be used.

- **query**: a database-style-specific query option for selecting records.

- any other keyword arguments are used to limit which records of the specified style are included.

Note: to use these keys when the option is called by one of the atomic- or crystalprototype options, add "potential_" to the buildcombo key.  For example, if you define a atomicparent with buildcombo name "parent", the currentIPR value can be set to the prepare input key parent_potential_currentIPR.