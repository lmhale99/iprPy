import atomman as am
import numpy as np

try: 
    import pymatgen as pmg
    has_pmg = True
except:
    has_pmg = False
    
def ucell(object, a=None, b=None, c=None, alpha=None, beta=None, gamma=None):
    if isinstance(object, (str, unicode)):
        if object[-4:] == '.cif':
            object = am.models.Cif(object)
        elif object[-4:] == '.xml' or object[-5:] == '.json':
            object = am.models.DataModel(object)
    
    
    if isinstance(object, am.models.DataModel):
        return ucell_dm(object, a, b, c, alpha, beta, gamma)      
    
    elif isinstance(object, am.models.Cif):
        return ucell_cif(object, a, b, c, alpha, beta, gamma)
            
    elif has_pmg and isinstance(object, pmg.Structure):
        return ucell_pmg(object, a, b, c, alpha, beta, gamma)
    
    else:
        raise ValueError('Unsupported data type!')

def ucell_dm(datamodel, a=None, b=None, c=None, alpha=None, beta=None, gamma=None):
    #create dictionary of arguments
    arg_dict = {'a': a, 'b':b, 'c':c, 'alpha':alpha, 'beta':beta, 'gamma':gamma}
    
    #extract the DataModel's crystal_structure information
    crystal = datamodel.find('crystal_structure')
    assert len(crystal) == 1, 'Exactly one crystal structure must be listed in data model'
    crystal = crystal[0]
    
    #identify the crystal_system
    crystal_system = None
    for sys_type in ('cubic', 'tetragonal', 'hexagonal', 'orthorhombic', 'rhombohedral', 'monoclinic', 'trigonal', 'triclinic'):
        try:
            cell = crystal['cell'][sys_type]
            crystal_system = sys_type
            break
        except:
            pass
    assert crystal_system is not None, 'No crystal system found!'
    
    #extract default cell lengths
    default_dict = {'a': float(cell['cell_length_a']['value'])}
    if crystal_system in ('orthorhombic', 'monoclinic', 'triclinic'):
        default_dict['b'] = float(cell['cell_length_b']['value'])
        default_dict['c'] = float(cell['cell_length_c']['value'])
    elif crystal_system in ('tetragonal', 'hexagonal'):
        default_dict['c'] = float(cell['cell_length_c']['value'])
    
    #extract default cell angles
    if crystal_system in ('trigonal', 'rhomohedral'):
        default_dict['alpha'] = float(cell['cell_angle_alpha']['value'])
    elif crystal_system == 'monoclinic':
        default_dict['beta'] =  float(cell['cell_angle_beta']['value'])
    elif crystal_system == 'triclinic':
        default_dict['alpha'] = float(cell['cell_angle_alpha']['value'])
        default_dict['beta'] =  float(cell['cell_angle_beta']['value'])
        default_dict['gamma'] = float(cell['cell_angle_gamma']['value'])
    
    #make a box based on default and argument cell parameters
    box = make_box(crystal_system, default_dict, arg_dict) 
    
    #create list of atoms and list of elements
    atoms = []
    el_list = []
    atype = 1
    scale = False
    
    sites = crystal['site']
    if not isinstance(sites, (list)):
        sites = [sites]
    for site in sites:
        atype_props = {}
        symbol = None
        
        #set atom type values
        
        for k, v in site['constituent'].iteritems():
            if k == 'component':
                assert atype == int(v), 'atomic component must be in order'
            elif k == 'symbol':
                symbol = v
            elif k == 'element':
                if symbol is not None:
                    symbol = v
            else:
                atype_props[k] = v
        el_list.append(symbol)
        
        #set per-atom values
        if not isinstance(site['equivalent_position'], list):
            site['equivalent_position'] = [site['equivalent_position']]
        for atom_pos in site['equivalent_position']:
            atom = am.Atom(atype=atype)
            for k, v in atom_pos.iteritems():
                if k == 'coordinates':
                    atom.pos(np_convert(v['value']))
                    if scale is False and v['unit'] == 'scaled':
                        scale = True
                else:
                    atom.prop(k, np_convert(v['value']))
            for k, v in atype_props.iteritems():
                atom.prop(k, np_convert(v['value']))
            atoms.append(atom)
        
        atype += 1
        
    system = am.System(box=box, atoms=atoms, scale=scale)
    
    return system, el_list
        
