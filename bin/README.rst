iprPy bin contents
==================

iprPy
-----

iprPy is the command line script for the framework.  Installing iprPy
should copy this to a directory in the user's PATH for access, or it can be
called directly from here or copied elsewhere.

iprPy_slurm
-----------

The iprPy_slurm files are example slurm submission scripts for calling the
iprPy command line.  The number at the end denotes how many cores are being
assigned to each job.  Note that currently only runner jobs will benefit from
being assigned multiple cores as all other iprPy commands run serially.

These are only examples and are designed specifically for the cluster system
that they are being used on.  The "SBATCH" commands detail the job name, wall
limit, etc. that will need to be specifically set based on your cluster.  The
"export" command is also specific and is used here to load the version of the
library tools that the LAMMPS and MPI executables use instead of the default
library tools.

When submitting iprPy_slurm scripts any arguments are passed to the iprPy
command line. For example:
- Start a runner on current machine: ./iprPy runner master master_1
- Submit a runner as a job: sbatch iprPy_slurm runner master master_1

prepare
-------

The prepare directory contains example master prepare scripts for preparing
calculations on different computer systems, and a corresponding example slurm
job submission script.

prepare.py
``````````

The prepare.py Python scripts use the master prepare operations to prepare
multiple calculation styles in line with the workflow used by the NIST 
Interatomic Potentials Repository.  See the
"IPR workflow/3. Workflow Manager.ipynb" Jupyter Notebook for an interactive
version of these scripts and a description of what the terms mean and what the
code is doing.

One thing to note is that many of the calculation pools rely on results from
earlier pools, so these prepare scripts may need to be executed again after
calculations in a given pool finish.

Feel free to modify the scripts to focus only on specific potentials or to
comment out calculation pools or any styles in a pool that you do not wish to
use.

iprPy_prepare
`````````````
iprPy_prepare is a slurm script that submits a job for the prepare_ctcms.py
prepare script.  Regularly submitting this job script makes the workflow used
by the NIST Interatomic Potentials Repository 'nearly' automatic.
