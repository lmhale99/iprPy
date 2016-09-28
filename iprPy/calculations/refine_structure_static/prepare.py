import os
import shutil
import sys
import glob
import uuid

from DataModelDict import DataModelDict as DM
import atomman.lammps as lmp

from iprPy.tools import fill_template, atomman_input, term_extractor
from .data_model import data_model
from .read_input import read_input

#Automatically identify the calculation's directory and name
__calc_dir__ = os.path.dirname(os.path.realpath(__file__)) 
__calc_type__ =  os.path.basename(__calc_dir__)
__calc_name__ = 'calc_' + __calc_type__

def description():
    """Returns a description for the calculation."""
    return "The refine_structure_static calculation uses molecular statics to find the equilibrium box size and elastic constants of a system using a specific potential and at a specific pressure."
    
def keywords():
    """Return the list of keywords used by this calculation that are searched for from the inline inline_terms and pre-defined global_variables."""
    return ['run_directory',
            'lib_directory',
            'copy_files',
            'lammps_command',
            'mpi_command',
            'potential_file',
            'potential_dir',
            'load',
            'load_options',
            'load_elements',
            'box_parameters',
            'size_mults',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'strain_range',
            'pressure_xx',
            'pressure_yy',
            'pressure_zz']

def singular_keywords():
    """Returns a dictionary of keywords that should have only one value for the calculation's prepare function, and the default values.""" 
    return {'run_directory':       None,
            'lib_directory':       None,
            'copy_files':          'true',
            'lammps_command':      None,
            'mpi_command':         '',
            'length_unit':         '',
            'pressure_unit':       '',
            'energy_unit':         '',
            'force_unit':          '',
            'strain_range':        '',
            'pressure_xx':         '',
            'pressure_yy':         '',
            'pressure_zz':         ''}

def unused_keywords():
    """Returns a list of the keywords in the calculation's template input file that the prepare function does not use."""
    return ['x-axis', 
            'y-axis', 
            'z-axis', 
            'shift']

def prepare(inline_terms, global_variables):
    """This is the prepare method for the calculation"""
    
    working_dir = os.getcwd()
    
    #Read in the calc_template 
    calc_template = __calc_name__ + '.template'
    with open(os.path.join(__calc_dir__, 'calc_files', calc_template)) as f:
        template = f.read()
    
    #Identify the contents of calc_files
    calc_files = os.listdir(os.path.join(__calc_dir__, 'calc_files'))
    calc_files.remove(calc_template)  

    #prepare_variables -- keywords used by this prepare function and the associated value lists given in inline_terms and global_variables
    #calculation_variables -- keywords in the calculation's template file. Empty and singular values filled in here, iterated values later 
    prepare_variables, calculation_variables = __initial_setup(inline_terms, global_variables)
    
    #Loop over all potentials
    for potential_file, potential_dir in zip(prepare_variables.aslist('potential_file'), 
                                             prepare_variables.aslist('potential_dir')):
        
        #Loop over all load systems
        for load, load_options, load_elements, box_parameters in zip(prepare_variables.aslist('load'), 
                                                                     prepare_variables.aslist('load_options'), 
                                                                     prepare_variables.aslist('load_elements'), 
                                                                     prepare_variables.aslist('box_parameters')):
        
            #Loop over all size_mults
            for size_mults in prepare_variables.aslist('size_mults'):
                
                #Add iterated values to calculation_variables
                calculation_variables['potential_file'] = potential_file
                calculation_variables['potential_dir'] =  potential_dir
                calculation_variables['load'] =           load
                calculation_variables['load_options'] =   load_options
                calculation_variables['box_parameters'] = box_parameters
                calculation_variables['size_mults'] =     size_mults
                calculation_variables['symbols'] =        ''
                
                #Fill in template using calculation_variables values, and build input_dict
                calc_in = fill_template(template, calculation_variables, '<', '>')
                input_dict = read_input(calc_in)
                
                #Extract info from input dict
                potential = lmp.Potential(input_dict['potential'])
                system_family = input_dict['system_family']
                
                #Check that the same potential is being used
                if 'system_potential' not in input_dict or input_dict['system_potential'] == potential.uuid:
                    
                    #Loop over all symbols combinations
                    for symbols in atomman_input.yield_symbols(load, load_options, load_elements, global_variables, potential):
                        
                        #Define directory path for the record
                        record_dir = os.path.join(calculation_variables['lib_directory'], str(potential), '-'.join(symbols), system_family, __calc_type__)
                        
                        #Add symbols to input_dict and build incomplete record
                        input_dict['symbols'] = list(symbols)               
                        record = data_model(input_dict)  
                        
                        #Check that no matching record already exists
                        if __is_new_record(record_dir, record):
                            
                            UUID = str(uuid.uuid4())
                            calculation_variables['symbols'] = ' '.join(symbols)
                            
                            #Create calculation run folder
                            sim_dir = os.path.join(calculation_variables['run_directory'], UUID)
                            os.makedirs(sim_dir)
                            
                            #Copy calc_files to run folder
                            for fname in calc_files:
                                shutil.copy(os.path.join(__calc_dir__, 'calc_files', fname), sim_dir)
                            
                            #Copy potential and load files to run directory and shorten paths
                            if calculation_variables['copy_files']:
                                
                                #Divy up the load information
                                load_terms = load.split()
                                load_style = load_terms[0]
                                load_file = ' '.join(load_terms[1:])
                                
                                #Copy loose files
                                shutil.copy(potential_file, sim_dir)
                                shutil.copy(load_file,      sim_dir)
                                
                                #Copy potential_dir and contents to run folder
                                os.mkdir(os.path.join(sim_dir, os.path.basename(potential_dir)))
                                for fname in glob.iglob(os.path.join(potential_dir, '*')):
                                    shutil.copy(fname, os.path.join(sim_dir, os.path.basename(potential_dir)))
                                
                                #Shorten file paths to be relative
                                calculation_variables['potential_file'] = os.path.basename(potential_file)
                                calculation_variables['potential_dir'] =  os.path.basename(potential_dir)
                                calculation_variables['load'] =           ' '.join([load_style, os.path.basename(load_file)])
                            
                            #Create calculation input file by filling in template with calculation_variables inline_terms
                            os.chdir(sim_dir)
                            calc_in = fill_template(template, calculation_variables, '<', '>')
                            input_dict = read_input(calc_in, UUID)
                            with open(__calc_name__ + '.in', 'w') as f:
                                f.write('\n'.join(calc_in))
                            os.chdir(working_dir)
                            
                            #Save the record to the library
                            with open(os.path.join(record_dir, UUID + '.xml'), 'w') as f:
                                record.xml(fp=f, indent=2)
                        
