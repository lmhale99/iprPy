__all__ = ['lammps_commands']

def lammps_commands():
    """
    Returns
    -------
    list
        The calculation input keys associated with the LAMMPS and MPI
        executable paths and commands.
    """
    return  [
                'lammps_command',
                'mpi_command',
            ]