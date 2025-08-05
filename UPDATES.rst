Updates
=======

0.11.8
------

- **relax_liquid_redo** calculation added that simplifies liquid relaxations
  by removing the mean squared displacement and evaluating the radial
  distribution function from generated dump files.

- **diffusion_liquid** calculation added that estimates the diffusion of a 
  liquid using both mean squared displacement and the velocity auto correlation
  function.

- **viscosity_driving** calculation added that estimates the viscosity of a
  liquid directly by applying a driving force.  For most purposes, it is
  recommended to use the Green-Kubo variation instead as this method is
  strongly sensitive to the size of the driving force used.

- **viscosity_green_kubo** calculation added that estimates the viscosity of a
  liquid using the Green-Kubo method.

- **melting_temperature** calculation added that estimates the melting
  temperature using a two-phase equilibrium configuration.  Polyhedral template
  matching is used to estimate the ratio of solid/liquid to verify both phases
  exist in equilibrium.

- **dislocation_dipole** calculation added that generates and relaxes small
  cell dislocation dipole configurations.  This is useful for computationally
  expensive potentials and compact (non-splitting) dislocation cores.

- **grain_boundary_grip** calculation added that uses the GRIP (grand canonical
- interface predictor) algorithm for exploring grain boundary configurations.

- **diatom_scan** calculation bug fix for when symbols are not str.

- **crystal_space_group** calculation updated for compatibility with
  newer versions of spglib.

- **dislocation_monopole** calculation updated to remove unnecessary dump
  files generated during the relaxation from being created.  Also, methods
  were added allowing for the dump files and png plots hosted on
  potentials.nist.gov for finished calculations to be downloaded. Bug fix
  for when the calculation function is called and annealsteps is not given
  a value.

- **dislocation_periodic_array** calculation updated to remove
  unnecessary dump files generated during the relaxation from being created.
  Bug fix for when the calculation function is called and annealsteps is not
  given a value.

- **energy_check** calculation is updated to include the system pressure
  in the results and to optionally save a dump file with atomic forces.

- **relax_static** calculation's master_prepare settings changed to reduce
  the total number of minimization cycles and to not throw an error if the
  max number of cycles is reached without the tolerance being achieved.

- **phonon** calculation has been updated so that it saves the band structure,
  density of states and thermo data are now saved in separate files rather
  than being included in the calculation's record.  This eliminates the
  memory issues that were associated with loading multiple phonon results.

- **stacking_fault_map_2D** calculation's minimum energy path is now better
  integrated in the calculation's class and as a method in the analysis
  submodule.

- **grain_boundary_static** method added that replaces the older
  **grain_boundary_search**.  The method has been reworked for consistency
  with the new grain_boundary_grip calculation.

- **MeltCommander** script added to bin that manages melting_temperature
  calculation runs by rerunning them with different input temperatures until
  a set number of successful/unsuccessful runs finish.

- **StackingFaultCommander** script added to bin that oversees running
  the MEP calculations on the stacking_fault_map_2D results.

- XSL and XSD files added to many of the iprPy calculations.  This supports
  uploading the results to potentials.nist.gov and rendering the results as
  HTML.

- **AtommanSystemLoad** calculation subset was updated to include extra
  terms family_url and parent_key.  The URL term allows for the public
  version of calculation records on potentials.nist.gov to point to the
  associated family structure pages.  The parent_key term standardizes how
  calculations know which previous record they are based on.

- **LammpsPotential** calculation subset was updated to include the extra
  terms potential_url and potential_LAMMPS_url.  These terms allow for the
  public version of calculation records on potential.nist.gov to point to
  the associated potential pages.

- The base **Calculation** class now makes the "script" value optional.  This
  value will be removed in future updates after it has been purged from all
  calculation records.

- **prepare** now returns a list of the prepared calculation names.  This can be
  used with a runner to target only the newest prepared calculations in the
  run_directory.  The list is also passed to fix_lammps_versions so that the
  fixes are only applied to the newest calculations.

- **prepare** also can now take a tar_dict parameter allowing for pre-loaded
  tar contents to be passed in, and for tar contents to be retained in memory
  rather than accessing them from the database every time they are needed.

- Bug fix in the buildcombos functions associated with preparing KIM potentials.

- **runner** no longer generates log files by default.  A "free" parameter has
  been added that when set to True runs through the prepared calculations without
  any database interactions.  Finished calculations can later be uploaded with
  finish_calculations.  Bug fix to ensure calculations are built correctly.

- **CijValue**, **InputValue** and **ResultValue** subclasses of
  yabadaba.Value have been added.  CijValue allows for the standard handling
  of elastic constants objects in records.  The other two Value objects are
  added to support future reworking of the Calculation classes.  If done
  correctly, these could be used to greatly reduce the amount of code in the
  Calculation class definitions improving maintenance of existing calculations
  and speeding up implementing new calculations.

