#!/usr/bin/env python3

# Set the lammps_command path for your specific machine
lammps_command = '/home/lmh1/LAMMPS/2022-06-23/src/lmp_mpi'

# Set the mpi_command value for the more expensive LAMMPS-based calculations
mpi_command = 'mpiexec -n 12'


# List the expensive styles that will use the mpi_command
expensive_calculations = [
    'dislocation_monopole',
    'dislocation_periodic_array',
    'elastic_constants_dynamic',
    'free_energy_liquid',
    'point_defect_mobility',
    'relax_dynamic',
    'relax_liquid',
]





###############################################################################

def set_command_paths(lammps_command, mpi_command, expensive_calculations):
    """
    Sets the lammps_command and mpi_command values across all calculation
    input scripts found in the demo folder.
    """
    from pathlib import Path

    for calc_in in Path('.').glob('*/calc_*.in'):
        with open(calc_in) as f:
            lines = f.readlines()
        
        calc_name = calc_in.parent.name

        for i, line in enumerate(lines):
            if 'lammps_command' in line:
                lines[i] = f'lammps_command                  {lammps_command}\n'
            
            if 'mpi_command' in line:
                if calc_name in expensive_calculations:
                    lines[i] = f'mpi_command                     {mpi_command}\n'
                else:
                    lines[i] = f'mpi_command                     \n'

        with open(calc_in, 'w') as f:
            f.write(''.join(lines))


if __name__ == '__main__':
    set_command_paths(lammps_command, mpi_command, expensive_calculations)