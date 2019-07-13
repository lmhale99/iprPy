__all__ = ['atomman_systemload']

def atomman_systemload():
    """
    Returns
    -------
    list
        The calculation input keys associated with loading an atomic
        configuration using atomman.load().
    """
    return  [
                'load_file',
                'load_content',
                'load_style',
                'family',
                'load_options',
                'symbols',
                'box_parameters',
            ]