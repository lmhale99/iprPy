# coding: utf-8
# Standard Python libraries
from pathlib import Path
from copy import deepcopy
import shutil
from typing import Optional, Union

from tqdm import tqdm

import atomman as am

import numpy as np

import pandas as pd

# iprPy imports
from ..tools import aslist, filltemplate
from .. import load_calculation, load_run_directory
from ..input import buildcombos, parse

def prepare(database,
            run_directory: str,
            calculation,
            input_script: Optional[Union[Path, str]] = None,
            debug: bool = False,
            content_dict: Optional[dict] = None,
            calc_df: Optional[pd.DataFrame] = None,
            **kwargs):
    """
    Function for preparing any iprPy calculation for high-throughput execution.
    Input parameters for preparing can either be given within an input script
    or by passing in keyword parameters.
    
    Parameters
    ----------
    database : iprPy.database.Database
        The database that will host the records for the prepared calculations.
    run_directory : str
        The path or name for the run_directory where the prepared calculations
        are to be placed.
    calculation : iprPy.calculation.Calculation or str
        The calculation style or an instance of the calculation style to prepare.
    input_script : str or file-like object, optional
        The file, path to file, or contents of an input script containing
        parameters for preparing the calculation.
    debug : bool
        If set to True, will throw errors associated with failed/invalid
        calculation builds.  Default is False.
    content_dict : dict, optional
        Option for advanced prepare control.  When preparing based on database
        records, a content_dict is used to store the record contents so
        metadata can be built from it before the file is copied into the
        prepared calculation folders.  Prepare is designed to automatically
        fetch the records from the database and extract the contents, but this
        parameter allows for the contents to be manually specified instead.
        Keys should be the record names and values the record model contents as
        DataModelDict objects.
    calc_df : pandas.DataFrame, optional
        Option for advanced prepare control.  The metadata DataFrame of
        pre-existing calculations to use for filtering out duplicates from the
        newly proposed combinations.  If not given, database.get_records_df()
        is called to get the metadata for all existing records of the given
        calculation style.  Being able to manually specify calc_df can reduce
        how long prepare takes by reducing the number of times get_records_df
        is called or providing filtering keywords to reduce the number of
        records returned by get_records_df.  CAUTION: Extra care is required
        with using calc_df as it makes it easier to accidentally prepare
        duplicate calculations!        
    **kwargs : str or list
        Allows for input parameters for preparing the calculation to be
        directly specified.  Any kwargs parameters that have names matching
        input_script parameters will overwrite the input_script values.
        Values must be strings or list of strings if allowed by the
        calculation for the particular parameter.
    """
    # Handle calculation
    if isinstance(calculation, str):
        calculation = load_calculation(calculation)
    dbwargs = {}
    if database.style == 'local':
        dbwargs['refresh_cache'] = True

    # Handle run_directory 
    try:
        run_directory = load_run_directory(run_directory)
    except:
        run_directory = Path(run_directory)
    if not run_directory.is_absolute():
        run_directory = Path(Path.cwd(), run_directory)
    run_directory.resolve()
    if not run_directory.exists():
        raise ValueError(f"Directory, {run_directory}, not found.")

    # Parse input_script
    if input_script is not None:
        temp = kwargs
        kwargs = parse(input_script, singularkeys=calculation.singularkeys)
        for key in temp:
            kwargs[key] = temp[key]
    
    # Build dataframe of all existing records for the calculation style
    if calc_df is None:
        old_calcs_df = database.get_records_df(style=calculation.style, **dbwargs)
        print(len(old_calcs_df), 'existing calculation records found', flush=True)
    else:
        old_calcs_df = calc_df
        print(len(old_calcs_df), 'existing calculation records provided', flush=True)
    
    # Build content_dict for manually defined "*_content record" fields
    content_dict = manual_content_dict(database, content_dict, **kwargs)

    # Complete kwargs with default values and buildcombos actions
    kwargs, content_dict = fill_kwargs(database, calculation, content_dict, **kwargs)

    # Build all combinations
    test_calcs, test_calcs_df, test_inputfiles, test_contents, content_dict = build_test_calcs(database, calculation, content_dict, debug=debug, **kwargs)
    print(len(test_calcs_df), 'calculation combinations to check', flush=True)
    if len(test_calcs_df) == 0:
        return

    # Find new unique combinations
    new_calcs_df = new_calculations(old_calcs_df, test_calcs_df,
                                    calculation.compare_terms,
                                    calculation.compare_fterms)
    print(len(new_calcs_df), 'new records to prepare', flush=True)

    # Iterate over new calculations and prepare
    for i in tqdm(new_calcs_df.index, 'preparing', ascii=True):
        new_calc = test_calcs[i]
        inputfile = test_inputfiles[i]
        copy_content = test_contents[i]
        
        prepare_calc(database, run_directory, new_calc, inputfile,
                     copy_content, content_dict)

