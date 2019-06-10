# iprPy imports
from . import loaded_formats, failed_formats

def generate_potential_record(format=None, **kwargs):
    """
    Build potential_LAMMPS record
    """

    # Get format if not given
    if format is None:
        if 'pair_style' not in kwargs:
            raise ValueError('format and/or pair_style are required')
        format = style2format(kwargs['pair_style'])

    # Load appropriate subclass
    if format in loaded_formats:
        return loaded_formats[format](**kwargs).build()
    else:
        if format in failed_formats:
            raise ImportError('format ' + format + ' failed to load: ' + failed_formats[format])
        else:
            raise ValueError('Unknown format: ' + format)
    
def style2format(pair_style):
    """
    Maps LAMMPS pair_style to one of the known formats
    """
    # Define known format to pair_style mappings
    formatstyles = {
        'EAM': ['eam'],
        'KIM': ['kim'],
        'LIBRARY': ['meam', 'meam/c', 'snap'],
        'PARAMFILE': ['adp', 'agni', 'airebo', 'airebo/morse', 'rebo', 'bop',
                    'comb', 'comb3', 'eam/alloy', 'eam/cd', 'eam/fs', 'edip',
                    'edip/multi', 'extep', 'gw', 'gw/zbl', 'lcbop', 
                    'meam/spline', 'meam/sw/spline', 'nb3b/harmonic', 
                    'polymorphic', 'reax', 'reax/c', 'smtbq', 'sw', 'table', 
                    'table/rx', 'tersoff', 'tersoff/table', 'tersoff/mod',
                    'tersoff/mod/c', 'tersoff/zbl', 'vashishta', 
                    'vashishta/table']
        }

    # Strip acceleration tags
    gputags = ['gpu', 'intel', 'kk', 'omp', 'opt']
    terms = pair_style.split('/')
    if terms[-1] in gputags:
        pair_style = '/'.join(terms[:-1])

    for format, styles in formatstyles.items():
        if pair_style in styles:
            return format
    
    raise ValueError('Format match for ' + pair_style + ' not found')