### Elastic constants parameters

Specifies the computed elastic constants for the interatomic potential and crystal structure, relative to the loaded system's orientation.

- __elasticconstants_file__: the path to a record containing the elastic constants to use.  If neither this or the individual Cij components (below) are given and *load_style* is 'system_model', this will be set to *load_file*.
- __C11, C12, C13, C14, C15, C16, C22, C23, C24, C25, C26, C33, C34, C35, C36, C44, C45, C46, C55, C56, C66__: the individual elastic constants components in units of pressure.  If the loaded system's orientation is the standard setting for the crystal type, then missing values will automatically be filled in. Example: if the loaded system is a cubic prototype, then only C11, C12 and C44 need be specified.
- Isotropic moduli: the elastic constants for an isotropic material can be defined using any two of the following
    - __C_M__: P-wave modulus (units of pressure).  
    - __C_lambda__: Lame's first parameter (units of pressure).
    - __C_mu__: shear modulus (units of pressure).
    - __C_E__: Young's modulus (units of pressure).
    - __C_nu__: Poisson's ratio (unitless).
    - __C_K__: bulk modulus (units of pressure).