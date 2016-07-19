import os
import shutil
import sys
import glob
import uuid

from DataModelDict import DataModelDict as DM
import atomman.lammps as lmp
import atomman as am

from iprPy.tools import fill_template, import_calc, atomman_input, term_extractor
from .data_model import data_model
from .read_input import read_input

#Automatically identify the calculation's directory and name
__calc_dir__ = os.path.dirname(os.path.realpath(__file__))   
__calc_type__ =  os.path.basename(__calc_dir__)
__calc_name__ = 'calc_' + __calc_type__
copy_files = True

def description():
    """Returns a description for the calculation."""
    return "The stacking_fault_static_FINAL calculation ..."
    
def keywords():
    """Return the list of keywords used by this calculation that are searched for from the inline terms and pre-defined variables."""
    return ['run_directory',
            'lib_directory',
            'lammps_command',
            'mpi_command',
            'potential_file',
            'potential_dir',
            'load',
            'load_options',
            'load_elements',
            'size_mults',
            'box_parameters',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'stacking_fault_model',
            'stacking_fault_shift_amount',
            'energy_tolerance',
            'force_tolerance',
            'maximum_iterations',
            'maximum_evaluations']

def prepare(terms, variables):
    """This is the prepare method for the calculation"""
    
    working_dir = os.getcwd()
    
    #Read in the calc_template 
    calc_template = __calc_name__ + '.template'
    with open(os.path.join(__calc_dir__, 'calc_files', calc_template)) as f:
        template = f.read()
    
    #Identify the contents of calc_files
    calc_files = os.listdir(os.path.join(__calc_dir__, 'calc_files'))
    calc_files.remove(calc_template)
    
    #Construct v, the dictionary of keywords for this function, using inline terms and pre-defined variables
    v = term_extractor(terms, variables, keywords())
    
    #Check lengths of v values and pull out single-valued terms
    run_directory, lib_directory, v_run = __initial_setup(v)
    
    #Loop over all potentials
    for potential_file, potential_dir in zip(v.aslist('potential_file'), 
                                             v.aslist('potential_dir')):

        #Loop over all systems
        for load, load_options, load_elements, box_parameters in zip(v.aslist('load'), 
                                                                     v.aslist('load_options'),
                                                                     v.aslist('load_elements'), 
                                                                     v.aslist('box_parameters')):
            
            #Loop over all stacking fault data models
            for stacking_fault_model in v.aslist('stacking_fault_model'):
                
                #Loop over all size_mults
                for size_mults in v.aslist('size_mults'):
                    
                
                    #Fill v_run with variable values
                    v_run['potential_file'] = potential_file
                    v_run['potential_dir'] =  potential_dir
                    v_run['load'] =           load
                    v_run['load_options'] =   load_options
                    v_run['box_parameters'] = box_parameters
                    v_run['symbols'] =        ''
                    v_run['size_mults'] =     size_mults
                    v_run['stacking_fault_model'] = stacking_fault_model
                    v_run['stacking_fault_shift_amount'] = '0 0 0'
                
                    #Fill template and build input_dict
                    calc_in = fill_template(template, v_run, '<', '>')
                    input_dict = read_input(calc_in)
                    
                    #Extract potential and system_family from input dict
                    potential = lmp.Potential(input_dict['potential'])
                    system_family = input_dict['system_family']

                    #Check that stacking fault's system_family matches
                    if system_family != input_dict['stacking_fault_model']['stacking_fault-parameters']['system-family']:
                        continue
            
                    #Loop over all symbols combinations
                    for symbols in atomman_input.yield_symbols(load, load_options, load_elements, variables, potential):

                        #Loop over all shift amounts
                        for stacking_fault_shift_amount in v.aslist('stacking_fault_shift_amount'):
                            
                            #Define directory path for the record
                            record_dir = os.path.join(lib_directory, str(potential), '-'.join(symbols), system_family, __calc_type__)
                            
                            #Add symbols to input_dict and build incomplete record
                            input_dict['symbols'] = list(symbols)   
                            input_dict['stacking_fault_shift_amount'] = stacking_fault_shift_amount
                            record = data_model(input_dict)  
                            
                            #Check if record already exists
                            if __is_new_record(record_dir, record):
                                
                                UUID = str(uuid.uuid4())
                                v_run['symbols'] = ' '.join(symbols)
                                v_run['stacking_fault_shift_amount'] = stacking_fault_shift_amount
                                
                                #Create calculation run folder
                                sim_dir = os.path.join(run_directory, UUID)
                                os.makedirs(sim_dir)
                                
                                #Copy calc_files to run folder
                                for fname in calc_files:
                                    shutil.copy(os.path.join(__calc_dir__, 'calc_files', fname), sim_dir)
                                
                                #Copy potential and load files to run directory and shorten paths
                                if copy_files:
                                    #Divy up the load information
                                    load_terms = load.split()
                                    load_style = load_terms[0]
                                    load_file = ' '.join(load_terms[1:])
                                    load_base = os.path.basename(load_file)
                                    
                                    v_run['potential_file'] = os.path.basename(potential_file)
                                    v_run['potential_dir'] =  os.path.basename(potential_dir)
                                    v_run['load'] =           ' '.join([load_terms[0], load_base])
                                    v_run['stacking_fault_model'] = os.path.basename(stacking_fault_model)
                                    
                                    shutil.copy(potential_file, sim_dir)
                                    shutil.copy(load_file, sim_dir)
                                    shutil.copy(stacking_fault_model, sim_dir)
                                
                                    #Copy potential_dir and contents to run folder
                                    os.mkdir(os.path.join(sim_dir, os.path.basename(potential_dir)))
                                    for fname in glob.iglob(os.path.join(potential_dir, '*')):
                                        shutil.copy(fname, os.path.join(sim_dir, os.path.basename(potential_dir)))
                                
                                #Create calculation input file by filling in template with v_run terms
                                os.chdir(sim_dir)
                                calc_in = fill_template(template, v_run, '<', '>')
                                input_dict = read_input(calc_in, UUID)
                                with open(__calc_name__ + '.in', 'w') as f:
                                    f.write('\n'.join(calc_in))
                                os.chdir(working_dir)
                                
                                #Save the record to the library
                                with open(os.path.join(record_dir, UUID + '.json'), 'w') as f:
                                    record.json(fp=f, indent=2)
                        
                        
                    