def ucell_cif(cif, a=None, b=None, c=None, alpha=None, beta=None, gamma=None):
    arg_dict = {'a': a, 'b':b, 'c':c, 'alpha':alpha, 'beta':beta, 'gamma':gamma}

    d_cell = cif.ucell()
    default_dict = {'a':    d_cell.box('a'), 
                    'b':    d_cell.box('b'),
                    'c':    d_cell.box('c'),
                    'alpha':d_cell.box('alpha'),
                    'beta': d_cell.box('beta'), 
                    'gamma':d_cell.box('gamma')}
    print default_dict
    
    #identify the crystal system
    crystal_system = get_crystal_system(default_dict)       
    
    box = make_box(crystal_system, default_dict, arg_dict)

    el_names = cif.element_list()
    
    system = am.System(box=box, atoms=d_cell.atoms(scale=True), scale=True)        
    
    return system, el_names

def ucell_pmg(struct, a=None, b=None, c=None, alpha=None, beta=None, gamma=None):
    arg_dict = {'a': a, 'b':b, 'c':c, 'alpha':alpha, 'beta':beta, 'gamma':gamma}

    default_dict = {'a':    struct.lattice.a, 
                    'b':    struct.lattice.b, 
                    'c':    struct.lattice.c,
                    'alpha':struct.lattice.alpha, 
                    'beta': struct.lattice.beta, 
                    'gamma':struct.lattice.gamma}
    
    #identify the crystal system
    crystal_system = get_crystal_system(default_dict)
    
    box = make_box(crystal_system, default_dict, arg_dict)

    system = am.System(box=box, natoms=struct.num_sites)
    all_elements = struct.species

    elements = []
    el_names = []
    for element in all_elements:
        if element not in elements:
            elements.append(element)
            el_names.append(str(element))

    for i in xrange(struct.num_sites):
        atype = elements.index(all_elements[i]) + 1
        system.atoms(i, 'atype', atype)
        system.atoms(i, 'pos', struct.sites[i].frac_coords, scale=True)
        for k, v in struct.sites[i].properties.iteritems():
            try:
                system.atoms(i, k, v)
            except:
                pass
    
    return system, el_names

def np_convert(value):
    np_array = np.array(value)
    if np_array.dtype == int or np_array.dtype == float:
        pass
    else:
        try:
            np_array = np.array(value, dtype=int)
        except:
            np_array = np.array(value, dtype=float)
    return np_array    
    
def get_crystal_system(params):
    if np.isclose(params['a'], params['b']):
        if np.isclose(params['a'], params['c']):
            assert np.isclose(params['alpha'], params['beta']) and np.isclose(params['alpha'], params['gamma']), 'Non-standard crystal system'
            if np.isclose(params['alpha'], 90.0):
                crystal_system = 'cubic'
            else:
                crystal_system = 'trigonal'
        else:
            assert np.isclose(params['alpha'], 90.0) and np.isclose(params['beta'], 90.0), 'Non-standard crystal system'
            if np.isclose(params['gamma'], 90.0):
                crystal_system = 'tetragonal'
            elif np.isclose(params['gamma'], 120.0):
                crystal_system = 'hexagonal'
            else:
                assert False,  'Non-standard crystal system'
    else:
        if np.isclose(params['alpha'], 90.0) and np.isclose(params['gamma'], 90.0):
            if np.isclose(params['beta'], 90.0):
                crystal_system = 'orthorhombic'
            else:
                crystal_system = 'monoclinic'
        else:
            crystal_system = 'triclinic'
    return crystal_system     
    
