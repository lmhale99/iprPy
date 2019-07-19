### Free Surface Defect Parameters

Defines a free surface defect system to construct and analyze.

- __surface_file__: the path to a free-surface record file that contains a set of input parameters associated with a particular free surface.  In particular, the free-surface record contains values for the a_uvw, b_uvw, c_uvw, atomshift, and surface_cutboxvector parameters.  As such, those parameters cannot be specified separately if surface_file is given.
- __surface_cutboxvector__: indicates along which box vector of the system the planar cut is made, i.e. which box direction is made non-periodic.  Allowed values are 'a', 'b', and 'c' corresponding to making the first, second and third, respectively, of the system's box directions non-periodic.  Default value is 'c'.