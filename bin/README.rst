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

prepare/master_prepare.in
-------------------------

The prepare directory contains example master prepare input scripts for
preparing calculations on different computer systems.  These scripts manage
and prepare multiple calculation styles in line with the workflow used by the
NIST Interatomic Potentials Repository.  See the
"IPR workflow/3. Workflow Manager.ipynb" Jupyter Notebook for an interactive
version of these scripts.

One thing to note is that many of the calculation pools rely on results from
earlier pools. As such, a master prepare script may need to be called multiple
times so that calculations further down the workflow can be properly prepared
as the necessary parent calculations finish.

Feel free to modify the scripts to focus only on specific potentials or to
comment out calculation pools or any styles in a pool that you do not wish to
use.

iprPy_prepare
-------------

The iprPy_prepare file is another slurm script in line with the iprPy_slurm
scripts mentioned above.  The only difference is that the full command for
calling master_prepare with one of the prepare scripts is explicitly given and
the job name is changed to "prepare".

Regularly submitting a iprPy_prepare job and keeping a number of runners active
through iprPy_slurm jobs makes the workflow nearly automated.

The iprPy_prepare_pool slurm scripts are designed to prepare one pool/round of
calculations at a time.  These tend to be more manageable for preparing across
all interatomic potentials.

check_runners.py
----------------

This is a working utility Python script that collects data from the run
directories, squeue and slurm job logs to give an overview on the status of
prepared calculations and runners.  This script was designed specifically for
one cluster running slurm and therefore there's no guarantee it will work well
on other resources.  Still, it may give insight to help others design something
similar.