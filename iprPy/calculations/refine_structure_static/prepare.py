import os
import shutil
import sys
import glob
import uuid

from DataModelDict import DataModelDict as DM
import atomman.lammps as lmp

from iprPy.tools import fill_template, import_calc, atomman_input, term_extractor

#Automatically identify the calculation's directory and name
__calc_dir__ = os.path.dirname(os.path.realpath(__file__)) 
__calc_type__ =  os.path.basename(__calc_dir__)
__calc_name__ = 'calc_' + __calc_type__
calc = import_calc(__calc_dir__, __calc_name__)

def prepare(terms, variable):
    """This is the prepare method for the calculation"""
    
    working_dir = os.getcwd()
    
    #Identify the necessary run files in the calculation directory
    calc_template = os.path.join(__calc_dir__, __calc_name__ + '.template')
    calc_py =       os.path.join(__calc_dir__, __calc_name__ + '.py')
    cij_template =  os.path.join(__calc_dir__, 'cij.template')
    
    #Read in the calc_template 
    with open(calc_template) as f:
        template = f.read()
    
    #Interpret and check terms and variables
    run_directory, lib_directory, v_dict = __initial_setup(terms, variable)
    
    #Loop over all potentials
    for potential_file, potential_dir in zip(variable.aslist('potential_file'), 
                                             variable.aslist('potential_dir')):
        
        #Load potential
        with open(potential_file) as f:
            potential = lmp.Potential(f)
        
        #Pass potential's file and directory info to v_dict
        v_dict['potential_file'] = os.path.basename(potential_file)
        v_dict['potential_dir'] = os.path.basename(potential_dir)
        
        #Loop over all systems
        for load, load_options, load_elements, box_parameters in zip(variable.aslist('load'), 
                                                                     variable.aslist('load_options'),
                                                                     variable.aslist('load_elements'), 
                                                                     variable.aslist('box_parameters')):
            
            #Divy up the load information
            load_terms = load.split()
            load_style = load_terms[0]
            load_file = ' '.join(load_terms[1:])
            load_base = os.path.basename(load_file)
            
            #Check for system_model fields from previous simulations
            if load_style == 'system_model':
                with open(load_file) as f:
                    model = DM(f)
                try:
                    system_family = model.find('system-info')['artifact']['family']
                except:
                    system_family = os.path.splitext(load_base)[0]
            else:
                system_family = os.path.splitext(load_base)[0]
            
            #Pass system's file, options and box parameters to v_dict
            v_dict['load'] = ' '.join([load_terms[0], load_base])
            v_dict['load_options'] = load_options
            v_dict['box_parameters'] = box_parameters

            #Loop over all symbols combinations
            for symbols in atomman_input.yield_symbols(load, load_options, load_elements, variable, potential):
                
                #Pass symbols to v_dict
                v_dict['symbols'] = ' '.join(symbols)
                
                #Define directory path for the record
                record_dir = os.path.join(lib_directory, str(potential), '-'.join(symbols), system_family, __calc_type__)
                  
                #Check if record already exists
                if __is_new_record(record_dir, v_dict):
                    UUID = str(uuid.uuid4())
                    
                    #Create calculation run folder
                    sim_dir = os.path.join(run_directory, UUID)
                    os.makedirs(sim_dir)
                    
                    #Copy files to run folder
                    shutil.copy(calc_py, sim_dir)
                    shutil.copy(cij_template, sim_dir)
                    shutil.copy(potential_file, sim_dir)
                    shutil.copy(load_file, sim_dir)
                    
                    #Copy potential_dir and contents to run folder
                    os.mkdir(os.path.join(sim_dir, os.path.basename(potential_dir)))
                    for fname in glob.iglob(os.path.join(potential_dir, '*')):
                        shutil.copy(fname, os.path.join(sim_dir, os.path.basename(potential_dir)))
                    
                    #Create calculation input file by filling in template with v_dict terms
                    os.chdir(sim_dir)
                    calc_in = fill_template(template, v_dict, '<', '>')
                    input_dict = calc.input(calc_in, UUID)
                    with open(__calc_name__ + '.in', 'w') as f:
                        f.write('\n'.join(calc_in))
                    os.chdir(working_dir)
                    
                    #Save the incomplete record
                    model = calc.data_model(input_dict)
                    with open(os.path.join(record_dir, UUID + '.json'), 'w') as f:
                        model.json(fp=f, indent=2)
                    
                    
                    
def __initial_setup(t, v):
    """
    Pulls out the singular values in terms, t, and variables, v.
    Asserts that multi-valued variables are of appropriate lengths.
    """
    
    v_dict = DM()
    
    #read in run and library directory information
    run_directory = atomman_input.get_value(v, 'run_directory')
    lib_directory = atomman_input.get_value(v, 'lib_directory')
    
    #read in the simulation-dependent singular valued variables
    v_dict['lammps_command'] = atomman_input.get_value(v, 'lammps_command')
    v_dict['mpi_command'] =    atomman_input.get_value(v, 'mpi_command', '')
    
    v_dict['size_mults'] =     atomman_input.get_value(v, 'size_mults', '')
    
    v_dict['length_unit'] =    atomman_input.get_value(v, 'length_unit', '')
    v_dict['pressure_unit'] =  atomman_input.get_value(v, 'pressure_unit', '')
    v_dict['energy_unit'] =    atomman_input.get_value(v, 'energy_unit', '')
    
    #Check lengths of the multi-valued variables
    assert len(v.aslist('potential_file')) == len(v.aslist('potential_dir')), 'potential_file and potential_dir must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('load_options')), 'load and load_options must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('load_elements')), 'load and load_elements must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('box_parameters')), 'load and box_parameters must be of the same length'
    
    #Read in terms
    t = term_extractor(t, ['strain_range', 'Pxx', 'Pyy', 'Pzz'])
    v_dict['strain_range'] = atomman_input.get_value(t, 'strain_range', '')
    v_dict['pressure_xx'] = atomman_input.get_value(t, 'Pxx', '')
    v_dict['pressure_yy'] = atomman_input.get_value(t, 'Pyy', '')
    v_dict['pressure_zz'] = atomman_input.get_value(t, 'Pzz', '')
                
    return run_directory, lib_directory, v_dict
    
def __is_new_record(record_dir, v_dict):
    """Check if a matching record already exists."""
    try:
        flist = os.listdir(record_dir) 
    except:
        os.makedirs(record_dir) 
        flist = []

    is_new = True
    for fname in flist:
        if os.path.splitext(fname)[1] in ['.xml', '.json']:
            is_new = False
            break
        
    return is_new
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
