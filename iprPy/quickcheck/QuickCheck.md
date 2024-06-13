## 1. JSON input fields

Settings for every calculation can be specified and defined in the same way.  Fields in the JSON matching the calculation name (and sub category) collect the settings options for the corresponding calculation.  The allowed values for the calculation fields are

- A value of False indicates that the specific calculation will not be performed.
- A value of True indicates that the specific calculation should be performed with the default parameter settings.
- An object value (a.k.a. embedded dict) collects run parameters that will be passed to the corresponding calculation to override the default values.

---


<details><summary>1.1. <b>lammps_command</b></summary>

The path to the LAMMPS executable that you wish to use.

</details>

<details><summary>1.2. <b>potential</b></summary>

Collects inputs that define the metadata for the potential so that the LAMMPS commands can be properly built.  The potential content can be specified in a few alternative ways

<details><summary>1.2.1. Use a potential_LAMMPS JSON file</summary>

LAMMPS compatible potentials hosted by the NIST Interatomic Potentials use potential_LAMMPS JSON files to collect metadata on the potentials and help build the LAMMPS pair_style, pair_coeff lines.  These can be found at https://potentials.nist.gov or at https://github.com/lmhale99/potentials-library.  

To specify potentials in this way, use the following sub elements of potential

- __file__ The path/name of the potential_LAMMPS JSON file.
- __pot_dir__ The path to the directory containing any parameter files.

</details>

<details><summary>1.2.2. Use pair_style and parameters/files</summary>

The alternate method is to specify the LAMMPS pair_style and any other necessary metadata information for building the LAMMPS pair_style, pair_coeff, and mass command lines.

Note that not all pair styles are supported by this option, most notably any of the hybrid variations.

Common sub elements for all pair_styles

- __pair_style__ The LAMMPS pair_style option associated with the potential.
- __pair_style_terms__ A list of any other terms that should follow the pair_style option in the pair_style command.
- __symbols__ The list of element model tags defined by the potential.
- __elements__ The elements that correspond to symbols, if there are any.
- __masses__ The masses that correspond to symbols.  Optional if elements is given.
- __allsymbols__ Boolean flag that when True will assign at least one integer atom type to each symbol.  This is required for a few pair_styles.
- __command_terms__ A list of terms for any other LAMMPS commands beyond pair_style, pair_coeff and masses that should be called for the potential to work properly.

Sub elements for file-less pair potential styles

- __interactions__ List of dict, where each dict has 'symbols', a list of two symbol tags, and 'terms', which lists the associated pair_coeff terms for that interaction.

Single parameter file potential styles

- __paramfile__ The parameter file for the potential.

Classic eam potentials (pair_style eam)

- __paramfiles__ A list of the individual parameter files that correspond to each of the symbols.

Parameter and library file potential styles (pair_style meam)

- __libfile__ The library file for the potential.
- __paramfile__ The parameter file, if there is one, that modifies the elemental interactions.

</details>

<details><summary>1.2.3. Download a potential from the NIST repository</summary>

Potentials can be automatically accessed and downloaded from the NIST database or a personal local copy of it according to the potential's unique id.

*Not implemented yet!*