def manual_content_dict(database,
                        content_dict: Optional[dict] = None,
                        **kwargs):
    """
    Checks kwargs for manually defined "*_content record" fields and retrieves
    the associated record contents from database and stores them in
    content_dict.

    Parameters
    ----------
    database : iprPy.database.Database
        The database to use for fetching record contents.
    content_dict : dict or None, optional
        The content_dict manually given to prepare(). If None, then a new
        empty dict will be created.
    **kwargs : dict
        Input parameters for preparing the calculation.

    Returns
    -------
    content_dict : dict
        Keys are the file name and values are the associated loaded file
        contents for extra input files needed for the calculations.
    """
    # Initialize content_dict if needed
    if content_dict is None:
        content_dict = {}

    # Loop over all *_content record fields
    for key in kwargs:
        if '_content' in key:

            # Loop over "*_content record" values
            for entry in aslist(kwargs[key]):
                terms = entry.split()
                if terms[0] != 'record':
                    continue
                
                # Check if already in content_dict
                name = terms[1]
                if name in content_dict:
                    continue

                # Retrieve record style if included
                if len(terms) == 3:
                    style = terms[2]
                else:
                    style = None

                # Get record contents
                record = database.get_record(style=style, name=name)
                content_dict[name] = record.model

    return content_dict
    
def fill_kwargs(database, calculation, content_dict, **kwargs):
    """
    Fills in kwargs with default values and buildcombos results.
    
    Parameters
    ----------
    database : iprPy.database.Database
        The database to use for building combos.
    calculation : iprPy.calculation.Calculation
        An instance of the calculation being prepared.
    content_dict : dict
        The content_dict created from the manually provided values to prepare
        and any manually defined "*_content record" fields.
    **kwargs : dict
        Input parameters for preparing the calculation.
        
    Returns
    -------
    kwargs : dict
        The full, updated input parameters.
    content_dict : dict
        Keys are the file name and values are the associated loaded file
        contents for extra input files needed for the calculations.
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
                        raise ValueError(f'Incompatible multikey lengths len({key}) != {length}')
    
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

def build_test_calcs(database, calculation, content_dict, debug=False, 
                     **kwargs):
    """
    Builds calculations based on iterating over the sets of kwargs values.
    
    Parameters
    ----------
    database : iprPy.database.Database
        Here, the database is used to fetch parent records when needed.
    calculation : iprPy.calculation.Calculation
        An instance of the calculation style being prepared.
    content_dict : dict
        Keys are the file name and values are the associated loaded file
        contents for extra input files needed for the calculations.
    debug : bool
        If set to True, will throw errors associated with failed/invalid
        calculation builds.  Default is False.
    **kwargs : dict
        The full input parameters to use for preparing the calculations.
        
    Returns
    -------
    test_calcs : numpy.NDArray
        The list of built calculations.
    test_calcs_df : pandas.DataFrame
        A table of the metadata associated with the test_calcs.
    test_inputfiles : list
        The calculation input files associated with the test_calcs.
    test_contents : list
        A list of the "content" input parameters used when building the
        calcuations.  The content parameters allow for 
    content_dict : dic
        The content_dict with parent records added in.
    """

    # Start calculation_dict with all singularkeys
    calculation_dict = {}
    for key in calculation.singularkeys:
        calculation_dict[key] = kwargs[key]

    test_calcs = []
    test_calcs_df = []
    test_inputfiles = []
    test_contents = []
    numinvalid = 0

    # Iterate over multidict combinations
    for subdict in itermultidict(calculation.multikeys, **kwargs):
        calculation_dict.update(subdict)
        
        # Generate inputfile
        test_inputfile = filltemplate(calculation.template, calculation_dict, '<', '>')
        
        # Build input_dict from calculation_dict
        input_dict = {}
        test_content = []
        for key in calculation_dict:
            if calculation_dict[key] != '':
                input_dict[key] = deepcopy(calculation_dict[key])

                if key[-8:] == '_content':
                    test_content.append(calculation_dict[key])
                    terms = calculation_dict[key].split()

                    if terms[0] == 'record':
                        record_name = terms[1]
                        try:
                            input_dict[key] = content_dict[record_name].json()
                        except:
                            crecord = database.get_record(name=record_name)
                            input_dict[key] = crecord.build_model().json() 
                            content_dict[record_name] = crecord.build_model()
        if debug is False:
            try:
                # Build test calculation and check if valid
                test_calc = load_calculation(calculation.calc_style, params=input_dict)
                assert test_calc.isvalid()
            except:
                numinvalid += 1
            else:
                # Add test calculation data to lists
                test_calcs.append(test_calc)
                test_calcs_df.append(test_calc.metadata())
                test_inputfiles.append(test_inputfile)
                test_contents.append(test_content)
        else:
            
            # Build test calculation and check if valid
            test_calc = load_calculation(calculation.calc_style, params=input_dict)
            assert test_calc.isvalid()
            
            # Add test calculation data to lists
            test_calcs.append(test_calc)
            test_calcs_df.append(test_calc.metadata())
            test_inputfiles.append(test_inputfile)
            test_contents.append(test_content)
    
    if numinvalid >= 1:
        print(numinvalid, 'invalid calculations skipped')
            
    test_calcs_df = pd.DataFrame(test_calcs_df)
    
    return test_calcs, test_calcs_df, test_inputfiles, test_contents, content_dict

def itermultidict(multikeys, **kwargs):
    """
    Generates each combination of kwargs by iterating over multikeys sets.
    
    Parameters
    ----------
    multikeys : list
        The key sets that should be iterated over together.
    **kwargs : dict
        The calculation input parameter terms as given.
        
    Yields
    ------
    dict
        A combination of individual kwargs values.
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
    """Returns a new dict containing terms in both dict1 and dict2"""
    newdict = dict1.copy()
    newdict.update(dict2)
    return newdict

