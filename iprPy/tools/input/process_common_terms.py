import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from DataModelDict import DataModelDict as DM
import numpy as np
import os
from ..term_extractor import term_extractor
from copy import deepcopy
import uuid

def process_common_terms(input_dict, UUID=None):
    """
    Process the common calculation input terms contained in input_dict. 
    
    The list of keys in input_dict that this function looks for and the 
    default values given to missing keys:
    - lammps_command, potential_file, load -- must be given
    - uuid -- can be prespecified in input_dict, or as a function argument. 
              default is a newly generated uuid4 string    
    - symbols -- must be given if not contained in the load file
    - mpi_command, load_options, box_parameters -- default to None
    - potential_dir -- default to '' (current directory)
    - length_unit -- default to 'angstrom'
    - energy_unit -- default to 'eV'
    - pressure_unit -- default to 'GPa'
    - force_unit -- default to 'eV/angstrom'
    - x-axis -- default to '1 0 0'
    - y-axis -- default to '0 1 0'
    - z-axis -- default to '0 0 1' (all axes together = no rotation)
    - size_mults -- default to '1 1 1' (no supersizing)
    - atom_shift -- default to '0 0 0' (no position shifting)

    Additional keys that are added to input_dict:
    - potential -- the loaded contents of the potential_file
    - system_family -- family name for tracking calculations derived from the 
                       same load configurations
    - ucell -- the original system as given by only load, load_options and 
               box_parameters
    - initial_system -- the system after ucell has been shifted, rotated and 
                        supersized according to atom_shift, x-axis, y-axis, 
                        z-axis, and size_mults 
    """    
        
    #Assert required keys exist
    assert 'lammps_command' in input_dict, 'lammps_command value not supplied'
    assert 'potential_file' in input_dict, 'potential_file value not supplied'
    assert 'load'           in input_dict, 'load value not supplied'
    
    #Set default values to optional keys
    if UUID is not None:
        input_dict['uuid'] =       UUID
    else:
        input_dict['uuid'] =       input_dict.get('uuid',           str(uuid.uuid4()))
    
    input_dict['mpi_command'] =    input_dict.get('mpi_command',    None)
    input_dict['potential_dir'] =  input_dict.get('potential_dir',  '')
    
    input_dict['length_unit'] =    input_dict.get('length_unit',    'angstrom')
    input_dict['energy_unit'] =    input_dict.get('energy_unit',    'eV')
    input_dict['pressure_unit'] =  input_dict.get('pressure_unit',  'GPa')
    input_dict['force_unit'] =     input_dict.get('force_unit',     'eV/angstrom')
    
    input_dict['load_options'] =   input_dict.get('load_options',   None)
    input_dict['box_parameters'] = input_dict.get('box_parameters', None)
    input_dict['symbols'] =        input_dict.get('symbols',        None)
    
    input_dict['x-axis'] =         input_dict.get('x-axis',         [1, 0, 0])    
    input_dict['y-axis'] =         input_dict.get('y-axis',         [0, 1, 0])
    input_dict['z-axis'] =         input_dict.get('z-axis',         [0, 0, 1])
    input_dict['atom_shift'] =     input_dict.get('atom_shift',     [0, 0, 0])   
    input_dict['size_mults'] =     input_dict.get('size_mults',     [(0,1), (0,1), (0,1)])
 
    #Convert strings to number lists
    if isinstance(input_dict['x-axis'], (str, unicode)): 
        input_dict['x-axis'] = list(np.array(input_dict['x-axis'].strip().split(), dtype=float))
    if isinstance(input_dict['y-axis'], (str, unicode)): 
        input_dict['y-axis'] = list(np.array(input_dict['y-axis'].strip().split(), dtype=float))
    if isinstance(input_dict['z-axis'], (str, unicode)):
        input_dict['z-axis'] = list(np.array(input_dict['z-axis'].strip().split(), dtype=float))
    if isinstance(input_dict['atom_shift'], (str, unicode)): 
        input_dict['atom_shift'] = list(np.array(input_dict['atom_shift'].strip().split(), dtype=float))
    if isinstance(input_dict['size_mults'], (str, unicode)): 
        input_dict['size_mults'] = list(np.array(input_dict['size_mults'].strip().split(), dtype=int))        
        
    #Read contents of potential_file into potential
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = DM(f)
    
    #load
    load_terms = input_dict['load'].split(' ')
    assert len(load_terms) > 1, 'load value must specify both style and file'
    load_style = load_terms[0]
    load_file =  ' '.join(load_terms[1:])    
   
    #system_family
    #check if system_model files already have an assigned system_family    
    if load_style == 'system_model':
        with open(load_file) as f:
            model = DM(f)
        #pass existing system_family name onto next generation
        try:
            input_dict['system_family'] = model.find('system-info')['artifact']['family']
        #generate new system_family name using the load_file 
        except:
            input_dict['system_family'] = os.path.splitext(os.path.basename(load_file))[0]
    #Other load_styles won't have a system family, so generate one using the load_file 
    else:
        input_dict['system_family'] = os.path.splitext(os.path.basename(load_file))[0]
    
    #load_options
    kwargs= {}
    if input_dict['load_options'] is not None:
        load_options_keys = ['key', 'data_set', 'pbc', 'atom_style', 'units', 'prop_info']
        kwargs = term_extractor(input_dict['load_options'], load_options_keys)
        
    #ucell and symbols
    ucell = am.System()
    if True:
        symbols = ucell.load(load_style, load_file, **kwargs)
    else:
        symbols = None
        ucell = None            
    if input_dict['symbols'] is None:
        input_dict['symbols'] = symbols
    else:
        input_dict['symbols'] = input_dict['symbols'].split(' ')
        assert len(symbols) == len(input_dict['symbols']), 'Number of symbols does not match number of sites'
    
    #This is necessary if trying to read an incomplete system_model
    if ucell is not None:
        input_dict['ucell'] = ucell
    
        #box_parameters
        if input_dict['box_parameters'] is not None:
            box_params = input_dict['box_parameters'].split(' ')
            if len(box_params) == 4 or len(box_params) == 7:
                unit = box_params[-1]
                box_params = box_params[:-1]
            else:
                unit = input_dict['length_unit']
            
            box_params = uc.set_in_units(np.array(box_params, dtype=float), unit)
            
            if len(box_params) == 3:
                input_dict['ucell'].box_set(a=box_params[0], b=box_params[1], c=box_params[2], scale=True) 
            elif len(box_params) == 6:
                input_dict['ucell'].box_set(a=box_params[0], b=box_params[1], c=box_params[2],
                                            alpha=box_params[0], beta=box_params[1], gamma=box_params[2], 
                                            scale=True) 
            else:
                ValueError('Invalid box_parameters command')
    
        #create initial_system
        input_dict['initial_system'] = deepcopy(input_dict['ucell'])
        
        #x-axis, y-axis, z-axis
        axes = np.array([input_dict['x-axis'], input_dict['y-axis'], input_dict['z-axis']], dtype='float64')

        if True:
            input_dict['initial_system'] = am.tools.rotate_cubic(input_dict['initial_system'], axes)
        else:
            input_dict['initial_system'] = lmp.normalize(am.tools.rotate(input_dict['initial_system'], axes))
            
        #atom_shift
        shift = (input_dict['atom_shift'][0] * input_dict['initial_system'].box.avect +
                 input_dict['atom_shift'][1] * input_dict['initial_system'].box.bvect +
                 input_dict['atom_shift'][2] * input_dict['initial_system'].box.cvect)
        pos = input_dict['initial_system'].atoms_prop(key='pos')
        input_dict['initial_system'].atoms_prop(key='pos', value=pos+shift)
        
        #size_mults
        if len(input_dict['size_mults']) == 6:
            input_dict['size_mults'] = [(input_dict['size_mults'][0], input_dict['size_mults'][1]), 
                                        (input_dict['size_mults'][2], input_dict['size_mults'][3]),
                                        (input_dict['size_mults'][4], input_dict['size_mults'][5])]
            
        if len(input_dict['size_mults']) == 3:
            for i in xrange(3):
                if isinstance(input_dict['size_mults'][i], (int, long)):
                    if input_dict['size_mults'][i] > 0:
                        input_dict['size_mults'][i] = (0, input_dict['size_mults'][i])
                    elif input_dict['size_mults'][i] < 0:
                        input_dict['size_mults'][i] = (input_dict['size_mults'][i], 0)
            input_dict['initial_system'].supersize(input_dict['size_mults'][0], input_dict['size_mults'][1], input_dict['size_mults'][2])
                                                   
        else:
            raise ValueError('Invalid size_mults command')                              
        
        