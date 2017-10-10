
iprPy.input package
*******************


Module contents
===============

**boolean(value)**

   Allows conversion of strings to Booleans.

   :Parameters:
      **value** (*str** or **bool*) -- If str, then 'true' and 't'
      become True and 'false' and 'f' become false. If bool, simply
      return the value.

   :Returns:
      Equivalent bool of value.

   :Return type:
      bool

   :Raises:
      ``ValueError`` -- If value is unrecognized.

**commands(input_dict, **kwargs)**

   Interprets calculation parameters associated with lammps_command
   and mpi_command input_dict keys.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'lammps_command'** the LAMMPS command to use for running
     simulations.

   * **'mpi_command'** the specific MPI command to run LAMMPS in
     parallel.

   * **'lammps_version'** the version of LAMMPS associated with
     lammps_command.

   * **'lammps_date'** a datetime.date object of the LAMMPS version.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **lammps_command** (*str*) -- Replacement parameter key name
        for 'lammps_command'.

      * **mpi_command** (*str*) -- Replacement parameter key name for
        'mpi_command'.

      * **lammps_version** (*str*) -- Replacement parameter key name
        for 'lammps_version'.

      * **lammps_date** (*str*) -- Replacement parameter key name for
        'lammps_date'.

**dislocationmonopole(input_dict, **kwargs)**

   Interprets calculation parameters associated with a
   dislocation-monopole record.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'dislocation_model'** a dislocation-monopole record to load.

   * **'dislocation_content'** alternate file or content to load
     instead of specified dislocation_model.  This is used by prepare
     functions.

   * **'x_axis', 'y_axis', 'z_axis'** the orientation axes.  This
     function only reads in values from the dislocation_model.

   * **'atomshift'** the atomic shift to apply to all atoms.  This
     function only reads in values from the dislocation_model.

   * **'dislocation_burgersvector'** the dislocation's Burgers vector
     as a crystallographic.vector.

   * **'dislocation_boundaryshape'** defines the shape of the boundary
     region.

   * **'dislocation_boundarywidth'** defines the minimum width of the
     boundary region.  This term is in units of the unit cell's a
     lattice parameter.

   * **'ucell'** the unit cell system. Used here in scaling the model
     parameters to the system being explored.

   * **'burgersvector'** the dislocation's Burgers vector as a
     Cartesian vector.

   * **'boundarywidth'** defines the minimum width of the boundary
     region. This term is in length units.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **dislocation_model** (*str*) -- Replacement parameter key
        name for 'dislocation_model'.

      * **dislocation_content** (*str*) -- Replacement parameter key
        name for 'dislocation_content'.

      * **x_axis** (*str*) -- Replacement parameter key name for
        'x_axis'.

      * **y_axis** (*str*) -- Replacement parameter key name for
        'y_axis'.

      * **z_axis** (*str*) -- Replacement parameter key name for
        'z_axis'.

      * **atomshift** (*str*) -- Replacement parameter key name for
        'atomshift'.

      * **dislocation_burgersvector** (*str*) -- Replacement parameter
        key name for 'dislocation_burgersvector'.

      * **dislocation_boundaryshape** (*str*) -- Replacement parameter
        key name for 'dislocation_boundaryshape'.

      * **dislocation_boundarywidth** (*str*) -- Replacement parameter
        key name for 'dislocation_boundarywidth'.

      * **ucell** (*str*) -- Replacement parameter key name for
        'ucell'.

      * **burgersvector** (*str*) -- Replacement parameter key name
        for 'burgersvector'.

      * **boundarywidth** (*str*) -- Replacement parameter key name
        for 'boundarywidth'.