def new_calculations(old, test, dterms, fterms):
    """
    Identifies which test calculations are new by comparing metadata field
    values
    
    Parameters
    ----------
    old : pandas.DataFrame
        The metadata of existing calculations.
    test :pandas.DataFrame
        The metadata of calculation combinations to check.
    dterms : list
        The names of metadata fields to directly compare.
    fterms : dict
        The names and tolerances to use for comparing float metadata fields.
        
    Returns
    -------
    pandas.DataFrame
        The rows of test that are unique when compared with old and later rows
        in test. 
    """
    old_count = len(old)
    allrecords = pd.concat([old, test], ignore_index=True)
    
    # Check direction-independent mult terms
    if 'a_mult' in dterms:
        allrecords['a_mult'] = allrecords.a_mult2 - allrecords.a_mult1
    if 'b_mult' in dterms:
        allrecords['b_mult'] = allrecords.b_mult2 - allrecords.b_mult1
    if 'c_mult' in dterms:
        allrecords['c_mult'] = allrecords.c_mult2 - allrecords.c_mult1
    
    try:
        isdup = am.tools.duplicates_allclose(allrecords, dterms, fterms)
    except:
        return test
    else:
        isnew = ~isdup[old_count:].values
        return test[isnew]

def prepare_calc(database, run_directory, new_calc, inputfile, copy_content, content_dict):
    """
    Prepares a single calculation by building the calculation folder and adding
    a record to the database.
    
    Parameters
    ----------
    database : iprPy.database.Database
        The database where records for the prepared calculations are added.
    run_directory : str or path-like object
        The path to the local run_directory where the prepared calculations
        are to be placed.
    new_calc : iprPy.calculation.Calculation
        The new calculation to prepare.
    inputfile : str
        The contents of the input file associated with new_calc.
    copy_content : list
        The list of extra input files to copy for new_calc.
    content_dict : dict
        Keys are the file name and values are the associated loaded file
        contents for extra input files needed for the calculations.
    """
    
    # Generate calculation folder
    calc_directory = Path(run_directory, new_calc.name)
    if not calc_directory.is_dir():
        calc_directory.mkdir(parents=True)

    # Save inputfile to calculation folder
    with open(Path(calc_directory, f'calc_{new_calc.calc_style}.in'), 'w', encoding='UTF-8') as f:
        f.write(inputfile)

    # Copy/generate content files keys
    for content in copy_content:
        terms = content.split()

        if terms[0] == 'record':
            record_name = terms[1]
            record_file = Path(calc_directory, f'{record_name}.json')
            with open(record_file, 'w') as f:
                content_dict[record_name].json(fp=f, indent=4)

        elif terms[0] == 'tarfile':
            try:
                tar = database.get_tar(name=terms[1])
            except:
                print(f'No tar for {terms[1]} found')
            else:
                file_name = f'{terms[1]}/{" ".join(terms[2:])}'
                tar.extract(file_name, calc_directory)
                tar.close()

        elif terms[0] == 'tar':
            try:
                tar = database.get_tar(name=terms[1])
            except:
                try:
                    dirpath = database.get_folder(name=terms[1])
                except:
                    print(f'No tar for {terms[1]} found')
                else:
                    shutil.copytree(dirpath, Path(calc_directory, dirpath.name))
            else:
                tar.extractall(calc_directory)
                tar.close()

    # Add record to database
    database.add_record(record=new_calc)