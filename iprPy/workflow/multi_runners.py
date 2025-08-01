import shlex
import subprocess

cmd = 'sbatch iprPy_slurm_16 runner iprhub iprhub_8 -t'

for i in range(30):
    subprocess.run(shlex.split(cmd))
