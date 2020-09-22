### Point Defect Parameters

Defines a point defect system to construct and analyze.

- __pointdefect_file__: the path to a point_defect record file that contains a set of input parameters associated with a specific point defect or set of point defects. In particular, the point_defect record contains values for the pointdefect_type, pointdefect_atype, pointdefect_pos, pointdefect_dumbbell_vect, and pointdefect_scale parameters. As such, those parameters cannot be specified separately if pointdefect_model is given.
- __pointdefect_type__: indicates which type of point defect to generate.
  - 'v' or 'vacancy': generate a vacancy.
  - 'i' or 'interstitial': generate a position-based interstitial.
  - 's' or 'substitutional': generate a substitutional.
  - 'd', 'db' or 'dumbbell': generate a dumbbell interstitial.
- __pointdefect_atype__: indicates the integer atom type to assign to an interstitial, substitutional, or dumbbell interstitial atom.
- __pointdefect_pos__: indicates the position where the point defect is to be placed. For the interstitial type, this cannot correspond to a current atom's position. For the other styles, this must correspond to a current atom's position.
- __pointdefect_dumbbell_vect__: specifies the dumbbell vector to use for a dumbbell interstitial. The atom defined by pointdefect_pos is shifted by -pointdefect_dumbbell_vect, and the inserted interstitial atom is placed at pointdefect_pos + pointdefect_dumbbell_vect.
- __pointdefect_scale__: Boolean indicating if pointdefect_pos and pointdefect_dumbbell_vect are taken as absolute Cartesian vectors, or taken as scaled values relative to the loaded system. Default value is False.
