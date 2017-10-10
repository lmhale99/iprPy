
Adding new potentials
*********************

New LAMMPS-compatible potentials can easily be integrated into the
framework. The iprPy framework makes a distinction between a potential
and a potential implementation.

* The “potential” is the code-independent mathematical interaction
  model. It is the idea of the interaction and typically associated
  with a publication.

* The “implementation” is any version of the potential designed to
  work with specific atomistic code(s). It is the actual parameters,
  extrapolation and files that are used to calculate the interaction.

Ideally, any implementation should exactly reproduce the underlying
potential model. However, this often does not occur as implementations
use numerical approximations that are easier/faster to solve.
Different atomistic codes use different interpolations, there can be
variations in the included data points, and numerical precision of the
parameters is not perfect and can vary between implementations.

Uniquely identifying each potential and implementation is important
for characterizing and understanding the predictions provided by the
interaction models. A potential can be thought of as defining one or
more virtual elements.  These virtual elements typically feature
properties and behaviors associated with real elements, but not
always.  Although multiple potentials can be associated with the same
real element(s), it is important to keep in mind that the virtual
element(s) for each potential is/are different and unique.

As for thinking about implementations, a simple analogy with
experimental chemistry is that an implementation is to a virtual
element what a sample is to a pure real element.  Every implementation
provides a representation of a virtual element, but is imperfect due
to numerical limitations. Every sample provides a representation of a
pure real element, but is imperfect due to impurities.  A high-quality
implementation/sample is one in which the imperfections are small
enough that they have a negligible effect on measured properties.


Assign Potential and Implementation keys and id’s
=================================================


Potential keys and id’s
-----------------------

Each potential is uniquely identified with both a machine-readable
hash key and a human-readable id.  The machine-readable key is a
randomly generated UUID4 key. The human-readable id is a string
generated based on the publication information associated with the
potential.

The format used a potential’s id is:

::

   YEAR--Lastname-F-M--model

where “YEAR” is the publication year, the last name and initials
correspond to the publication’s primary author, and “model” uniquely
identifies the interaction model. Typically, “model” can simply be a
list of the elemental symbols defined by the potential. For cases
where this is not enough (multiple potentials for the same element
given in the same paper or published in the same year) then the
symbols can be followed by a number or an alternate identifier used by
the authors themselves for differentiating the models.

For potentials that do not have a publication associated with them
(either unpublished or yet-to-be published), the year and name fields
can be based on the creation year and the primary creator’s name. If
an associated publication comes out later, then the potential’s id is
updated but the potential’s key is left unchanged. Keeping the key the
same allows for results to be properly tracked and catalogued.


Implementation keys and id’s
----------------------------

Each implementation of a potential is also assigned a unique key and
id.  The implementation’s key is a random UUID4, and the
implementation’s id has the format:

::

   PotentialID--Code--Version.

Here, “PotentialID” is the id for the associated potential, “Code”
indicates which atomistic code it is designed for, and “Version”
provides additional information to uniquely identify the
implementation.

Since the current iprPy only supports potential_LAMMPS
implementations, “Code” should have one of two values:

* “LAMMPS” for potentials that are natively interpreted by the LAMMPS
  software, and

* “openKIM” for potentials that are part of the openKIM framework.

As for “Version”, this is left to the discretion of users, but should
remain consistent for a given project. For instance, LAMMPS potential
implementations hosted on the Interatomic Potential Repository are
given “Version” information consisting of IPR-#, where # is a hosted
version # starting with 1 and increasing any time updates/replacement
files are provided that alter the numbers or parameters associated
with the potential.


Example id’s
------------

For an example, let’s say Bon Scott published a potential for
actinium, dysprosium and carbon in 1979. The potential’s id would be:

::

   1979--Scott-B--Ac-Dy-C

Now, there can be multiple implementations of this potential:

* An implementation created personally by Brian Johnson and not hosted
  elsewhere:

  ::
     1979--Scott-B--Ac-Dy-C--LAMMPS--Johnson-1

* An implementation hosted on the Interatomic Potential Repository:

  ::
     1979--Scott-B--Ac-Dy-C--LAMMPS--IPR-1

