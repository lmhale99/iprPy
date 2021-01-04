# Scripts for master_prepare.py

The master_prepare.py script provides a means of preparing all implemented iprPy calculation styles according to the workflow used by the NIST Interatomic Potentials Repository.  

The use of this script and runners makes the NIST workflow *nearly* automatic.

- Only calculations in the workflow that are ready to be run will be prepared.  If a calculation requires results from another calculation, the parent calculation will need to finish before it will be prepared.  Thus, this script will need to be called repeatedly as calculations finish.
- Runner scripts need to be called to perform the calculations in the run directories after preparing.
- The total workflow can be divided into two major parts: identifying relaxed crystals and evaluating bulk defect properties of said crystals.  Identifying new relaxed crystals requires that workflow.process.relaxed be called after crystal_space_group is performed on the results of the relax_ calculations.  Ideally, workflow.process.relaxed should be called once all relaxations are finished for the current included potentials.

## Required database and machine settings

These parameters identify the iprPy database and the primary LAMMPS and mpi commands to use when performing the calculations.

- **database_name**: The name of the set database to prepare the calculations for.
- **mpi_command**: The mpi command (executable and options) to use when calling LAMMPS with multiple processors.  Use the variable {np_per_runner} in place of the number of processors.
- **lammps_command**: The primary LAMMPS executable to use for performing the simulations.  Must be 30 Oct 2019 or newer.

## Alternate LAMMPS commands for old potential versions

These can be used with older implementations of NIST-hosted potentials that are no longer in a format compatible with current versions of LAMMPS.  Note that all of the related old implementations have been superseded by newer versions that behave (nearly) identically. Not needed if potential_status (see below) is left as active as the associated implementations will be ignored.

NOTE: The alternate LAMMPS commands are set *after* all calculations in a given run_directory pool are prepared.  Because of this, no runner should be working in that run_directory when preparing. 

- **lammps_command_snap_1**: An alternate LAMMPS executable to use with version 1 SNAP potentials.  Must be between 8 Aug 2014 and 30 May 2017. 
- **lammps_command_snap_2**: An alternate LAMMPS executable to use with version 2 SNAP potentials.  Must be between 3 Dec 2018 and 12 Jun 2019. 
- **lammps_command_old**: An alternate LAMMPS executable to use with implementations that had small issues that newer LAMMPS no longer ignores.  Must be before 30 Oct 2019.

## Alternate LAMMPS commands for specific pair styles

LAMMPS separates out the different pair_styles into modular packages that may or may not require additional libraries.  While not typical, conflicts can arise between installed packages which require building multiple versions of LAMMPS with different sets of pair_style packages.  This section allows for alternate LAMMPS commands to be defined based on pair_style.

NOTE: The alternate LAMMPS commands are set *after* all calculations in a given run_directory pool are prepared.  Because of this, no runner should be working in that run_directory when preparing. 

- **lammps_command_aenet**: An alternate LAMMPS executable to use with aenet potentials.  As of this writing, aenet exists as a user package that has not officially been integrated into LAMMPS.
- **lammps_command_kim**: An alternate LAMMPS executable to use with KIM potentials. 

## Pre-check options

These are options for testing inputs prior to preparing.

- **test_commands**: True or False indicating if the listed lammps_command executables are to be tested prior to preparing the calculations.  Will issue an error if the primary lammps_command fails or is too old, and will ignore any alternate lammps_commands if they fail or are not in the correct version range.  Must be set to False if the lammps_commands are not accessible to the computer the prepare script is running on.

## Calculation pool definitions

In the iprPy framework, runners are assigned a set number of processors that they can use, and then randomly select and perform prepared calculations from a run_directory.  The run_directories then serve as pools of calculations to be performed, with each pool containing a subset of similar calculations that all expect to be performed using the same number of processors.  Here, the calculations prepared for each run_directory pool and the expected number of processors for that pool are specified with the following parameters.

- **styles**: A space-delimited string of all calculation styles to prepare in the run_directory.
- **run_directory_name**: The name of the iprPy run_directory to use.
- **np_per_runner**: The expected number of processors that a runner operating in the run directory will have.

Multiple pools can be prepared during the same run by listing multiple lines with these values.  The only requirement is that an equal number of each line be given.

## Potential-limiting options

By default, master_prepare.py will prepare the calculations based on all currently active NIST-hosted potentials.  This can be changed by specifying input parameters starting with "potential_".  Most options can be given multiple values by listing the parameter on more than one line.

### Basic options

- **potential_style**: The name of the record style to get potentials for.  Default value is potential_LAMMPS.
- **potential_status**: The current status of the potential implementations to fetch.  Can be set to "all", "active", "superseded", and/or "retracted".  Default value is active.

### Individual potential selection options

- **potential_id**: The ids of specific potential implementations to only prepare.
- **potential_key**: The keys of specific potential implementations to only prepare.
- **potential_pot_id**: The ids of specific potentials for which the associated implementations will only be prepared.
- **potential_pot_key**: The keys of specific potentials for which the associated implementations will only be prepared.

### Other selection options

- **potential_pair_style**: The LAMMPS pair_styles for which the associated potential implementations will only be prepared.
- **potential_query**: If the database is a MongoDB, then a mongo-style query can be passed in to limit the returned records (may work or require conversion of the input).

## Other options

Any other key-values will be passed on to the different prepare functions.  For each individual calculation being prepared, the keys will be added to the underlying prepare input scripts.  This will modify default input values or how the prepare buildcombos work if the key matches something that the prepare script recognizes.  If the key is not recognized by the calculation's input script or any of the buildcombos, it should be ignored. 

## Planned improvements

These are improvements that would add useful functionality to be done in the future (hopefully soon).

- Certain keys, like "family", should be limiters that can work with most/all calculations.  These options should be integrated into each workflow.prepare function.
- Calculation-specific keys should be able to be specified by starting the key with the calculation's name.  This would allow for modifications to be made to how each calculation is being prepared while avoiding any possible parameter name conflicts.  This should be managed in master_prepare.py, but the workflow.prepare functions may need to be checked for naming conflicts.
- The pair_style-specific alternate LAMMPS commands should be handled in a more robust and scalable manner.  The current static lists of pair_style-specific ids is not sustainable in the long run.  