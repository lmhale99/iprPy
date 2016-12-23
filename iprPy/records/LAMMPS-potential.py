from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-LAMMPS-potential.xsd')

def todict(record):

    model = DM(record)

    pot = model['LAMMPS-potential']
    params = {}
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