* An implementation in the openKIM framework, which has a short KIM ID
  of MO_123456789012_001:

  ..
     1979--Scott-B--Ac-Dy-C--openKIM--MO_123456789012_001


New Potential vs. New Implementation
------------------------------------

It can occasionally be ambiguous to determine if an update to a
potential results in a new potential or a new implementation. These
following guidelines can be used to help differentiate between the two

1. Altering or refitting empirical parameters to improve predictions
   constitutes a new potential model.

2. Published parameter corrections due to typos in the original work
   create a new implementation as the corrections reflect the authors
   original intent.

3. Changes in interpretations of a model typically coincide with a new
   implementation as they don't alter the underlying model.

4. Classifying simple modifications, such as cutoff functions and
   rounding at extremely close interatomic distances, can be
   subjective.  In these cases it comes down to determining if the
   model is still fundamentally the same for important use cases, or
   if it results in a substantial, meaningful improvement.


Creating a potential_LAMMPS record
==================================

A LAMMPS implementation of a potential can be added to the iprPy by
creating a potential_LAMMPS record for it and saving it as a JSON file
in the library/potential_LAMMPS directory.  The structure of the
record is fairly straight forward and is consistent with a common
json/xml structure.


"potential-LAMMPS"
------------------

The data model for the record has a single root element called
"potential-LAMMPS".  All other elements are subelements of this root.


"key"
-----

The first subelement of "potential-LAMMPS".  This is a UUID4 hash-key
that uniquely identifies the implementation.


"id"
----

The second subelement of "potential-LAMMPS".  This is a human-readable
id that uniquely identifies the implementation.


"potential"
-----------

The third subelement of "potential-LAMMPS".  This element identifies
the potential model that the implementation represents with the
following subelements:

* "key" is the UUID4 that uniquely identifies the potential model.

* "id" is the human-readable id that uniquely identifies the potential
  model.


"units"
-------

The fourth subelement of "potential-LAMMPS".  This specifies the
LAMMPS units option to use with the potential.


"atom_style"
------------

The fifth subelement of "potential-LAMMPS".  This specifies the LAMMPS
atom_style option to use with the potential.


"atom"
------

The sixth subelement of "potential-LAMMPS". This provides information
relating to the atomic interaction models defined by the potential.
For each atomic interaction model, the following can be defined:

* "element" is the chemical element tag associated with the atomic
  model.

* "symbol" is the unique symbol used by the potential to identify the
  atomic model.

* "mass": the atomic mass to use with all atoms of the given atomic
  model.

For most potentials, "element" and "symbol" are equivalent.  As such,
if only one of the two is given, the other is automatically assigned
the same value. Similarly, if mass is not given, then it will be
assigned the standard reference value associated with "element".
While the mass value is not required, it is recommended that it be
included for consistency, and should match what the developers used if
known.


"pair_style"
------------

The seventh subelement of "potential-LAMMPS".  This classifies the
terms that appear in the LAMMPS pair_style command associated with the
potential.  It uses the following subelements:

* "type" defines the LAMMPS pair_style option used by the
  implementation.

* "term" lists any extra terms that appear in the pair_style line.
  (See below for more information on the "term" subelement.)


"pair_coeff"
------------

The eighth subelement of "potential-LAMMPS".  This lists and
classifies the terms that appear in any LAMMPS pair_coeff commands
required by the potential. Each pair_coeff line is defined with the
following subelements:

* "interaction" specifies the atoms associated with the pair_coeff
  interaction definition.  It contains a single subelement "symbol",
  which lists all atomic model symbols associated with the
  interaction.  "interaction" is optional if all atomic interactions
  are defined with the same pair_coeff line.

* "term" lists any terms that appear in the pair_coeff line.  (See
  below for more information on the "term" subelement.)


"command"
---------

The final (optional) subelement of "potential-LAMMPS". This classifies
the terms that appear in any other LAMMPS commands required by the
implementation. It has a single subelement:

* "term" lists all terms that appear in a LAMMPS command line.  (See
  below for more information on the "term" subelement.)


"term"
------

The "term" element is used by the "pair_style", "pair_coeff", and
"command" elements.  It provides a list that characterizes the options
and parameters contained within a LAMMPS input command line.  Each
word of the command line is listed in order and characterized as one
of the following:

* "option" is a string option choice or value.

* "parameter" is a numerical parameter value.

* "file" is the path to a potential's parameter file.

* "symbols" is a Boolean indicating to show a list of the atomic
  symbols that are to be associated with the integer atom types of the
  atomic configuration.

* "symbolsList" is a Boolean indicating to show a list of all unique
  atomic symbols to associate with a particular interaction model.
  DEPRECIATED as its usage is incorrect.


Examples
========

The potential_LAMMPS data model was created to allow similar treatment
across the wide range of potential formats (i.e. pair_styles)
supported by LAMMPS. This is important as the format of the pair_style
and pair_coeff lines vary between different pair_styles.  Currently,
five distinct formats have been recognized, and examples are given
here for how to represent each using a potential_LAMMPS record.

1. Simple pair styles, e.g. lj, morse, born.

2. Original EAM style.

3. Many-body potentials, e.g. eam/alloy, tersoff, sw.

4. Many-body potentials with library files, e.g. meam.

5. hybrid and hybrid-overlay styles.

**NOTE!** The examples are not for real potentials! They are only
meant to provide a demonstration for different potential styles.


Simple pair styles
------------------

The main thing to note with the simple pair styles is that each
"pair_coeff"-"interaction" specifies exactly two "symbol" values:

::

   {
       "potential-LAMMPS": {
           "key": "7102f7ec-3612-4665-ad7e-60de508b5f37",
           "id": "lj_cut-demo--He-Ar--LAMMPS--v1",
           "potential": {
               "key": "ebf17ffa-a5e7-41c5-8e6d-8e00eb7f5068",
               "id": "lj_cut-demo--He-Ar"
           },
           "units": "lj",
           "atom_style": "atomic",
           "atom": [
               {
                   "element": "He"
               },
               {
                   "element": "Ar"
               }
           ],
           "pair_style": {
               "type": "lj/cut",
               "term": {
                   "parameter": 10.0
               }
           },
           "pair_coeff": [
               {
                   "interaction": {
                       "symbol": [
                           "He",
                           "He"
                       ]
                   },
                   "term": [
                       {
                           "parameter": 1.0
                       },
                       {
                           "parameter": 1.0
                       }
                   ]
               },
               {
                   "interaction": {
                       "symbol": [
                           "Ar",
                           "Ar"
                       ]
                   },
                   "term": [
                       {
                           "parameter": 2.0
                       },
                       {
                           "parameter": 2.0
                       }
                   ]
               },
               {
                   "interaction": {
                       "symbol": [
                           "He",
                           "Ar"
                       ]
                   },
                   "term": [
                       {
                           "parameter": 1.0
                       },
                       {
                           "parameter": 2.0
                       }
                   ]
               }
           ]
       }
   }


Original EAM style
------------------

The original EAM style can be thought of as a variation of the simple
pair styles.  The difference here is that cross-element interactions
are defined automatically by the potential and are not specified by
the pair_coeff lines:

::

   {
       "potential-LAMMPS": {
           "key": "d78cad46-a61e-439a-9676-38219e78ef1b",
           "id": "eam-demo--Ni-Cu--LAMMPS--ipr1",
           "potential": {
               "key": "776db45c-7f1d-42f8-8b85-5c8dfd2d240c",
               "id": "eam-demo--Ni-Cu"
           },
           "units": "metal",
           "atom_style": "atomic",
           "atom": [
               {
                   "element": "Cu",
                   "mass": 63.55
               },
               {
                   "element": "Ni",
                   "mass": 58.71
               }
           ],
           "pair_style": {
               "type": "eam"
           },
           "pair_coeff": [
               {
                   "interaction": {
                       "symbol": [
                           "Cu",
                           "Cu"
                       ]
                   },
                   "term": {
                       "file": "Cu.eam"
                   }
               },
               {
                   "interaction": {
                       "symbol": [
                           "Ni",
                           "Ni"
                       ]
                   },
                   "term": {
                       "file": "Ni.eam"
                   }
               }
           ]
       }
   }


Many-body potentials
--------------------

With the many-body potentials, all interactions are defined in the
same potential parameter file, which is called by a single pair_coeff
LAMMPS input command.  Because of this, the "pair_coeff"-"interaction"
is optional, but if it is given, it should list all included "symbol"
atomic models:

