============================
High-Throughput Calculations
============================

(OLD...)

A number of scripts for running calculations in a high-throughput manner can be found in the ‘iprPy/high-throughput-scripts’ directory. This directory has subdirectories
- ‘prepare’ contains scripts that create multiple instances of different calculations
- ‘runner’ contains a script for automatically running the calculations, and other associated files.
prepare scripts

Each calculation currently has its own prepare script associated with it. Initially, one master prepare script was planned, but it ended up having too much overhead and complexity to effectively work.

All the prepare scripts are contained in subdirectories named after the calculations themselves. They can be executed by calling the script as a command with an input file as an argument. While each prepare script has its own unique combinatorial logic and input parameters, numerous utility functions are built into iprPy to allow for common feels and behaviors.


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    classes
    prepare
    runner
    inline








