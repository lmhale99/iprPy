__all__ = ['freesurface']

def freesurface():
    """
    Returns
    -------
    list
        The calculation input keys associated with a free surface defect.
    """
    return  [
                'surface_file',
                'surface_content',
                'surface_family',
                'surface_cutboxvector',
            ]