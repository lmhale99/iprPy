__all__ = ['stackingfault']

def stackingfault():
    """
    Returns
    -------
    list
        The calculation input keys associated with a stacking fault defect.
    """
    return  [
                'stackingfault_file',
                'stackingfault_content',
                'stackingfault_family',
                'stackingfault_cutboxvector',
                'stackingfault_faultpos',
                'stackingfault_shiftvector1',
                'stackingfault_shiftvector2',
            ]