- Fixes to QuickCheck for support of troublesome potentials.  A quick_check
  option was also added to the iprPy command line.

- EmperorPrepare and various other scripts added/updated in the bin folder.
  **multi_runner_slurm.py** for submitting multiple SLURM jobs simultaneously.
  **clean_bad_guys.py** for removing prepared calculations and assigning them
  error messages.  **reposition_orphans.py** to separate prepared calculations
  in one run_directory into other run_directories based on their calculation
  styles.  **add_urls_and_backup.py** fills in the URL fields of calculation
  records with the correct potentials.nist.gov sites, and copies the records
  to multiple locations as needed.  **sleep_until_done.py** tells a job to
  sleep until a run_directory is empty.  **targeted_runner.py** includes an
  example script where runners can be started that target calculations for a
  given potential rather than the default random selection.

- Alternate Emperor scripts added that combine prepare with runner job
  submission allowing for automated workflows of certain calculations.

- Automatic importing of calculations now safely checks if the
  calculation is incomplete.

- Calculation.run() now tries to save results.json up to 5 times.

- **run_calculation()** updated to infer a calculation's name from its parent
  directory if needed.  This helps ensure that the command line "iprPy run"
  calls assign the correct name/key rather than some random value.

- Many improvements to the **analysis** submodule as new calculation results
  are being prepared for release on the NIST Repository website.

- The diatom and E_vs_r_scan website plots are now generated using ploty
  instead of Bokeh.  The phonon plot generation is updated for the changes
  to the phonon calculation and to reduce the file size.

- Minor doc updates - still need a thorough revisit.

0.11.7
------

- **elastic_constants_dynamic** calculation completely reworked to use the
  deformation-fluctuation hybrid method which converges better than the old
  deformation-only way.

- **point_defect_mobility** calculation added that evaluates the point defect
  mobility energy barrier associated with point defects jumping from one stable
  position to a nearby position using nudged-elastic band (NEB) calculations.

- **grain_boundary_static** calculation added that explores and relaxes a 
  grain boundary configuration.  Calculation still in development and will
  likely result in the other grain boundary calculations being removed.

- **relax_static** now has a raise_at_maxcycles that can be set to False
  allowing calculations that reach maxcycles to finish successfully rather
  than raising an error. 

- **relax_dynamic** removed computing the stress/atom as it was unused and
  doesn't work with some of the newer ML potentials.  The master_prepare
  settings now have separate at_temp and at_temp_50K branches reflecting that
  the higher temperatures are incrementally prepared from the lower temperature
  results.

- The **free_energy** and **free_energy_liquid** calculations' master_prepare
  settings have been added. 

- Base **Calculation** updated so all calculations now have a URL field, clean(),
  clean_files() methods, and a calc_output_files list of files generated by the
  calculation.  The URL field provides a means of assigning a persistent
  identifier (PID) to a calculation's record once uploaded to a CDCS database.
  The clean_files() method deletes all files listed in calc_output_files
  allowing for the work space where a calculation was performed to be cleaned
  up.  The clean() method resets the calculation's status to 'not calculated',
  clears any error message, and deletes the calc_files if requested.

- The **clean_files** operation as described above has also been added as a
  command line option.

- Fix across multiple calculations to dump at maxiter rather than maxeval so
  that dump files are created at the end of unconverged minimizations rather
  than throwing errors.

- **QuickCheck** class added that provides a simple means of running many of
  the cheaper iprPy calculation in succession and collects the results in a 
  clear manner.  This is primarily designed to support potential development
  by allowing a set of target properties to be specified and quickly evaluated
  as an initial screening step of potential fits.

- Base **IprPyDatabase** updated with a finish_bad_calculations() method that
  finishes calculations in a run directory by setting their status to "error",
  and uploading both the record and calculation tar to the database.  This is
  largely used to clean up calculations that fail to finish in a reasonable
  amount of time.

- The **prepare** and **master_prepare** methods are updated for faster
  and more efficient operations by reducing the database access overhead.

- **runner** has been made slightly smarter when selecting a calculation to
  bid on.

- A **BaseEmperorPrepare** class has been added that adds an object-oriented
  means of defining different calculation pools for a given machine.  This
  further abstracts from master_prepare and gets one step closer to true 
  automated calculation preparation.

- Updates for newer versions of importlib.resources.

- Updates form newer versions of Bokeh for **iprPy.analysis.PropertyProcessor**.

- Bug fix related to interpreting lammps_command values with the
  **LammpsCommands** subset.

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
