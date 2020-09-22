### Free Surface Defect Parameters

Defines a free surface defect system to construct and analyze.

- __surface_file__: the path to a free-surface record file that contains a set of input parameters associated with a particular free surface.
- __surface_hkl__ three integers specifying the Miller (hkl) plane which the surface will be created for.
- __surface_cellsetting__ indicates the conventional cell setting for the crystal to use for specifying *surface_hkl* if the given unit cell is primitive.  Values are 'p', 'c', 'i', 'a', 'b' and 'c'.  Default value is 'p', i.e. the hkl values will be taken as directly related to the loaded unit cell.
- __surface_cutboxvector__: specifies which of the three box vectors ('a', 'b', or 'c') is to be made non-periodic to create the free surface.  Default value is 'c'.
- __surface_shiftindex__: integer indicating which rigid body shift to apply to the system before making the cut.  This effectively controls the atomic termination planes.
- __sizemults__: three integers specifying the box size multiplications to use.
- __surface_minwidth__: floating point number stating the minimum width along the cutboxvector direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
- __surface_even__: boolean indicating if the number of replicas in the cutboxvector direction must be even.  Default value is False.