def __initial_setup(inline_terms, global_variables):
    """
    Checks that the values in prepare_variables are of appropriate length, and returns calculation_variables dictionary with all empty and singular values.
    """
    
    #Construct prepare_variables dictionary using_inline inline_terms and global_variables
    prepare_variables = term_extractor(inline_terms, global_variables, keywords())
    
    #Initialize calculation_variables
    calculation_variables = DM()
    
    #Save inline_terms that must be singular-valued to calculation_variables 
    for keyword, default in singular_keywords().iteritems():
        calculation_variables[keyword] = atomman_input.get_value(prepare_variables, keyword, default)
    
    #Fill in mandatory blank values
    for keyword in unused_keywords():
        calculation_variables[keyword] = ''
        
        #Issue a warning if the keyword is defined in global_variables
        if keyword in global_variables:
            print 'Warning: high-throughput of', __calc_type__, 'ignores term', keyword
            
    #Convert 'copy_files' to boolean flag
    if calculation_variables['copy_files'].lower() == 'true':
        calculation_variables['copy_files'] = True
    elif calculation_variables['copy_files'].lower() == 'false':
        calculation_variables['copy_files'] = False
    else:
        raise ValueError('copy_files must be either True or False!')
    
    #Check lengths of the iterated global_variables
    assert len(prepare_variables.aslist('potential_file')) == len(prepare_variables.aslist('potential_dir')),  'potential_file and potential_dir must be of the same length'
    assert len(prepare_variables.aslist('load')) ==           len(prepare_variables.aslist('load_options')),   'load and load_options must be of the same length'
    assert len(prepare_variables.aslist('load')) ==           len(prepare_variables.aslist('load_elements')),  'load and load_elements must be of the same length'
    assert len(prepare_variables.aslist('load')) ==           len(prepare_variables.aslist('box_parameters')), 'load and box_parameters must be of the same length'
    
    #Set default values for iterated global_variables
    if len(prepare_variables.aslist('size_mults')) == 0:  prepare_variables['size_mults'] = '3 3 3'  
    
    return prepare_variables, calculation_variables
    
def __is_new_record(record_dir, record):
    """Check if a matching record already exists."""
    match_keys = [['calculation-system-relax', 'calculation', 'script'],
                  ['calculation-system-relax', 'calculation', 'run-parameter', 'strain-range'],
                  ['calculation-system-relax', 'calculation', 'run-parameter', 'load_options'],
                  ['calculation-system-relax', 'potential', 'id'],
                  ['calculation-system-relax', 'system-info', 'artifact'],
                  ['calculation-system-relax', 'system-info', 'symbols'],
                  ['calculation-system-relax', 'phase-state', 'temperature'],
                  ['calculation-system-relax', 'phase-state', 'pressure-xx'],
                  ['calculation-system-relax', 'phase-state', 'pressure-yy'],
                  ['calculation-system-relax', 'phase-state', 'pressure-zz']]

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