**elasticconstants(input_dict, build=True, **kwargs)**

   Interprets calculation parameters associated with elastic
   constants.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'elasticconstants_model'** a record containing elastic
     constants to load.

   * **'elasticconstants_content'** alternate file or content to load
     instead of specified elasticconstants_model.  This is used by
     prepare functions.

   * **'C11', 'C12', ..., 'C66'** individually specified elastic
     constant terms.

   * **'C'** atomman.ElasticConstants object.

   * **'load_file'** the system load file, which is searched for
     elastic constants if neither elasticconstants_model nor Cij terms
     are specified.

   * **'load_content'** alternate file or content to load instead of
     the specified load_file.

   * **'pressure_unit'** default unit of pressure to use for reading
     in elastic constants.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **build** (*bool*) -- If False, parameters will be
        interpreted, but objects won't be built from them (Default is
        True).

      * **elasticconstants_model** (*str*) -- Replacement parameter
        key name for 'elasticconstants_model'.

      * **elasticconstants_content** (*str*) -- Replacement parameter
        key name for 'elasticconstants_content'.

      * **Ckey** (*str*) -- Replacement parameter key name for for
        identifying the C11, C12, etc. terms.

      * **load_file** (*str*) -- Replacement parameter key name for
        'load_file'.

      * **load_content** (*str*) -- Replacement parameter key name for
        'load_content'.

      * **C** (*str*) -- Replacement parameter key name for 'C'.

      * **pressure_unit** (*str*) -- Replacement parameter key name
        for 'pressure_unit'.

**freesurface(input_dict, **kwargs)**

   Interprets calculation parameters associated with a free-surface
   record.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'surface_model'** a free-surface record to load.

   * **'surface_content'** alternate file or content to load instead
     of specified surface_model. This is used by prepare functions.

   * **'x_axis, y_axis, z_axis'** the orientation axes. This function
     only reads in values from the surface_model.

   * **'atomshift'** the atomic shift to apply to all atoms. This
     function only reads in values from the surface_model.

   * **'surface_cutboxvector'** the cutboxvector parameter for the
     surface model. Default value is 'c' if neither surface_model nor
     surface_cutboxvector are given.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **surface_model** (*str*) -- Replacement parameter key name
        for 'surface_model'.

      * **surface_content** (*str*) -- Replacement parameter key name
        for 'surface_content'.

      * **x_axis** (*str*) -- Replacement parameter key name for
        'x_axis'.

      * **y_axis** (*str*) -- Replacement parameter key name for
        'y_axis'.

      * **z_axis** (*str*) -- Replacement parameter key name for
        'z_axis'.

      * **atomshift** (*str*) -- Replacement parameter key name for
        'atomshift'.

      * **surface_cutboxvector** (*str*) -- Replacement parameter key
        name for 'surface_cutboxvector'.

**minimize(input_dict, **kwargs)**

   Interprets calculation parameters associated with a LAMMPS
   minimization.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'energytolerance'** The energy tolerance for the structure
     minimization.  This value is unitless. (Default is 0.0).

   * **'forcetolerance'** The force tolerance for the structure
     minimization. This value is in units of force. (Default is 0.0).

   * **'maxiterations'** The maximum number of minimization iterations
     to use (default is 10000).

   * **'maxevaluations'** The maximum number of minimization
     evaluations to use (default is 100000).

   * **'maxatommotion'** The maximum distance in length units that any
     atom is allowed to relax in any direction during a single
     minimization iteration (default is 0.01 Angstroms).

   * **'force_unit'** The default force unit to use for reading
     forcetolerance.

   * **'length_unit'** The default length unit to use for reading
     maxatommotion.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **energytolerance** (*str*) -- Replacement parameter key name
        for 'energytolerance'.

      * **forcetolerance** (*str*) -- Replacement parameter key name
        for 'forcetolerance'.

      * **maxiterations** (*str*) -- Replacement parameter key name
        for 'maxiterations'.

      * **maxevaluations** (*str*) -- Replacement parameter key name
        for 'maxevaluations'.

      * **maxatommotion** (*str*) -- Replacement parameter key name
        for 'maxatommotion'.

      * **force_unit** (*str*) -- Replacement parameter key name for
        'force_unit'.

      * **length_unit** (*str*) -- Replacement parameter key name for
        'length_unit'.

   :Raises:
      ``ValueError`` -- If both energytolerance and forcetolerance are
      0.0.

