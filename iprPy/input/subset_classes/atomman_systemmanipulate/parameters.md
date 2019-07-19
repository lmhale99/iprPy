### System manipulations

Performs simple manipulations on the loaded initial system.

- __a_uvw, b_uvw, c_uvw__: are crystallographic Miller vectors to rotate the system by such that the rotated system's a, b, c box vectors correspond to the specified Miller vectors of the loaded configuration.  Using crystallographic vectors for rotating ensures that if the initial configuration is periodic in all three directions, the resulting rotated configuration can be as well with no boundary incompatibilities.  Default values are '1 0 0', '0 1 0', and '0 0 1', respectively (i.e. no rotation).
- __atomshift__: a vector positional shift to apply to all atoms.  The shift is relative to the size of the system after rotating, but before sizemults have been applied.  This allows for the same relative shift regardless of box_parameters and sizemults.  Default value is '0.0 0.0 0.0' (i.e. no shift).
- __sizemults__: multiplication parameters for making a supercell of the loaded system.  This may either be a list of three or six integer numbers.  Default value is '3 3 3'.
  - ma mb mc: multipliers for each box axis.  Values can be positive or negative indicating the direction relative to the original box's origin for shifting/multiplying the system.  
  - na pa nb pb nc pc: negative, positive multiplier pairs for each box axis.  The n terms must be less than or equal to zero, and the p terms greater than or equal to zero.  This allows for expanding the system in both directions relative to the original box's origin.