def __initial_setup(v):
    """
    Check that the lengths of variables are appropriate and pull out single-valued variables.
    Return run_directory, lib_directory, and v_run (the keyword dictionary for a single run)
    """
    
    v_run = DM()
    
    #read in run and library directory information
    run_directory = atomman_input.get_value(v, 'run_directory')
    lib_directory = atomman_input.get_value(v, 'lib_directory')
    
    #read in the simulation-dependent singular valued variables
    v_run['lammps_command'] = atomman_input.get_value(v, 'lammps_command')
    v_run['mpi_command'] =    atomman_input.get_value(v, 'mpi_command', '')
       
    v_run['length_unit'] =    atomman_input.get_value(v, 'length_unit',   '')
    v_run['pressure_unit'] =  atomman_input.get_value(v, 'pressure_unit', '')
    v_run['energy_unit'] =    atomman_input.get_value(v, 'energy_unit',   '')
    v_run['force_unit'] =     atomman_input.get_value(v, 'force_unit',    '')
    
    v_run['energy_tolerance']    = atomman_input.get_value(v, 'energy_tolerance',    '')
    v_run['force_tolerance']     = atomman_input.get_value(v, 'force_tolerance',     '')
    v_run['maximum_iterations']  = atomman_input.get_value(v, 'maximum_iterations',  '')
    v_run['maximum_evaluations'] = atomman_input.get_value(v, 'maximum_evaluations', '')
    
    #Check lengths of the multi-valued variables
    assert len(v.aslist('potential_file')) == len(v.aslist('potential_dir')), 'potential_file and potential_dir must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('load_options')), 'load and load_options must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('load_elements')), 'load and load_elements must be of the same length'
    assert len(v.aslist('load')) == len(v.aslist('box_parameters')), 'load and box_parameters must be of the same length'
    
    #Check that other variables are of at least length 1
    if len(v.aslist('size_mults')) == 0:
        v['size_mults'] = '1 1 1'  
    assert len(v.aslist('stacking_fault_model')) > 0, 'no stacking_fault_model found'
            
    return run_directory, lib_directory, v_run
    
def __is_new_record(record_dir, record):
    """Check if a matching record already exists."""
    match_keys = [['calculation-generalized-planar-fault', 'calculation', 'script'],
                  ['calculation-generalized-planar-fault', 'calculation', 'run-parameter', 'size-multipliers'],
                  ['calculation-generalized-planar-fault', 'calculation', 'run-parameter', 'energy_tolerance'],
                  ['calculation-generalized-planar-fault', 'calculation', 'run-parameter', 'force_tolerance'],
                  ['calculation-generalized-planar-fault', 'calculation', 'run-parameter', 'maximum_iterations'],
                  ['calculation-generalized-planar-fault', 'calculation', 'run-parameter', 'maximum_evaluations'],
                  ['calculation-generalized-planar-fault', 'calculation', 'run-parameter', 'stacking_fault_shift_amount'],
                  ['calculation-generalized-planar-fault', 'potential', 'id'],
                  ['calculation-generalized-planar-fault', 'system-info', 'artifact'],
                  ['calculation-generalized-planar-fault', 'system-info', 'symbols'],
                  ['calculation-generalized-planar-fault', 'stacking-fault-parameters', 'stacking-fault', 'id']]
    
    try:
        flist = os.listdir(record_dir) 
    except:
        os.makedirs(record_dir) 
        flist = []
        return True
  
    for fname in flist:
        if os.path.splitext(fname)[1] in ['.xml', '.json']:
            with open(os.path.join(record_dir, fname)) as f:
                old_record = DM(f)
            
            match = True
            for match_key in match_keys:
                record_value = record[match_key]
                old_value = old_record[match_key]
                
                if not isclose(record_value, old_value, abs_tol=1e-9):
                    match = False
                    break

            if match:
                return False
                    
    return True
 
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    if a == b:
        return True
    else:
        try:
            return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol) 
        except:
            return False