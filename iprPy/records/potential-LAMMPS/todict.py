from DataModelDict import DataModelDict as DM

import numpy as np

def todict(record, full=True, flat=False):

    model = DM(record)

    pot = model['potential-LAMMPS']
    params = {}
    params['key'] =             pot['key']
    params['id'] =              pot['id']
    params['pot_key'] =         pot['potential']['key']
    params['pot_id'] =          pot['potential']['id']
    params['units'] =           pot['units']
    params['atom_style'] =      pot['atom_style']
    params['pair_style'] =      pot['pair_style']['type']
    
    params['elements'] = []
    params['masses'] = []
    params['symbols'] = []
    params['charge'] = []
    
    for atom in pot.iteraslist('atom'):
        params['elements'].append(atom.get('element', np.nan))
        params['masses'].append(atom.get('mass', np.nan))
        params['symbols'].append(atom.get('symbol', np.nan))
        params['charge'].append(atom.get('charge', np.nan))
    
    return params 