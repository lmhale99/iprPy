#!/bin/bash

# This runs all calculations in demo one at a time to check that they are working.  

# Note #1: Use the set_command_paths.py script BEFORE using this to properly set
# the lammps_command and mpi_command values to your machine-specific values!!!

# Note #2: Running all calculations will take a few hours of time.  Most are quick,
# but some are time-consuming even with shortened settings and multiple cores.

for fullpath in */calc*.in
do
    dir="$(dirname "$fullpath")"
    file="$(basename ${fullpath})"
    echo $dir

    cd $dir
    iprPy run $file
    echo
    cd ..
done