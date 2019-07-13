__all__ = ['lammps_minimize']

def lammps_minimize():
    """
    Returns
    -------
    list
        The calculation input keys associated with the LAMMPS minimize command.
    """
    return  [
                'energytolerance',
                'forcetolerance',
                'maxiterations',
                'maxevaluations',
                'maxatommotion',
            ]  