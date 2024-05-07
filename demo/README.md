# Calculation Demonstrations

This folder collects example demonstration input files to test run any calculation method.

## 0-files directory

The "0-files" subdirectory contains reference files to be used by the calculations.

## Calculation directories

All other subdirectories are named for the corresponding calculation and contain a single example input file.  The input files can be viewed and edited using any text editor.

The documentation for a calculation's input file parameters can be viewed from the command line using the iprPy command

    iprPy templatedoc {name}

where {name} is the calculation's name.

Each calculation can be executed from a command line by cd'ing into the appropriate directory and calling "iprPy run" on the calculation's input file

    iprPy run calc_{name}.in

**Caution**: Many of the input scripts have settings designed for a quick check that the calculation method is working properly.  This means that some settings, like sizemults and the various steps parameters for dynamic calculations, are smaller than the recommended values to obtain good results.  

If the calculation finishes successfully, a results.json file will be generated that collects calculation metadata, input values and results.  If the calculation does not finish successfully, the associated error message will be displayed.

## set_command_paths.py

The set_command_paths.py script is designed to set the lammps_command and mpi_command values across all of the calculation scripts to your machine-specific values.  Just open the set_command_paths.py script in any text editor, replace the lammps_command and mpi_command values at the top of the file with the correct ones for your machine, then run the script with

    python set_command_paths.py

Note that this script is designed to only operate within this directory and thus should not be moved or called from elsewhere!

## runall.bash

The runall.bash is a script designed to run each calculation in the demo directory one after another.  This is primarily for validating that all calculations are working properly.

If you plan on using runall yourself, be sure to use set_command_paths.py first to set the LAMMPS commands for your machine!!!  Also, note that running all calculations will likely take a few hours to finish as some calculations can be time consuming even with short non ideal settings and multiple cores. 