Input script parameters
-----------------------

This is a list of the input parameter names recognized by the
calculation script.

Initial system configuration to load
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides the information associated with loading an atomic
configuration.

-  **load\_file**: the path to the initial configuration file being read
   in.

-  **load\_style**: the style/format for the load\_file. The style can
   be any file type supported by atomman.load()

-  **load\_options**: a list of key-value pairs for the optional
   style-dependent arguments used by atomman.load().

-  **family**: specifies the configuration family to associate with the
   loaded file. This is typically a crystal structure/prototype
   identifier that helps with linking calculations on the same material
   together. If not given and the load\_style is system\_model, then the
   family will be taken from the file if included. Otherwise, the family
   will be taken as load\_file stripped of path and extension.

-  **symbols**: a space-delimited list of the potential's atom-model
   symbols to associate with the loaded system's atom types. Required if
   load\_file does not contain this information.

-  **box\_parameters**: allows for the specification of new box
   parameters to scale the loaded configuration by. This is useful for
   running calculations based on prototype configurations that do not
   contain material-specific dimensions. Can be given either as a list
   of three or six numbers, with an optional unit of length at the end.
   If the unit of length is not given, the specified length\_unit
   (below) will be used.

   -  a b c (unit): for orthogonal boxes.

   -  a b c alpha beta gamma (unit): for triclinic boxes. The angles are
      taken in degrees.

Units for input/output values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifies the units for various physical quantities to use when saving
values to the results record file. Also used as the default units for
parameters in this input parameter file.

-  **length\_unit**: defines the unit of length for results, and input
   parameters if not directly specified. Default value is 'angstrom'.

-  **energy\_unit**: defines the unit of energy for results, and input
   parameters if not directly specified. Default value is 'eV'.

-  **pressure\_unit**: defines the unit of pressure for results, and
   input parameters if not directly specified. Default value is 'GPa'.

-  **force\_unit**: defines the unit of pressure for results, and input
   parameters if not directly specified. Default value is 'eV/angstrom'.

Run parameters
~~~~~~~~~~~~~~

Provides parameters specific to the calculation at hand.

-  **symmetryprecision**: a precision tolerance used for the atomic
   positions and box dimensions for determining symmetry elements.
   Default value is '0.01 angstrom'.

-  **primitivecell**: a boolean flag indicating if the returned unit
   cell is to be primitive (True) or conventional (False). Default value
   is False.

-  **idealcell**: a boolean flag indicating if the box dimensions and
   atomic positions are to be idealized based on the space group (True)
   or averaged based on their actual values (False). Default value is
   True.
