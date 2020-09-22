### Dislocation defect parameters

Defines a unique dislocation type and orientation

- __dislocation_file__: the path to a dislocation_monopole record file that contains a set of input parameters associated with a specific dislocation.
- __dislocation_slip_hkl__: three integers specifying the Miller (hkl) slip plane for the dislocation.
- __dislocation_ξ_uvw__: three integers specifying the Miller \[uvw\] line vector direction for the dislocation.  The angle between burgers and ξ_uvw determines the dislocation's character
- __dislocation_burgers__: three floating point numbers specifying the crystallographic Miller Burgers vector for the dislocation.
- __dislocation_m__ three floats for the Cartesian vector of the final system that the dislocation solution's m vector (in-plane, perpendicular to ξ) should align with.  Limited to being parallel to one of the three Cartesian axes.  
- __dislocation_n__ three floats for the Cartesian vector of the final system that the dislocation solution's n vector (slip plane normal) should align with.  Limited to being parallel to one of the three Cartesian axes.
- __dislocation_shift__: three floating point numbers specifying a rigid body shift to apply to the atoms in the system. This controls how the atomic positions align with the ideal position of the dislocation core, which is at coordinates (0,0) for the two Cartesian axes aligned with m and n.
- __dislocation_shiftscale__: boolean indicating if the *dislocation_shift* value should be absolute (False) or scaled relative to the rotated cell used to construct the system.
- __dislocation_shiftindex__: integer alternate to specifying shift values, the shiftindex allows for one of the identified suggested shift values to be used that will position the slip plane halfway between two planes of atoms.  Note that shiftindex values only shift atoms in the slip plane normal direction and may not be the ideal positions for some dislocation cores.
- __sizemults__: three integers specifying the box size multiplications to use.
- __amin__: floating point number stating the minimum width along the a direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
- __bmin__: floating point number stating the minimum width along the b direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
- __cmin__: floating point number stating the minimum width along the c direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
