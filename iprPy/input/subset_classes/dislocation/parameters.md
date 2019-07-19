### Dislocation defect parameters

Defines a unique dislocation type and orientation

- __dislocation_file__: the path to a dislocation_monopole record file that contains a set of input parameters associated with a specific dislocation. In particular, the dislocation_monopole record contains values for the *a_uvw, b_uvw, c_uvw, atomshift, dislocation_stroh_m, dislocation_stroh_n, dislocation_lineboxvector,* and *dislocation_burgersvector* parameters. As such, those parameters cannot be specified separately if *pointdefect_model* is given.
- __dislocation_stroh_m__: three floating point numbers corresponding to the $m$ unit vector defining one of the two axes used by the Stroh method. $m$ must be perpendicular to the *dislocation_lineboxvector* and within the slip plane. Default value is '0 1 0'.
- __dislocation_stroh_n__: three floating point numbers corresponding to the $m$ unit vector defining one of the two axes used by the Stroh method. $n$ must be perpendicular to the *dislocation_lineboxvector* and normal to the slip plane. Default value is '0 0 1'.
- __dislocation_lineboxvector__: 'a', 'b', or 'c' specifying which of the three box vectors the dislocation line is made parallel to. Default value is 'a'.
- __dislocation_burgersvector__: three floating point numbers specifying the dislocation's Burgers vector in Crystallographic uvw units relative to the loaded system's box vectors.