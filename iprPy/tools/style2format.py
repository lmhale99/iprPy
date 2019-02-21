from . import loaded_formats

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

def style2format(pair_style):
    """
    Maps LAMMPS pair_style to one of the known formats
    """
    # Strip acceleration tags
    gputags = ['gpu', 'intel', 'kk', 'omp', 'opt']
    terms = pair_style.split('/')
    if terms[-1] in gputags:
        pair_style = '/'.join(terms[:-1])

    for potformat, styles in formatstyles.items():
        if pair_style in styles:
            return potformat
    
    raise ValueError(f'Format match for {pair_style} not found')