- __id__ The unique id for the LAMMPS potential implementation (ends in --LAMMPS--ipr#).
- __pot_dir_style__ Indicates where any associated parameter file(s) should be located.  'working' indicates the current working directory, 'id' indicates a subdirectory of the current working directory with id matching the name, and 'local' indicates that the files are in the local database.  If the files are not already in the corresponding location, they will be copied/dowloaded to them.
- __local_name__ The name of an alternate local database to search for matching potentials. 
- __remote_name__ The name of an alternate remote database to search for matching potentials.
- __local__ Bool indicating if the search should check the local database.
- __remote__ Bool indicating if the search should check the remote database.

</details>
<br/>

</details>


<details><summary>1.3. <b>isolated_atom</b></summary>

The isolated_atom field passes calculation settings to the isolated_atom calculation.  This evaluates the potential energy value for an atom of each symbol model when in isolation as this is necessary for relating the potential energy to the cohesive energy.  For most potentials, the isolated atom values are explicitly zero or should be zero if implemented properly.  

There are no input parameters that can be modified for this calculation.

</details>

<details><summary>1.4. <b>diatom_scan</b></summary>

The diatom_scan field passes calculation settings to the diatom_scan calculation.  This generates a configuration containing only two atoms and measures the potential energy as a function of separation distance.

Input parameters
- __symbols__: A list of two symbol sets indicating the pair interactions to explore.  If None (default) then all unique pair combinations will be calculated.
- __rmin__: The minimum r separation to use for the scan.  Default value is 2.0.
- __rmax__: The maximum r separation to use for the scan.  Default value is 6.0.
- __rsteps__: The number of r separations to evaluate.  Default value is 50.

</details>

<details><summary>1.5. <b>relax_static_diatom</b></summary>

The relax_static_diatom passes calculation settings to the relax_static calculation for relaxing a diatom configuration.  This finds the stable separation distances for the two atoms.

Input parameters
- __symbols__: A list of two symbol sets indicating the pair interactions to explore.  If None (default) then all unique pair combinations used for diatom_scan will be calculated.
- __etol__: The energy tolerance to use for the relaxation.  Default value is 0.0.
- __ftol__: The force tolerance to use for the relaxation.  Default value is 1e-8.
- __maxiter__: The maximum number of relaxation iterations to use per minimization cycle. Default value is 100000.
- __maxeval__: The maximum number of relaxation evaluations to use per minimization cycle. Default value is 1000000.
- __dmax__: The maximum distance each atom can move during a relaxation iteration.  Default value is 0.1.
- __maxcycles__: The maximum number of minimizations to perform. Default value is 20.
- __ctol__: The tolerance to use for stopping the cycles.  Default value is 1e-10.
- __raise_at_maxcycles__: If True then an error will be thrown if maxcycles is reached before ctol.  Default value is False.

</details>

<details><summary>1.6. <b>crystal</b></summary>

The crystal element provides a list of the crystal-based calculations an settings as described in Section 2.

</details>

<details><summary>1.7. <b>html_results</b></summary>

Collects the HTML results settings as described in Section 3.

</details>

## 2. Crystal-specific settings

<details><summary>2.1. <b>name</b></summary>

The name to use for identifying the crystal structure with respect to the others here.

</details>

<details><summary>2.2. <b>load_file</b></summary>

The file path/name of the crystal configuration to load.

</details>
<details><summary>2.3. <b>load_style</b></summary>

The format of the configuration file: 
- 'atom_data' for LAMMPS data files
- 'atom_dump' LAMMPS dump files
- 'poscar'
- 'cif'

</details>
<details><summary>2.4. <b>symbols</b></summary>

List of symbols to assign to each integer atom type of the crystal.  Optional if the load_style contains the symbol/element info.

</details>

<details><summary>2.5. <b>E_vs_r_scan</b></summary>

- __rmin__: 2.0
- __rmax__: 6.0
- __rsteps__: 50
- __sizemult__: 2

</details>

<details><summary>2.6. <b>relax_static</b></summary>

- __ucells__: None
- __etol__: 0.0
- __ftol__: 1e-8
- __maxiter__: 100000
- __maxeval__: 1000000
- __dmax__: 0.01
- __maxcycles__: 100
- __ctol__: 1e-10
- __raise_at_maxcycles__: False

</details>

<details><summary>2.7. <b>crystal_space_group</b></summary>

- __symprec__: 1e-5
- __to_primitive__: False
- __no_idealize__: False

</details>

<details><summary>2.8. <b>elastic_constants_static</b></summary>

- __strainrange__: 1e-6
- __etol__: 0.0
- __ftol__: 1e-8
- __maxiter__: 100000
- __maxeval__: 1000000
- __dmax__: 0.01

</details>

<details><summary>2.9. <b>phonon</b></summary>

- __distance__: 0.01
- __symprec__: 1e-5
- __strainrange__: 1e-6
- __numstrains__: 1

</details>

<details><summary>2.10. <b>point_defect_static</b></summary>

- __point_defects__:
- __sizemult__: 5
- __etol__: 0.0
- __ftol__: 1e-8
- __maxiter__: 100000
- __maxeval__: 1000000
- __dmax__: 0.01

</details>

<details><summary>2.11. <b>surface_energy_static</b></summary>

- __surfaces__:
- __minwidth__: 30
- __etol__: 0.0
- __ftol__: 1e-8
- __maxiter__: 100000
- __maxeval__: 1000000
- __dmax__: 0.01

</details>

## 3. Output settings

<details><summary>3.1. <b>filename</b></summary>

The HTML file to save the results to.

</details>

<details><summary>3.2. <b>plot_diatom_scan</b></summary>

Dict or list of dict providing the settings for generating plots from the diatom_scan results.  Each dict specified one plot and takes the terms

- __filename__ The name of the file where the plot will be saved.
- __symbols__ A list of pairs of symbols identifying which diatom_scans to include in this plot.  If not given, all scans will be plotted.
- __xlim__ Optional limiters to use on the x coordinates.
- __ylim__ Optional limiters to use on the y coordinates.

</details>

<details><summary>3.3. <b>plot_E_vs_r_scan</b></summary>

Dict or list of dict providing the settings for generating plots from the E_vs_r_scan results.  Each dict specified one plot and takes the terms

- __filename__ The name of the file where the plot will be saved.
- __crystals__ A list of crystal names indicating which scans to include in the plot.  If not given, all scans will be plotted.
- __xaxis__ Indicates which x-axis type to use: 'r' (radial distance) or 'a' (lattice parameter).
- __xlim__ Optional limiters to use on the x coordinates.
- __ylim__ Optional limiters to use on the y coordinates.

 </details>
<details><summary>3.4. <b>plot_width</b></summary>

The html width setting to use for displaying the plots.  Default value is '500px'.

</details>

<details><summary>3.5. <b>length_unit</b></summary>

Unit of length to display results in.  Default value is 'angstrom'.

</details>

<details><summary>3.6. <b>energy_unit</b></summary>

Unit of energy to display results in.  Default value is 'eV'.

</details>

<details><summary>3.7. <b>pressure_unit</b></summary>

Unit of pressure to display results in.  Default value is 'GPa'.

</details>

<details><summary>3.8. <b>energy_per_area_unit</b></summary>

Unit of energy per area to display results in.  Default value is  'mJ/m^2'.

</details>