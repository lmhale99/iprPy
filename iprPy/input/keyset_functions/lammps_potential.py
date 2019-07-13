__all__ = ['lammps_potential']

def lammps_potential():
    """
    Returns
    -------
    list
        The calculation input keys associated with loading a LAMMPS-supported
        potential using atomman.lammps.Potential.
    """
    return  [
                'potential_file',
                'potential_content',
                'potential_dir',
                'potential_dir_content',
            ]   