::

   {
       "potential-LAMMPS": {
           "key": "a45a7731-d115-4079-b6f5-aa700c5b5c56",
           "id": "EAM-alloy-demo--Ni-Al-Co--LAMMPS--v1",
           "potential": {
               "key": "820738a9-f556-468b-9041-9d98351ff751",
               "id": "EAM-alloy-demo--Ni-Al-Co"
           },
           "units": "metal",
           "atom_style": "atomic",
           "atom": [
               {
                   "element": "Ni",
                   "mass": 58.6934
               },
               {
                   "element": "Al",
                   "mass": 26.981539
               },
               {
                   "element": "Co",
                   "mass": 58.9332
               }
           ],
           "pair_style": {
               "type": "eam/alloy"
           },
           "pair_coeff": {
               "term": [
                   {
                       "file": "file.eam.alloy"
                   },
                   {
                       "symbols": "True"
                   }
               ]
           }
       }
   }


Many-body potentials with library files
---------------------------------------

Potential styles, such as MEAM, require both a library file and a
potential file.  Between the two files in the pair_coeff line is a
list of all symbols for the potential.  This first list of symbols is
constant and its order is dependent on how interactions are defined in
the potential file:

::

   {
       "potential-LAMMPS": {
           "key": "ac63aa71-808c-47e7-b80b-991a50870f35",
           "id": "MEAM-demo--Cu-Al-Fe--LAMMPS--v1",
           "potential": {
               "key": "9546264a-06b8-451a-9920-f8a17cc6917b",
               "id": "MEAM-demo--Cu-Al-Fe"
           },
           "units": "metal",
           "atom_style": "atom",
           "atom": [
               {
                   "element": "Cu",
                   "symbol": "CuX"
               },
               {
                   "element": "Al",
                   "symbol": "AlX"
               },
               {
                   "element": "Fe",
                   "symbol": "FeX"
               }
           ],
           "pair_style": {
               "type": "meam"
           },
           "pair_coeff": {
               "term": [
                   {
                       "file": "library.meam"
                   },
                   {
                       "option": "CuX AlX FeX"
                   },
                   {
                       "file": "potential.meam"
                   },
                   {
                       "symbols": true
                   }
               ]
           }
       }
   }


hybrid and hybrid/overlay styles
--------------------------------

The two hybrid styles then combine multiple other pair_styles.  Note
that the nature of the hybrid syles makes the order of the pair_coeff
values important:

::

   {
       "potential-LAMMPS": {
           "key": "7687807f-6355-4bef-bdc3-dc0dc944e106",
           "id": "hybrid-demo--Cu-H--LAMMPS--v3",
           "potential": {
               "key": "14226c15-561c-44d4-96ad-ad51304a3606",
               "id": "hybrid-demo--Cu-H"
           },
           "units": "metal",
           "atom_style": "atom",
           "atom": [
               {
                   "element": "Cu"
               },
               {
                   "element": "H"
               }
           ],
           "pair_style": {
               "type": "hybrid",
               "term": [
                   {
                       "option": "eam/alloy"
                   },
                   {
                       "option": "lj/cut"
                   },
                   {
                       "parameter": 5.0
                   }
               ]
           },
           "pair_coeff": [
               {
                   "interaction": {
                       "symbol": [
                           "Cu"
                       ]
                   },
                   "term": [
                       {
                           "option": "eam/alloy"
                       },
                       {
                           "file": "cu.eam.alloy"
                       },
                       {
                           "symbols": true
                       }
                   ]
               },
               {
                   "interaction": {
                       "symbol": [
                           "Cu",
                           "H"
                       ]
                   },
                   "term": [
                       {
                           "option": "lj/cut"
                       },
                       {
                           "parameter": 3.5
                       },
                       {
                           "parameter": 3.0
                       }
                   ]
               },
               {
                   "interaction": {
                       "symbol": [
                           "H",
                           "H"
                       ]
                   },
                   "term": [
                       {
                           "option": "lj/cut"
                       },
                       {
                           "parameter": 1.2
                       },
                       {
                           "parameter": 2.4
                       }
                   ]
               }
           ]
       }
   }
