Updates
=======

0.11.6
------

- **relax_liquid** now has the option to restart and continue incomplete
  simulations.
- All records now have a database parameter giving them a default database to
  pull more content from, if needed.  This makes it possible to add methods
  that retrieve information if it is not directly stored in the records
  themselves.
- **iprPy retrieve** command line updated to make database specification
  optional and allow both the remote and local databases to be changed.
- More potentials now included in the old_pots list.

0.11.5
------

- **phonon** calculation: bug fixed, Notebook updated, and analysis methods
  added.
- **relax_liquid** master_prepare options added and updated to reflect how the
  IPR workflow is being performed.
- raise_error option added to calculation runs to raise any calculation error
  rather than save the error message to the results.json file.
- Records updated to reflect the changes to queries in yabadaba 0.2.0.

0.11.4
------

- **free_energy** calculation method added that evaluates the Gibbs free energy
  of a solid structure through thermodynamic integration from a Einstein solid.
- **phonon** calculation fixed and now properly performs QHA.  Default parameter
  values updated to give better results.
- **relax_dynamic** default parameter values for at_temp master prepare changed.
- Analysis tools for building **PropertyProcessor** records added to iprPy
  from previously private code.
- The **StackingFaultMap2D** calculation/record class now reads in and
  interprets results from the JSON/XML files.
- XSL transformations added for some calculations.
- Bug fix for **crystal_space_group** calculation's pandasfilter method.
- Bug fix for **E_vs_r_scan** calculation's cdcsquery method.
- Fix in **diatom_scan** calculation for potentials that don't like multiple
  atypes.
- Bug fix with running surface_energy_static and point_defect_static
  calculations, where "E_coh" is now properly updated to "E_pot".
