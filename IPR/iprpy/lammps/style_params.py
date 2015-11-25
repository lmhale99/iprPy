#Specifies the per-atom values associated with the different LAMMPS atom_style options    
def atom_style_params(atom_style='atomic'):
    if atom_style == 'angle':
        params = ['id', 'mol', 'type', 'x', 'y', 'z']
    elif atom_style == 'atomic':
        params = ['id', 'type', 'x', 'y', 'z']
    elif atom_style == 'body':
        params = ['id', 'type', 'flag', 'mass', 'x', 'y', 'z']
    elif atom_style == 'bond':
        params = ['id', 'mol', 'type', 'x', 'y', 'z']       
    elif atom_style == 'charge':
        params = ['id', 'type', 'q', 'x', 'y', 'z']
    elif atom_style == 'dipole':
        params = ['id', 'type', 'q', 'x', 'y', 'z', 'mux', 'muy', 'muz']
    elif atom_style == 'electron':
        params = ['id', 'type', 'q', 'spin', 'eradius', 'x', 'y', 'z']
    elif atom_style == 'ellipsoid':
        params = ['id', 'type', 'flag', 'density', 'x', 'y', 'z']        
    elif atom_style == 'full':
        params = ['id', 'mol', 'type', 'q', 'x', 'y', 'z']
    elif atom_style == 'line':
        params = ['id', 'mol', 'type', 'flag', 'density', 'x', 'y', 'z']        
    elif atom_style == 'meso':
        params = ['id', 'type', 'rho', 'e', 'cv', 'x', 'y', 'z']
    elif atom_style == 'molecular':
        params = ['id', 'mol', 'type', 'x', 'y', 'z']
    elif atom_style == 'peri':
        params = ['id', 'type', 'volume', 'density', 'x', 'y', 'z']
    elif atom_style == 'smd':
        params = ['id', 'type', 'mol', 'volume', 'mass', 'kernel_radius', 'contact_radius', 'x', 'y', 'z']
    elif atom_style == 'sphere':
        params = ['id', 'type', 'diameter', 'density', 'x', 'y', 'z']
    elif atom_style == 'template':
        params = ['id', 'mol', 'template-index', 'template-atom', 'type', 'x', 'y', 'z']
    elif atom_style == 'tri':
        params = ['id', 'mol', 'type', 'flag', 'density', 'x', 'y', 'z']          
    elif atom_style == 'wavepacket':
        params = ['id', 'type', 'q', 'spin', 'eradius', 'etag', 'cs_re', 'cs_im', 'x', 'y', 'z']
    elif atom_style[:6] == 'hybrid':
        substyles = atom_style.split()
        params = ['id', 'type', 'x', 'y', 'z']
        for substyle in substyles[1:]:
            subparams = atom_style_params(atom_style=substyle)
            for subparam in subparams:
                if subparam not in ['id', 'type', 'x', 'y', 'z']:
                    params.append(subparam)
    else:
        raise ValueError('atom_style ' + atom_style + ' not supported')
    
    return params

def velocity_style_params(atom_style='atomic'):
    if atom_style == 'electron':
        params = ['id', 'vx', 'vy', 'vz', 'ervel']
    elif atom_style == 'ellipsoid':
        params = ['id', 'vx', 'vy', 'vz', 'lx', 'ly', 'lz']
    elif atom_style == 'sphere':
        params = ['id', 'vx', 'vy', 'vz', 'wx', 'wy', 'wz']
    elif atom_style[:6] == 'hybrid':
        substyles = atom_style.split()
        params = ['id', 'vx', 'vy', 'vz']
        for substyle in substyles[1:]:
            subparams = atom_style_params(atom_style=substyle)
            for subparam in subparams:
                if subparam not in ['id', 'vx', 'vy', 'vz']:
                    params.append(subparam)
    else:
        params = ['id', 'vx', 'vy', 'vz']
    
    return params