def make_box(crystal_system, default, arg):
    if crystal_system == 'cubic':
        if arg['a'] is None:
            assert arg['b'] is None and arg['c'] is None, 'define lattice parameters in order'                    
            a = b = c = default['a']
        else:
            assert (arg['a'] == arg['b'] or arg['b'] is None) and (arg['a'] == arg['c'] or arg['c'] is None), 'cubic lengths must match'
            a = b = c = arg['a']
            
        assert arg['alpha'] is None or arg['alpha'] == 90.0, 'cubic angles must be 90'
        assert arg['beta']  is None or arg['beta']  == 90.0, 'cubic angles must be 90'
        assert arg['gamma'] is None or arg['gamma'] == 90.0, 'cubic angles must be 90'
        alpha = beta = gamma = 90.0
            
    elif crystal_system == 'tetragonal':
        if arg['a'] is None:
            assert arg['b'] is None, 'define lattice parameters in order'
            a = b = default['a']
        else:
            assert arg['b'] is None or arg['a'] == arg['b'], 'tetragonal lengths a and b must match'
            a = b = arg['a']
        if arg['c'] is None:
            c = default['c'] * a / default['a']
        else:
            c = arg['c']    
            
        assert arg['alpha'] is None or arg['alpha'] == 90.0, 'tetragonal angles must be 90'
        assert arg['beta']  is None or arg['beta']  == 90.0, 'tetragonal angles must be 90'
        assert arg['gamma'] is None or arg['gamma'] == 90.0, 'tetragonal angles must be 90'
        alpha = beta = gamma = 90.0
        
    elif crystal_system == 'hexagonal':
        if arg['a'] is None:
            assert arg['b'] is None, 'define lattice parameters in order'
            a = b = default['a']
        else:
            assert arg['b'] is None or arg['a'] == arg['b'], 'hexagonal lengths a and b must match'
            a = b = arg['a']
        if arg['c'] is None:
            c = default['c'] * a / default['a']
        else:
            c = arg['c']  
            
        assert arg['alpha'] is None or arg['alpha'] == 90.0, 'hexagonal angles must be 90'
        assert arg['beta']  is None or arg['beta']  == 90.0, 'hexagonal angles must be 90'
        assert arg['gamma'] is None or arg['gamma'] == 120.0,'hexagonal angles must be 90'
        alpha = beta = 90.0
        gamma = 120.0
    
    elif crystal_system == 'orthorhombic':
        if arg['a'] is None:
            a = default['a']
        else:
            a = arg['a']
        if arg['b'] is None:
            b = default['b'] * a / default['a']
        else:
            b = arg['b']     
        if arg['c'] is None:
            c = default['c'] * a / default['a']
        else:
            c = arg['c'] 
        
        assert arg['alpha'] is None or arg['alpha'] == 90.0, 'orthorhombic angles must be 90'
        assert arg['beta']  is None or arg['beta']  == 90.0, 'orthorhombic angles must be 90'
        assert arg['gamma'] is None or arg['gamma'] == 90.0, 'orthorhombic angles must be 90'
        alpha = beta = gamma = 90.0
    
    elif crystal_system == 'rhombohedral' or crystal_system == 'trigonal':
        if arg['a'] is None:
            assert arg['b'] is None and arg['c'] is None, 'define lattice parameters in order'                    
            a = b = c = default['a']
        else:
            assert (arg['a'] == arg['b'] or arg['b'] is None) and (arg['a'] == arg['c'] or arg['c'] is None), 'rhombohedral lengths must match'
            a = b = c = arg['a']
        
        if arg['alpha'] is None:
            assert arg['beta'] is None and arg['gamma'] is None, 'define lattice angles in order'                    
            alpha = beta = gamma = default['alpha']
        else:
            assert (arg['alpha'] == arg['beta'] or arg['beta'] is None) and (arg['alpha'] == arg['gamma'] or arg['gamma'] is None), 'rhombohedral angles must match'
            alpha = beta = gamma = arg['alpha']
        assert alpha < 120, 'Non-standard rhombohedral angle'
    
    elif crystal_system == 'monoclinic':
        if arg['a'] is None:
            a = default['a']
        else:
            a = arg['a']
        if arg['b'] is None:
            b = default['b'] * a / default['a']
        else:
            b = arg['b']     
        if arg['c'] is None:
            c = default['c'] * a / default['a']
        else:
            c = arg['c'] 
        
        assert arg['alpha'] is None or arg['alpha'] == 90.0, 'orthorhombic angles must be 90'
        assert arg['gamma'] is None or arg['gamma'] == 90.0, 'orthorhombic angles must be 90'
        alpha = gamma = 90.0
        if arg['beta'] is None:
            beta = default['beta']
        else:
            beta = arg['beta']
        assert beta > 90, 'Non-standard monoclinic angle'

    elif crystal_system == 'triclinic':
        if arg['a'] is None:
            a = default['a']
        else:
            a = arg['a']
        if arg['b'] is None:
            b = default['b'] * a / default['a']
        else:
            b = arg['b']     
        if arg['c'] is None:
            c = default['c'] * a / default['a']
        else:
            c = arg['c'] 

        if arg['alpha'] is None:
            alpha = default['alpha']
        else:
            alpha = arg['alpha']
        if arg['beta'] is None:
            beta = default['beta']
        else:
            beta = arg['beta']     
        if arg['gamma'] is None:
            gamma = default['gamma']
        else:
            gamma = arg['gamma'] 

    return am.Box(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
