iprPy bin contents
==================

**iprPy** is the command line script for the framework.  See the package
documentation for more details and a list of the options.

The **iprPy_slurm** files are example slurm submission scripts for calling the
iprPy command line.  Each one differs only in the number of processors.
Note that the SBATCH and export lines depend on the systems you are running on.

Note that with the iprPy_slurm scripts any arguments are passed to the iprPy
command line. For example:
- Start a runner on current machine: ./iprPy runner master master_1
- Submit a runner as a job: sbatch iprPy_slurm runner master master_1

**iprPy_prepare** is a slurm script that calls master_prepare.py from the IPR
Workflow directory.  While iprPy and iprPy_slurm can be used to prepare
individual calculations, the master_prepare.py script prepares multiple
calculations according to the settings used by the NIST Interatomic Potentials
Repository.  Regularly submitting this makes the workflow 'nearly' automatic.
