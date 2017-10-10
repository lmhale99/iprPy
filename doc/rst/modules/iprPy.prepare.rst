
iprPy.prepare package
*********************


Module contents
===============

**icalculations(database, record_style=None, symbol=None, family=None,
potential=None)**

   Iterates over calculation records in a database that match limiting
   conditions.

   :Parameters:
      * **database** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database being accessed.

      * **record_style** (*str*) -- The record style to access.

      * **symbol** (*str** or **list of str**, **optional*) -- Single
        string element tag or list of element tags to limit by.  Only
        calcualtions that use element models for at least one of the
        listed symbols will be included.  If not given, then no
        limiting by symbol.

      * **family** (*str** or **list of str**, **optional*) -- Single
        family name or list of family names to limit by.  Only
        calculations associated with the given system families will be
        included.  If not given, then no limiting by family.

      * **potential** (*str** or **list of str**, **optional*) --
        Single potential id or list of potential ids to limit by.
        Only calculations associated with the given potential will be
        included. If not given, then no limiting by potential.

   :Yields:
      *iprPy.Record* -- Each record from the database matching the
      limiting conditions.

**ipotentials(database, record_style='potential_LAMMPS', element=None,
name=None, pair_style=None, currentIPR=True)**

   Iterates over potential records in a database that match limiting
   conditions.

   :Parameters:
      * **database** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database being accessed.

      * **record_style** (*str**, **optional*) -- The record style to
        access (Default is 'potential_LAMMPS').

      * **element** (*str** or **list of str**, **optional*) -- Single
        string element tag or list of element tags to limit by.  Only
        potentials that have element models for at least one of the
        listed elements will be included.  If not given, then no
        limiting by element.

      * **name** (*str** or **list of str**, **optional*) -- Single
        potential id or list of potential ids to limit by.  Only
        potentials with the given potential id will be included.  If
        not given, then no limiting by name.

      * **pair_style** (*str** or **list of str**, **optional*) --
        Single LAMMPS pair_style or list of LAMMPS pair_styles to
        limit by. Only potentials with the given pair_style will be
        included.  If not given, then no limiting by pair_style.

      * **currentIPR** (*bool*) -- If True, only the current IPR
        implementations of the potentials will be included, i.e. the
        record names end with --IPR#, and # is the highest for all
        records associated with the same potential id. If False, all
        matching implementations will be included. (Default is True.)

   :Yields:
      *iprPy.Record* -- Each record from the database matching the
      limiting conditions.

**iprototypes(database, record_style='crystal_prototype',
natypes=None, name=None, spacegroup=None, crystalfamily=None,
pearson=None)**

   Iterates over crystal prototype records in a database that match
   limiting conditions.

   :Parameters:
      * **database** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database being accessed.

      * **record_style** (*str**, **optional*) -- The record style to
        access (Default is 'crystal_prototype').

      * **name** (*str** or **list of str**, **optional*) -- Single
        prototype name or list of prototype names to limit by.  Only
        prototypes with id, name, prototype, or Strukturbericht values
        matching name will be included.  If not given, then no
        limiting by name.

      * **spacegroup** (*str** or **list of str**, **optional*) --
        Single spacegroup or list of spacegroups to limit by.  Only
        prototypes with space-group number, Hermann-Maguin, or
        Schoenflies values matching spacegroup will be included.  If
        not given, then no limiting by spacegroup.

      * **crystalfamily** (*str** or **list of str**, **optional*) --
        Single crystal family name or list of crystal family names to
        limit by.  Only prototypes with the matching crystalfamily
        will be included. If not given, then no limiting by
        crystalfamily.

      * **pearson** (*str** or **list of str**, **optional*) -- Single
        Pearson symbol or list of Pearson symbols to limit by.  Only
        prototypes with Pearson-symbol terms matching pearson will be
        included.  If not given, then no limiting by pearson.

   :Yields:
      *iprPy.Record* -- Each record from the database matching the
      limiting conditions.

**isymbolscombos(prototype, potential)**

   Iterates over all possible symbol combinations associated with a
   prototype's unique (Wycoff) sites and a potential's element models.

   :Parameters:
      * **potential** (`iprPy.Record <iprPy.rst#iprPy.Record>`_) -- A
        record associated with an interatomic potential.

      * **prototype** (`iprPy.Record <iprPy.rst#iprPy.Record>`_) -- A
        record associated with a crystal prototype

   :Yields:
      *list of str* -- List of symbol tags corresponding to the
      potential's element models and the prototype's unique sites.
