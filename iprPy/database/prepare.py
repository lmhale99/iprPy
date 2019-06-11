# Standard Python libraries
from pathlib import Path
import uuid
import shutil
from copy import deepcopy

# iprPy imports
from ..tools import aslist, filltemplate
from .. import load_record
from ..input import buildcombos, parse

def prepare(database, run_directory, calculation, input_script=None, **kwargs):
    """
    Function for preparing any iprPy calculation for high-throughput execution.
    Input parameters for preparing can either be given within an input script
    or by passing in keyword parameters.
    
    Parameters
    ----------
    database : iprPy.database.Database
        The database that will host the records for the prepared calculations
    run_directory : str
        The path to the local run_directory where the prepared calculations
        are to be placed.
    calculation : iprPy.calculation.Calculation
        The calculation to prepare.
    input_script : str or file-like object, optional
        The file, path to file, or contents of an input script containing
        parameters for preparing the calculation.  Cannot be given with kwargs.
    **kwargs : str or list
        Input parameters for preparing the calculation.  Values must be strings
        or list of strings if allowed by the calculation.
    """
    
    # Parse input_script to kwargs if given
    if input_script is not None:
        if len(kwargs) == 0:
            kwargs = parse(input_script, singularkeys=calculation.singularkeys)
        else:
            raise ValueError('input_script cannot be given with other keyword parameters')
    
    # Build dataframe of all existing records for the calculation style
    record_df = database.get_records_df(style=calculation.record_style,
                                        full=False, flat=True,
                                        script='calc_' + calculation.style)
    print(len(record_df), 'existing calculation records found', flush=True)
    
    # Check multikeys
    for keyset in calculation.multikeys:
        
        # Check lengths of multikey sets
        length = None
        for key in keyset:
            if key in kwargs:
                kwargs[key] = aslist(kwargs[key])
                if length is None:
                    length = len(kwargs[key])
                else:
                    if len(kwargs[key]) != length:
                        raise ValueError('Incompatible multikey lengths')
        
        # Fill in necessary blanks
        if length is None:
            for key in keyset:
                kwargs[key] = []
        else:
            for key in keyset:
                kwargs[key] = kwargs.get(key, ['' for i in range(length)])
                for i in range(len(kwargs[key])):
                    if kwargs[key][i].lower() == 'none':
                        kwargs[key][i] = ''
    
    # Handle prepare build special functions
    if 'buildcombos' in kwargs:
        for build_command in aslist(kwargs['buildcombos']):
            terms = build_command.split()
            
            # Set buildcombos name to style if name not given
            if len(terms) == 2:
                bname = terms[0]
            elif len(terms) == 3:
                bname = terms[2]
            else:
                raise ValueError('Invalid buildcombos command: must be "style key [name]"')
            
            # Save buildcombos style and associated multikeys set
            bstyle = terms[0]
            bkeys = None
            for keyset in calculation.multikeys:
                if terms[1] in keyset:
                    bkeys = keyset
            if bkeys is None:
                raise ValueError('No multikeys paired to buildcombos command')
            
            # Parse out all kwarg keys starting with buildcombos name
            bname_ = bname + '_'
            bkwargs = {}
            for key in list(kwargs.keys()):
                if key[:len(bname_)] == bname_:
                    bkwargs[key[len(bname_):]] = kwargs.pop(key)
            
            inputs = buildcombos(bstyle, database, bkeys, **bkwargs)
            for key in inputs:
                kwargs[key].extend(inputs[key])
    
    # Fill in missing values
    for key in calculation.singularkeys:
        kwargs[key] = kwargs.get(key, '')
    for keyset in calculation.multikeys:
        for key in keyset:
            if len(kwargs[key]) == 0:
                kwargs[key] = ['']
    
    # Start calculation_dict with all singularkeys
    calculation_dict = {}
    for key in calculation.singularkeys:
        calculation_dict[key] = kwargs[key]
    
    numprepared = 0

    # Iterate over multidict combinations
    for subdict in itermultidict(calculation.multikeys, **kwargs):
        calculation_dict.update(subdict)
        
        # Create calc_key
        calc_key = str(uuid.uuid4())
        
        # Build input_dict from calculation_dict
        input_dict = {}
        for key in calculation_dict:
            if calculation_dict[key] != '':
                input_dict[key] = deepcopy(calculation_dict[key])
            
            if key[-8:] == '_content':
                terms = input_dict[key].split()
                
                if terms[0] == 'file':
                    with open(terms[1], 'rb') as f:
                        input_dict[key] = f.read()
                
                elif terms[0] == 'record':
                    crecord = database.get_record(name=terms[1])
                    input_dict[key] = crecord.content.json(indent=4)
                
                elif terms[0] == 'tar':
                    tar = database.get_tar(name=terms[1])
                    f = tar.extractfile(terms[1] + '/' + ' '.join(terms[2:]))
                    input_dict[key] = f.read()
                    f.close()
                    tar.close()
        
        # Build incomplete record
        calculation.process_input(input_dict, calc_key, build=False)
        
        new_record = load_record(style=calculation.record_style, name=calc_key)
        new_record.buildcontent('calc_' + calculation.style, input_dict)
        
        # Check if record is valid and new
        if new_record.isvalid() and new_record.isnew(record_df=record_df):
            numprepared += 1

            # Add record to database
            database.add_record(record=new_record)
            
            # Generate calculation folder
            calc_directory = Path(run_directory, calc_key)
            calc_directory.mkdir(parents=True)
            
            # Save inputfile to calculation folder
            inputfile = filltemplate(calculation.template, calculation_dict, '<', '>')
            with open(Path(calc_directory, 'calc_' + calculation.style + '.in'), 'w') as f:
                f.write(inputfile)
            
            # Add calculation files to calculation folder
            for calc_file in calculation.files:
                shutil.copy(calc_file, calc_directory)
            
            # Save content keys to file keys
            for key_file in input_dict:
                if key_file[-5:] == '_file':
                    key_content = key_file.replace('_file', '_content')
                    dirpath = Path(calc_directory, input_dict[key_file]).parent
                    if not dirpath.is_dir():
                        dirpath.mkdir(parents=True)
                    try:
                        with open(Path(calc_directory, input_dict[key_file]), 'w') as f:
                            f.write(input_dict[key_content])
                    except:
                        with open(Path(calc_directory, input_dict[key_file]), 'wb') as f:
                            f.write(input_dict[key_content])
            
            # Copy potential artifacts if needed and exist
            if 'potential_dir' in input_dict:
                try:               
                    tar = database.get_tar(name=input_dict['potential_dir'])
                except:
                    pass
                else:
                    tar.extractall(calc_directory)
                    tar.close()
    print(numprepared, 'new calculations prepared')

def itermultidict(multikeys, **kwargs):
    
    # End recursion
    if len(multikeys) == 0:
        yield {}
    else:
        # Iterate over all options for first keyset
        keyset = multikeys[0]
        for i in range(len(kwargs[keyset[0]])):
            multidict = {}
            for key in keyset:
                multidict[key] = kwargs[key][i]
            
            # Recursively add subsequent keysets
            for subdict in itermultidict(multikeys[1:], **kwargs):
                yield merge_dicts(multidict, subdict)

def merge_dicts(dict1, dict2):
    newdict = dict1.copy()
    newdict.update(dict2)
    return newdict
