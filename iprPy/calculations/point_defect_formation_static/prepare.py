import os
import shutil
import sys
import glob
import uuid

from DataModelDict import DataModelDict as DM
import atomman.lammps as lmp
import atomman as am

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
    min_template =  os.path.join(__calc_dir__, 'min.template')
    
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
                
                #Skip if load relaxed with a different potential
                try:
                    pot_key = model.find('potential')['key']
                    if pot_key != potential.uuid:
                        continue
                except:
                    pass
                
                #Get or make the load artifact family name
                try:
                    system_family = model.find('system-info')['artifact']['family']
                except:
                    system_family = os.path.splitext(load_base)[0]
            else:
                system_family = os.path.splitext(load_base)[0]
            
            #Loop over all point defect data models
            for ptd_model in variable.aslist('ptd_model'):
                    
                #Check if ptd_model's system_family matches the load_file's system_family
                with open(ptd_model) as f:
                    ptd = DM(f)
                if system_family != ptd['point-defect']['system-family']:
                    continue
               
                #Pass system's file, options and box parameters to v_dict
                v_dict['load'] = ' '.join([load_terms[0], load_base])
                v_dict['load_options'] = load_options
                v_dict['box_parameters'] = box_parameters
                
                #Pass defect model to v_dict
                ptd_file = os.path.basename(ptd_model)
                v_dict['ptd_model'] = ptd_file
                v_dict['ptd_name'] = ptd['point-defect']['identifier']['name']
                
                #Loop over all symbols combinations
                for symbols in atomman_input.yield_symbols(load, load_options, load_elements, variable, potential):
                    
                    #Pass symbols to v_dict
                    v_dict['symbols'] = ' '.join(symbols)
                    
                    #Define directory path for the record
                    record_dir = os.path.join(lib_directory, str(potential), '-'.join(symbols), system_family, __calc_type__)

                    #Loop over all size_mults
                    for size_mults in variable.aslist('size_mults'):
                        v_dict['size_mults'] = size_mults
                        #Check if record already exists
                        if __is_new_record(record_dir, v_dict):
                            UUID = str(uuid.uuid4())
                            
                            #Create calculation run folder
                            sim_dir = os.path.join(run_directory, UUID)
                            os.makedirs(sim_dir)
                            
                            #Copy files to run folder
                            shutil.copy(calc_py, sim_dir)
                            shutil.copy(min_template, sim_dir)
                            shutil.copy(potential_file, sim_dir)
                            shutil.copy(load_file, sim_dir)
                            shutil.copy(ptd_model, sim_dir)
                            
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
       
    v_dict['length_unit'] =    atomman_input.get_value(v, 'length_unit',   '')
    v_dict['pressure_unit'] =  atomman_input.get_value(v, 'pressure_unit', '')
    v_dict['energy_unit'] =    atomman_input.get_value(v, 'energy_unit',   '')
    v_dict['force_unit'] =     atomman_input.get_value(v, 'force_unit',    '')
    
    v_dict['energy_tolerance']    = atomman_input.get_value(v, 'energy_tolerance',    '')
    v_dict['force_tolerance']     = atomman_input.get_value(v, 'force_tolerance',     '')
    v_dict['maximum_iterations']  = atomman_input.get_value(v, 'maximum_iterations',  '')
    v_dict['maximum_evaluations'] = atomman_input.get_value(v, 'maximum_evaluations', '')
    
    #Check lengths of the multi-valued variables
    assert len(v.aslist('potential_file')) == len(v.aslist('potential_dir')), 'potential_file and potential_dir must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('load_options')), 'load and load_options must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('load_elements')), 'load and load_elements must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('box_parameters')), 'load and box_parameters must be of the same length'
    
    #Check that other variables are of at least length 1
    if len(v.aslist('size_mults')) == 0:
        v['size_mults'] = '1 1 1'  
    assert len(v.aslist('ptd_model')) > 0, 'no ptd_model found'
    
    #Read in terms
    #NO TERMS DEFINED FOR THIS CALCULATION
    #t = term_extractor(t, [])
    #v_dict[] = atomman_input.get_value(t, '', '')
            
    return run_directory, lib_directory, v_dict
    
def __is_new_record(record_dir, v_dict):
    """Check if a matching record already exists."""
    try:
        flist = os.listdir(record_dir) 
    except:
        os.makedirs(record_dir) 
        return True

    is_new = True
    for fname in flist:
        if os.path.splitext(fname)[1] in ['.xml', '.json']:
            with open(os.path.join(record_dir, fname)) as f:
                record = DM(f)
           
            sys_file = record.find('system-info')['artifact']['file']
            
            load_file = ' '.join(v_dict['load'].split()[1:])
            if sys_file != load_file:
                continue
            
            ptd_name = record.find('point-defect')['identifier']['name']
            if ptd_name != v_dict['ptd_name']:
                continue
                
            a_mult = record.find('a-multiplyer')
            b_mult = record.find('b-multiplyer')
            c_mult = record.find('c-multiplyer')
            
            mults = v_dict['size_mults'].split()
            if len(mults) == 3:
                a_m = abs(int(mults[0]))
                b_m = abs(int(mults[1]))
                c_m = abs(int(mults[2]))
            elif len(mults) == 6:
                a_m = int(mults[1]) - int(mults[0])
                b_m = int(mults[3]) - int(mults[2])
                c_m = int(mults[5]) - int(mults[4])
            else:
                raise ValueError('Invalid size_mults term')
                
            if (a_m, b_m, c_m) == (a_mult, b_mult, c_mult):
                is_new = False
                break
        
    return is_new
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