**pointdefect(input_dict, build=True, **kwargs)**

   Interprets calculation parameters associated with a point-defect
   record.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'pointdefect_model'** a point-defect record to load.

   * **'pointdefect_content'** alternate file or content to load
     instead of specified pointdefect_model.  This is used by prepare
     functions.

   * **'pointdefect_type'** defines the point defect type to add.

   * **'pointdefect_atype'** defines the atom type for the defect
     being added.

   * **'pointdefect_pos'** position to add the defect.

   * **'pointdefect_dumbbell_vect'** vector associated with a dumbbell
     interstitial.

   * **'pointdefect_scale'** indicates if pos and vect terms are
     scaled or unscaled.

   * **'ucell'** system unit cell. Used for scaling parameters.

   * **'calculation_params'** dictionary of point defect terms as read
     in.

   * **'point_kwargs'** dictionary of processed point defect terms as
     used by the atomman.defect.point function.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **build** (*bool*) -- If False, parameters will be
        interpreted, but objects won't be built from them (Default is
        True).

      * **pointdefect_model** (*str*) -- Replacement parameter key
        name for 'pointdefect_model'.

      * **pointdefect_content** (*str*) -- Replacement parameter key
        name for 'pointdefect_content'.

      * **pointdefect_type** (*str*) -- Replacement parameter key name
        for 'pointdefect_type'.

      * **pointdefect_atype** (*str*) -- Replacement parameter key
        name for 'pointdefect_atype'.

      * **pointdefect_pos** (*str*) -- Replacement parameter key name
        for 'pointdefect_pos'.

      * **pointdefect_dumbbell_vect** (*str*) -- Replacement parameter
        key name for 'pointdefect_dumbbell_vect'.

      * **pointdefect_scale** (*str*) -- Replacement parameter key
        name for 'pointdefect_scale'.

      * **ucell** (*str*) -- Replacement parameter key name for
        'ucell'.

      * **calculation_params** (*str*) -- Replacement parameter key
        name for 'calculation_params'.

      * **point_kwargs** (*str*) -- Replacement parameter key name for
        'point_kwargs'.

**potential(input_dict, **kwargs)**

   Interprets calculation parameters associated with a
   potential-LAMMPS record.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'potential_file'** the potential-LAMMPS model to load.

   * **'potential_dir'** the directory containing all of the
     potential's artifacts.

   * **'potential_content'** alternate file or content to load instead
     of specified potential_file. This is used by prepare functions.

   * **'potential'** the atomman.lammps.Potential object created.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **potential_file** (*str*) -- Replacement parameter key name
        for 'potential_file'.

      * **potential_dir** (*str*) -- Replacement parameter key name
        for 'potential_dir'.

      * **potential** (*str*) -- Replacement parameter key name for
        'potential'.

