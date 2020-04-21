# coding: utf-8
# Standard Python libraries
from pathlib import Path
import uuid
import shutil
from copy import deepcopy

import atomman as am

import pandas as pd

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
    filedict = calculation.filedict
    record = load_record(calculation.record_style)

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

    # Complete kwargs with default values and buildcombos actions
    kwargs, content_dict = fill_kwargs(database, calculation, kwargs)

    # Build all combinations
    test_records, test_record_df, test_inputfiles, test_contents, content_dict = build_testrecords(database, calculation, content_dict, **kwargs)
    print(len(test_record_df), 'record combinations to check', flush=True)
    if len(test_record_df) == 0:
        return
    
    # Find new unique combinations
    newrecord_df = new_calculations(record_df, test_record_df, record.compare_terms, record.compare_fterms)
    print(len(newrecord_df), 'new records to prepare', flush=True)

    # Iterate over new records and prepare
    for i, newrecord_series in newrecord_df.iterrows():
        newrecord = test_records[i]
        inputfile = test_inputfiles[i]
        copy_content = test_contents[i]
        
        # Generate calculation folder
        calc_directory = Path(run_directory, newrecord_series.key)
        if not calc_directory.is_dir():
            calc_directory.mkdir(parents=True)

        # Save inputfile to calculation folder
        with open(Path(calc_directory, f'calc_{calculation.style}.in'), 'w') as f:
            f.write(inputfile)

        # Copy calculation files to calculation folder
        for filename in filedict:
            calc_file = Path(calc_directory, filename)
            with open(calc_file, 'w') as f:
                f.write(filedict[filename])

        # Copy/generate content files keys
        for content in copy_content:
            terms = content.split()

            if terms[0] == 'record':
                record_name = terms[1]
                record_file = Path(calc_directory, record_name+'.json')
                with open(record_file, 'w') as f:
                    content_dict[record_name].json(fp=f, indent=4)

            elif terms[0] == 'tarfile':
                tar = database.get_tar(name=terms[1])
                file_name = terms[1] + '/' + ' '.join(terms[2:])
                tar.extract(file_name, calc_directory)
                tar.close()
            
            elif terms[0] == 'tar':
                tar = database.get_tar(name=terms[1])
                tar.extractall(calc_directory)
                tar.close()
        
        # Add record to database
        database.add_record(record=newrecord)

def fill_kwargs(database, calculation, kwargs):
    """
    Fills in kwargs with default values and buildcombos results.
    """
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

    # Initialize content dict
    content_dict = {}
                        
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

            inputs, content_dict = buildcombos(bstyle, database, bkeys, content_dict=content_dict, **bkwargs)

            for key in inputs:
                kwargs[key].extend(inputs[key])

    # Fill in missing values
    for key in calculation.singularkeys:
        kwargs[key] = kwargs.get(key, '')
    for keyset in calculation.multikeys:
        for key in keyset:
            if len(kwargs[key]) == 0:
                kwargs[key] = ['']
    
    return kwargs, content_dict

def build_testrecords(database, calculation, content_dict, **kwargs):

    # Start calculation_dict with all singularkeys
    calculation_dict = {}
    calculation_dict['script'] = 'calc_' + calculation.style
    for key in calculation.singularkeys:
        calculation_dict[key] = kwargs[key]

    new_records = []
    new_record_df = []
    new_inputfiles = []
    copy_contents = []
    
    # Iterate over multidict combinations
    for subdict in itermultidict(calculation.multikeys, **kwargs):
        calculation_dict.update(subdict)
        
        # Generate inputfile
        inputfile = filltemplate(calculation.template, calculation_dict, '<', '>')

        # Create calc_key
        calc_key = str(uuid.uuid4())

        # Build input_dict from calculation_dict
        input_dict = {}
        copy_content = []
        for key in calculation_dict:
            if calculation_dict[key] != '':
                input_dict[key] = deepcopy(calculation_dict[key])

                if key[-8:] == '_content':
                    copy_content.append(calculation_dict[key])
                    terms = calculation_dict[key].split()

                    if terms[0] == 'record':
                        record_name = terms[1]
                        try:
                            input_dict[key] = content_dict[record_name].json()
                        except:
                            crecord = database.get_record(name=record_name)
                            input_dict[key] = crecord.content.json()
                            content_dict[record_name] = crecord.content
        
        # Build incomplete record
        #try:
        calculation.process_input(input_dict, calc_key, build=False)
        #except:
        #    continue
        
        new_record = load_record(style=calculation.record_style, name=calc_key)
        new_record.buildcontent(input_dict)

        # Check if record is valid
        if new_record.isvalid():
            new_records.append(new_record)
            new_record_df.append(new_record.todict(full=False, flat=True))
            new_inputfiles.append(inputfile)
            copy_contents.append(copy_content)
            
    new_record_df = pd.DataFrame(new_record_df)
    
    return new_records, new_record_df, new_inputfiles, copy_contents, content_dict

def itermultidict(multikeys, **kwargs):
    """
    Generates each combination of kwargs by iterating over 
    multikeys sets.
    """
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
    """
    Returns a new dict containing terms in both dict1 and dict2
    """
    newdict = dict1.copy()
    newdict.update(dict2)
    return newdict

def new_calculations(old, test, dterms, fterms):
    old_count = len(old)
    allrecords = pd.concat([old, test], ignore_index=True)
    
    if 'a_mult' in dterms:
        allrecords['a_mult'] = allrecords.a_mult2 - allrecords.a_mult1
    if 'b_mult' in dterms:
        allrecords['b_mult'] = allrecords.b_mult2 - allrecords.b_mult1
    if 'c_mult' in dterms:
        allrecords['c_mult'] = allrecords.c_mult2 - allrecords.c_mult1
    
    isdup = am.tools.duplicates_allclose(allrecords, dterms, fterms)
    
    isnew = ~isdup[old_count:].values
    return test[isnew]