Updates
=======

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