**stackingfault1(input_dict, **kwargs)**

   Interprets calculation parameters associated with a stacking-fault
   record. This function should be called before
   iprPy.input.systemmanupulate.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'stackingfault_model'** a stacking-fault record to load.

   * **'stackingfault_content'** alternate file or content to load
     instead of specified stackingfault_model.  This is used by
     prepare functions.

   * **'x_axis, y_axis, z_axis'** the orientation axes.  This function
     only reads in values from the stackingfault_model.

   * **'atomshift'** the atomic shift to apply to all atoms.  This
     function only reads in values from the stackingfault_model.

   * **'stackingfault_cutboxvector'** the cutboxvector parameter for
     the stackingfault model.  Default value is 'c' if neither
     stackingfault_model nor stackingfault_cutboxvector are given.

   * **'stackingfault_faultpos'** the relative position within a unit
     cell where the stackingfault is to be placed.

   * **'stackingfault_shiftvector1'** one of the two fault shifting
     vectors as a crystallographic vector.

   * **'stackingfault_shiftvector2'** one of the two fault shifting
     vectors as a crystallographic vector.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **stackingfault_model** (*str*) -- Replacement parameter key
        name for 'stackingfault_model'.

      * **stackingfault_content** (*str*) -- Replacement parameter key
        name for 'stackingfault_content'.

      * **x_axis** (*str*) -- Replacement parameter key name for
        'x_axis'.

      * **y_axis** (*str*) -- Replacement parameter key name for
        'y_axis'.

      * **z_axis** (*str*) -- Replacement parameter key name for
        'z_axis'.

      * **atomshift** (*str*) -- Replacement parameter key name for
        'atomshift'.

      * **stackingfault_cutboxvector** (*str*) -- Replacement
        parameter key name for 'stackingfault_cutboxvector'.

      * **stackingfault_faultpos** (*str*) -- Replacement parameter
        key name for 'stackingfault_faultpos'.

      * **stackingfault_shiftvector1** (*str*) -- Replacement
        parameter key name for 'stackingfault_shiftvector1'.

      * **stackingfault_shiftvector2** (*str*) -- Replacement
        parameter key name for 'stackingfault_shiftvector2'.

**stackingfault2(input_dict, build=True, **kwargs)**

   Interprets calculation parameters associated with a stacking-fault
   record. This function should be called after
   iprPy.input.systemmanupulate.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'stackingfault_faultpos'** the relative position within a unit
     cell where the stackingfault is to be placed.

   * **'stackingfault_shiftvector1'** one of the two fault shifting
     vectors as a crystallographic vector.

   * **'stackingfault_shiftvector2'** one of the two fault shifting
     vectors as a crystallographic vector.

   * **'sizemults'** the system size multipliers. Only accessed here.

   * **'ucell'** the unit cell system. Only accessed here.

   * **'axes'** the 3x3 matrix of axes. Only accessed here.

   * **'faultpos'** the absolute fault position relative to the
     initial system.

   * **'shiftvector1'** one of the two fault shifting vectors as a
     Cartesian vector.

   * **'shiftvector2'** one of the two fault shifting vectors as a
     Cartesian vector.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **stackingfault_faultpos** (*str*) -- Replacement parameter
        key name for 'stackingfault_faultpos'.

      * **stackingfault_shiftvector1** (*str*) -- Replacement
        parameter key name for 'stackingfault_shiftvector1'.

      * **stackingfault_shiftvector2** (*str*) -- Replacement
        parameter key name for 'stackingfault_shiftvector2'.

      * **sizemults** (*str*) -- Replacement parameter key name for
        'sizemults'.

      * **ucell** (*str*) -- Replacement parameter key name for
        'ucell'.

      * **axes** (*str*) -- Replacement parameter key name for 'axes'.

      * **faultpos** (*str*) -- Replacement parameter key name for
        'faultpos'.

      * **shiftvector1** (*str*) -- Replacement parameter key name for
        'shiftvector1'.

      * **shiftvector2** (*str*) -- Replacement parameter key name for
        'shiftvector2'.

