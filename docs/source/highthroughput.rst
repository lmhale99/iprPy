
High-Throughput Scripts
A number of scripts for running calculations in a high-throughput manner can be found in the ‘iprPy/high-throughput-scripts’ directory. This directory has subdirectories
-	‘prepare’ contains scripts that create multiple instances of different calculations
-	‘runner’ contains a script for automatically running the calculations, and other associated files.
prepare scripts
Each calculation currently has its own prepare script associated with it. Initially, one master prepare script was planned, but it ended up having too much overhead and complexity to effectively work.
All the prepare scripts are contained in subdirectories named after the calculations themselves. They can be executed by calling the script as a command with an input file as an argument. While each prepare script has its own unique combinatorial logic and input parameters, numerous utility functions are built into iprPy to allow for common feels and behaviors.
prepare input files
The input files are basic text files which define values for parameters associated with creating and running the calculations. The simple rules for the format are
1.	Each line is read separately, and divided into whitespace delimited terms.
2.	Blank lines are allowed.
3.	Comments are allowed by starting terms with #. The # term and any subsequent terms on the line are ignored. 
4.	The first term in each line is a variable name.
5.	All remaining terms are collected together as a complete value that is assigned to that variable name.
6.	If a variable name is given, then a value must also be given.
7.	Multiple lines for the same variable name are allowed, in which case the values are appended as a list.  
Here is an example:
#This is a comment line
run_directory /users/mydir/runtime

strain_range 1e-5
strain_range 1e-6

When read, only two variables will be created: 
-	run_directory = ‘/users/mydir/runtime’
-	strain_range = [‘1e-5’, ‘1e-6’]
High-Throughput Scripts, cont.
Common input file variables
While the specific variables for each prepare script are different and can be interpreted in different ways, there are a few terms that are common. 
run_directory – path to the directory where the calculations that are being prepared are placed.
lib_directory – path to the directory containing the library of calculation records.
lammps_command – path to (or command for) the particular LAMMPS executable to use. 
mpi_command – full MPI command to use for running LAMMPS on multiple processors.
length_unit – unit for length dimensions to use for input/output. Default value is angstrom.
pressure_unit  – unit for length dimensions to use for input/output. Default value is GPa.
energy_unit – unit for length dimensions to use for input/output. Default value is eV.
force_unit  – unit for length dimensions to use for input/output. Default value is eV/angstrom.

More information on the terms used by each calculation can be found with the prepare script documentation.
runner
Once calculations have been prepared, they can be executed individually or through the use of the runner.py script. All runner.py needs is an input file listing run_directory and lib_directory variables and values. Here are some features of runner:
1.	Each instance of runner picks a calculation in run_directory at random and begins to execute it if no other runner has claimed it.
2.	Automatically checks if results from another calculation are needed to perform the current calculation. If so, the runner tries to execute the required calculation first. NOTE: the current prepare scripts are NOT supporting this (yet).
3.	If a calculation fails, the error message is collected without stopping the runner. 
4.	Results or errors are collected and saved into an xml record and saved to the lib_directory record library.
5.	The simulation directory is archived as a tar.gz file and moved to the lib_directory.
6.	Multiple runners can simultaneously work on calculations in the same run_directory. They can also work on calculations in different run_directories and feed results to the same lib_directory.
7.	When submitting on a cluster queue, each runner is assigned a particular number of cores to use. Therefore, running the calculations optimally can be done by collecting the jobs into run_directories based on the number of processors used by the calculation. 