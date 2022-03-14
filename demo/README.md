# Calculation Demonstrations

This folder collects example demonstration input files to test run any calculation method.

The "0-files" subdirectory contains reference files to be used by the calculations.

All other subdirectories are named for the corresponding calculation and contain a single example input file.  The input files can be viewed and edited using any text editor.

The documentation for a calculation's input file parameters can be viewed from the command line using the iprPy command

    iprPy templatedoc {name}

where {name} is the calculation's name.

Each calculation can be executed from a command line by cd'ing into the appropriate directory and calling "iprPy run" on the calculation's input file

    iprPy run calc_{name}.in

If the calculation finishes successfully, a results.json file will be generated that collects calculation metadata, input values and results.  If the calculation does not finish successfully, the associated error message will be displayed.