**systemload(input_dict, build=True, **kwargs)**

   Interprets calculation parameters associated with building a ucell
   system.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'load_file'** file to load system information from.

   * **'load_style'** file format of load_file.

   * **'load_content'** alternate file or content to load instead of
     specified load_file.  This is used by prepare functions.

   * **'load_options'** any additional options associated with loading
     the load file as an atomman.System.

   * **'symbols'** the list of atomic symbols associated with ucell's
     atom types.  Optional if this information is in
     load/load_content.

   * **'box_parameters'** the string of box parameters to scale the
     system by.  Optional if the load file already is properly scaled.

   * **'system_family'** if the load file contains a system_family
     term, then it is passed on. Otherwise, a new system_family is
     created based on the load file's name.

   * **'ucell'** this is where the resulting system is saved.

   * **'symbols'** the list of atomic symbols associated with ucell's
     atom types. This is either taken from the load file or the
     load_symbols key.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **build** (*bool*) -- If False, parameters will be
        interpreted, but objects won't be built from them (Default is
        True).

      * **load_file** (*str*) -- Replacement parameter key name for
        'load_file'.

      * **load_style** (*str*) -- Replacement parameter key name for
        'load_style'.

      * **load_options** (*str*) -- Replacement parameter key name for
        'load_options'.

      * **symbols** (*str*) -- Replacement parameter key name for
        'symbols'.

      * **box_parameters** (*str*) -- Replacement parameter key name
        for 'box_parameters'.

      * **system_family** (*str*) -- Replacement parameter key name
        for 'system_family'.

      * **ucell** (*str*) -- Replacement parameter key name for
        'ucell'.

**systemmanipulate(input_dict, build=True, **kwargs)**

   Interprets calculation parameters associated with manupulating a
   ucell system to produce an initialsystem system.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'ucell'** unmodified system to manipulate

   * **'x_axis', 'y_axis', z_axis'** three orthogonal axes vectors by
     which to rotate.

   * **'atomshift'** scaled vector to shift all atoms by.

   * **'sizemults'** 3x2 array of ints indicating how to create a
     supercell.

   * **'axes'** a 3x3 array containing all three axis terms.

   * **'initialsystem'** the resulting system after manipulation is
     saved here.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **build** (*bool*) -- If False, parameters will be
        interpreted, but objects won't be built from them (Default is
        True).

      * **ucell** (*str*) -- Replacement parameter key name for
        'ucell'.

      * **x_axis** (*str*) -- Replacement parameter key name for
        'x_axis'.

      * **y_axis** (*str*) -- Replacement parameter key name for
        'y_axis'.

      * **z_axis** (*str*) -- Replacement parameter key name for
        'z_axis'.

      * **atomshift** (*str*) -- Replacement parameter key name for
        'atomshift'.

      * **sizemults** (*str*) -- Replacement parameter key name for
        'sizemults'.

      * **axes** (*str*) -- Replacement parameter key name for 'axes'.

      * **initialsystem** (*str*) -- Replacement parameter key name
        for 'initialsystem'.

**units(input_dict, **kwargs)**

   Interprets calculation parameters associated with default units.

   The input_dict keys used by this function (which can be renamed
   using the function's keyword arguments):

   * **'length_unit'** the unit of length to use. Default is angstrom.

   * **'energy_unit'** the unit of energy to use. Default is eV.

   * **'pressure_unit'** the unit of pressure to use. Default is GPa.

   * **'force_unit'** the unit of force to use. Default is
     eV/angstrom.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **length_unit** (*str*) -- Replacement parameter key name for
        'length_unit'.

      * **energy_unit** (*str*) -- Replacement parameter key name for
        'energy_unit'.

      * **pressure_unit** (*str*) -- Replacement parameter key name
        for 'pressure_unit'.

      * **force_unit** (*str*) -- Replacement parameter key name for
        'force_unit'.

**value(input_dict, key, default_unit=None, default_term=None)**

   Interprets a calculation parameter by converting it from a string
   to a float in working units.

   The parameter being converted is a str with one of two formats: -
   '<number>' - '<number> <unit>'

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing input
        parameter key-value pairs.

      * **key** (*str*) -- The key of input_dict to evaluate.

      * **default_unit** (*str**, **optional*) -- Default unit to use
        if not specified in the parameter value.  If not given, then
        no unit conversion will be done on unitless parameter values.

      * **default_term** (*str**, **optional*) -- Default str
        parameter value to use if key not in input_dict.  Can be
        specified as '<value> <unit>' to ensure that the default value
        is always the same regardless of the working units or
        default_unit.  If not given, then key must be in input_dict.

   :Returns:
      The interpreted value of the input parameter's str value in the
      working units.

   :Return type:
      float
