# coding: utf-8
# Standard Python libraries
from pathlib import Path
import shutil

from tqdm import tqdm

import pandas as pd

import atomman as am

# iprPy imports
from .prepare import prepare
from .runner import runner, RunManager
from .master_prepare import master_prepare
from .reset_orphans import reset_orphans
from .. import load_run_directory
from ..tools import iaslist

class IprPyDatabase():
    """
    Provides methods to extend the yabadaba.Database classes to support
    iprPy calculation record actions.
    """

    @property
    def potdb(self):
        """atomman.library.Database : A library database based on the current object"""
        try:
            return self.__potdb
        except AttributeError:
            self.build_potdb()
            return self.__potdb

    def build_potdb(self, remote=None, remote_name=None, remote_database=None,
                    remote_style=None, remote_host=None, remote_terms=None, 
                    kim_models=None, kim_api_directory=None, kim_models_file=None):
        """
        Creates potdb, an atomman.library.Database with the local_database
        value set to the current object.  Allows for reference records to be
        retrieved using the atomman/potentials get methods.

        Parameters
        ----------
        remote : bool, optional
            Indicates if the load operations will check for remote records.
            Default value is controlled by settings.  If False, then the remote
            interactions will not be set.
        remote_name : str, optional
            The name assigned to a pre-defined database to use for the remote
            interactions.  Cannot be given with remote_style, remote_host or
            remote_terms.
        remote_database : yabadaba.Database
            A pre-existing Database object to use for the remote.
        remote_style : str, optional
            The database style to use for the remote interactions.
        remote_host : str, optional
            The URL/file path where the remote database is hosted.
        remote_terms : dict, optional
            Any other keyword parameters defining necessary access/settings
            information for using the remote database.  Allowed keywords are
            database style-specific.
        kim_models : str or list, optional
            Allows for the list of installed_kim_models to be explicitly given.
            Cannot be given with the other kim parameters.
        kim_api_directory : path-like object, optional
            The directory containing the kim api to use to build the list.
            Cannot be given with the other kim parameters.
        kim_models_file : path-like object, optional
            The path to a whitespace-delimited file listing full kim ids.
            Cannot be given with the other kim parameters.

        """
        self.__potdb = am.library.Database(local=True, local_database=self,
                                           remote=remote, remote_name=remote_name,
                                           remote_database=remote_database,
                                           remote_style=remote_style,
                                           remote_host=remote_host,
                                           remote_terms=remote_terms,
                                           kim_models=kim_models,
                                           kim_api_directory=kim_api_directory,
                                           kim_models_file=kim_models_file)

    def check_records(self, record_style=None):
        """
        Counts the number of records of a given style in the database.  If the
        records are calculation records, then it will also list the number of
        calculations with each status value.
        
        Parameters
        ----------
        record_style : str, optional
            The record style to check on.  If not given, then the available record
            styles will be listed and the user prompted to pick one.
        """
        if record_style is None:
            record_style = self.select_record_style()
        
        if record_style is not None:
            
            # Always refresh local calculation records
            if self.style == 'local' and record_style[:12] == 'calculation_':
                kwargs = {'refresh_cache': True}
            else:
                kwargs = {}

            # Display information about database records
            df = self.get_records_df(style=record_style, **kwargs) 
            print(f'In {self}:')
            print(f'- {len(df)} of style {record_style}', flush=True)
            
            # Count status values of calculations
            if 'status' in df:
                print(f" - {len(df[df.status=='finished'])} finished")
                print(f" - {len(df[df.status=='not calculated'])} not finished")
                print(f" - {len(df[df.status=='error'])} issued errors")

    def clean_records(self, run_directory, record_style=None, records=None):
        """
        Resets all records of a given style that issued errors. Useful if the
        errors are due to external conditions.
        
        Parameters
        ----------
        run_directory : str
            The directory where the cleaned calculation instances are to be
            returned.
        record_style : str, optional
            The record style to clean.  If not given, then the available record
            styles will be listed and the user prompted to pick one.
        records : list, optional
            A list of Record objects from the database to clean.  Allows
            the user full control on which records to reset.  Cannot be given
            with record_style.
        """
        # Check for run_directory first by name then by path
        try:
            run_directory = load_run_directory(run_directory)
        except:
            run_directory = Path(run_directory).resolve()
            if not run_directory.is_dir():
                raise ValueError('run_directory not found/set')

        # Select record_style if needed
        if record_style is None and records is None:
            record_style = self.select_record_style()

        # Get records by record_style
        if record_style is not None:
            if records is not None:
                raise ValueError('record_style and records cannot both be given')
            
            # Always refresh local calculation records
            if self.style == 'local' and record_style[:12] == 'calculation_':
                kwargs = {'refresh_cache': True}
            else:
                kwargs = {}

            # Retrieve records with errors from self
            records = self.get_records(style=record_style, status='error', **kwargs) 
        
        elif records is None:
            # Set empty list if record_style is still None and no records given
            records = []
        
        print(len(records), 'records to clean')
        
        # Loop over all error records
        for record in records:

            # Check if record has saved tar
            try:
                tar = self.get_tar(record=record)
            except:
                print(f'failed to extract {record.name} tar')
            else:
                # Copy tar back to run_directory
                try:
                    tar.extractall(run_directory)
                except:
                    print(f'failed to extract {record.name} tar')
                    tar.close()
                else:
                    # Delete database version of tar
                    tar.close()
                    try:
                        self.delete_tar(record=record)
                    except:
                        print(f'failed to delete {record.name} tar')
            
            # Clean record and update in the database
            record.clean()
            try:
                record.build_model()
            except:
                print('failed to update', record.name)
            else:
                self.update_record(record=record)
        
        # Remove bid files
        for bidfile in run_directory.glob('*/*.bid'):
            bidfile.unlink()
        
        # Remove results.json files
        for resultsfile in run_directory.glob('*/results.json'):
            resultsfile.unlink()

    def finish_calculations(self, run_directory, verbose=False):
        """
        Checks a run directory for calculations that have competed running and
        moves them to the database by adding/updating the records and archiving
        the calculation folder. Allows for calculations to be ran in isolation,
        or to clean up completed calculations if a connection to a remote
        database is lost.

        Parameters
        ----------
        run_directory : str
            The directory to search for completed calculations.
        verbose : bool, optional
            If True, print statements will list the records successfully
            added/updated to the database.  Default value is False.        
        """
        # Check for run_directory first by name then by path
        try:
            run_directory = load_run_directory(run_directory)
        except:
            run_directory = Path(run_directory).resolve()
            if not run_directory.is_dir():
                raise ValueError('run_directory not found/set')

        for calc in Path(run_directory).glob('*'):

            # Check that the path is a directory
            if not calc.is_dir():
                continue

            # Check if calc is finished
            record_file = Path(calc, 'results.json')
            if not record_file.is_file():
                continue

            # Check that the calc input script exists and get the style
            infiles = [i for i in calc.glob('calc_*.in')]
            if len(infiles) == 1:
                infile = infiles[0]
                style = infile.stem.replace('calc_', 'calculation_')
            else:
                continue

            # Add record and tar
            name = calc.name
            try:
                self.add_record(name=name, style=style, model=record_file, verbose=verbose)
            except:
                self.update_record(name=name, style=style, model=record_file, verbose=verbose)
            try:
                self.add_tar(name=name, style=style, root_dir=run_directory)
            except:
                self.update_tar(name=name, style=style, root_dir=run_directory)

            # Delete calc folder
            shutil.rmtree(calc)

    def finish_bad_calculations(self, run_directory, error_message, records=None,
                                verbose=False):
        """
        Finishes calculations in a run directory by setting their status to "error",
        and uploading both the record and calculation tar to the database.  

        Parameters
        ----------
        run_directory : str
            The directory to search for calculations.
        error_message : str
            The error message to assign to the calculations.
        records : str, Record, list or None, optional
            Record(s) or record name(s) to finish in this way.  If None (default)
            then all calculations found in the run directory will be finished
            with the error status and message.
        verbose : bool, optional
            If True, print statements will list the records successfully
            added/updated to the database.  Default value is False.        
        """
        # Check for run_directory first by name then by path
        try:
            run_directory = load_run_directory(run_directory)
        except:
            run_directory = Path(run_directory).resolve()
            if not run_directory.is_dir():
                raise ValueError('run_directory not found/set')

        # Get list of record names
        names = []
        if records is not None:
            for record in iaslist(records):
                if isinstance(record, str):
                    names.append(record)
                else:
                    names.append(record.name)

        for calc in Path(run_directory).glob('*'):
            
            # Check that the path is a directory
            if not calc.is_dir():
                continue

            # Check if calculation is in the listed records to finish
            calc_name = calc.name
            if records is not None and calc_name not in names:
                continue

            # Check if the calc input script exists to get the style
            infiles = [i for i in calc.glob('calc_*.in')]
            if len(infiles) == 1:
                infile = infiles[0]
                style = infile.stem.replace('calc_', 'calculation_')
            else:
                style = None

            # Load content
            record = self.get_record(name=calc_name, style=style)
            model = record.model
            
            # Update status and error fields
            root = record.modelroot
            model[root]['status'] = 'error'
            model[root]['error'] = error_message
            
            # Save to calc directory
            with open(Path(calc, 'results.json'), 'w', encoding='utf-8') as f:
                model.json(fp=f, indent=4, ensure_ascii=False)
                
            # Update record
            self.update_record(record=record, verbose=verbose)

            try:
                self.add_tar(record=record, root_dir=run_directory)
            except:
                self.update_tar(record=record, root_dir=run_directory)
            
            # Delete calc folder
            shutil.rmtree(calc)

    def reset_orphans(self, run_directory, orphan_directory=None):
        """
        Resets calculations that were moved to an orphan directory back to a
        run directory and removes any bid files that they contain.  Can be useful
        if connection is lost to a remote database or a runner was accidentally
        started with the wrong database. This is identical to calling
        iprPy.reset_orphans and is only a class method for consistency with other
        workflow operations.

        Parameters
        ----------
        run_directory : str
            The directory to move the orphaned calculations to.
        orphan_directory : str, optional
            The orphan directory containing archived calculation folders.  The
            default value assumes that the orphan directory is a directory named
            "orphan" that is in the same parent directory as run_directory, i.e.
            is at "../orphan" relative to run_directory.
        """
        reset_orphans(run_directory, orphan_directory=orphan_directory)

    def merge_records(self, dest, record_style, includetar=True, overwrite=False,
                      dryrun=False, **kwargs):
        """
        Copies records from the current database to another database by first comparing
        the records in the two databases to identify missing (and changed) content.  
        
        Parameters
        ----------
        dest :  Database
            The destination database to copy records to.
        record_style : str
            The record style to compare existing records between the two
            databases and copy missing/updated records to dest. 
        includetar : bool, optional
            If True, the tar archives will be copied along with the records,
            and missing tars will also be searched for.
            If False, only the records will be copied. (Default is True).
        overwrite : bool, optional
            If False (default) only new records and tars will be copied.
            If True, the content of all records will be compared to identify
            those that have been changed, and those will be updated in dest
            to match the content in the current database.
        dryrun : bool, optional
            If True, the identified records to add/update to dest will be
            returned as a list rather than sending them to dest. copy_records()
            can then be called afterwards using the list of records.
            If False (default), copy_records will automatically be called and
            the list not returned.
        **kwargs : any, optional
            Any query keyword options to use when building the lists of existing
            calculations to compare. NOTE these are only applied to get_records
            calls at the moment and so should not be combined with includetar!!!
            
        Returns
        -------
        list
            The records identified to add/update from the current database to
            dest.  Only returned if dryrun is True.
        """
        
        # Get records in source database
        self_records, self_df = self.get_records(record_style, return_df=True, **kwargs)
        print(len(self_records), 'records in source')
        
        # Get records in destination database
        dest_records, dest_df = dest.get_records(record_style, return_df=True, **kwargs)
        print(len(dest_records), 'records in destination')
        
        # Identify records missing from destination
        if len(dest_records) > 0:
            missing = set(self_df.name[~self_df.name.isin(dest_df.name.tolist())])
        else:
            missing = set(self_df.name)
        print(len(missing), 'records missing from destination')
        
        if overwrite is True:
            print('comparing content of records')
            # Identify records that have changed
            changed = []
            for name in tqdm(self_df.name[~self_df.name.isin(missing)], desc="Comparing records", ascii=True):
                self_record = self_records[self_df.name == name][0].model.json(ensure_ascii=False)
                dest_record = dest_records[dest_df.name == name][0].model.json(ensure_ascii=False)
                if self_record != dest_record:
                    changed.append(name)
            print(len(changed), 'records in destination different in source')
            missing = missing.union(changed)
        
        if includetar is True:
            
            # Get metadata for tars in source database
            self_tar = []
            for frecord in self.mongodb[f'{record_style}.files'].find():
                self_tar.append(frecord)
            self_tar = pd.DataFrame(self_tar)
            print(len(self_tar), 'tars in source')
            
            # Get metadata for tars in destination database
            dest_tar = []
            for frecord in dest.mongodb[f'{record_style}.files'].find():
                dest_tar.append(frecord)
            dest_tar = pd.DataFrame(dest_tar)
            print(len(dest_tar), 'tars in destination')   
            
            # Identify records missing from destination
            if len(dest_records) > 0:
                missingtar = set(self_tar.recordname[~self_tar.recordname.isin(dest_tar.recordname.tolist())])
            else:
                missingtar = set(self_tar.recordname)
            print(len(missingtar), 'tars missing from destination')
            missing = missing.union(missingtar)
        
        if len(missing) > 0:
            records = self_records[self_df.name.isin(missing)]
            if dryrun:
                print(len(records), 'to copy')
            else:
                self.copy_records(dest, records=records, includetar=includetar, overwrite=overwrite)
            return records
        else:
            print('No records to copy')
            return []
        
    def copy_references(self, dest, includetar=True, overwrite=False):
        """
        Copies all reference record styles from the current database to
        another database.

        Parameters
        ----------
        dest : Database
            The destination database to copy the reference records to.
        includetar : bool, optional
            If True, the tar archives will be copied along with the records.
            If False, only the records will be copied. (Default is True).
        overwrite : bool, optional
            If False (default) only new records and tars will be copied.
            If True, all existing content will be updated.
        """
        refstyles = [
            'potential_LAMMPS',
            'potential_LAMMPS_KIM',
            'crystal_prototype',
            'reference_crystal',
            #'relaxed_crystal',
            'free_surface',
            'stacking_fault',
            'point_defect',
            'dislocation',
        ]
        for style in iaslist(refstyles):
            print(style)
            self.copy_records(dest, record_style=style, includetar=includetar, overwrite=overwrite)

    def get_parent_records(self, record=None, name=None, style=None,
                           ancestors=False):
        """
        Returns all records that are parents to the given one.

        Parameters
        ----------
        record : iprPy.Record, optional
            The record whose parents are to be found.
        name : str, optional
            Record name for identifying a record to load and check for parents.
            Cannot be given with record. 
        style : str, optional
            Record style associated with the record identified by name.
            Cannot be given with record. 
        ancestors : bool, optional
            If True, then the identified parents will be recursively searched to
            identify all ancestors of the current record.  Default value is False,
            meaning that only direct parents are returned.

        Returns
        -------
        list of iprPy.Record
            All the parent records 
        """
        # Get child record if needed
        if record is None:
            record = self.get_record(name=name, style=style) 
        elif name is not None or style is not None:
            raise ValueError('record cannot be given with name/style')
        
        parents = []
        try:
            # Check if record has system-info
            model = record.build_model().find('system-info')
        except:
            pass
        else:
            # Loop over all file values in system-info
            for load_file in model.finds('file'):
                
                # See if load file is in a directory
                directory = Path(load_file).parent.stem
                if directory != '':
                    # Set parentname as load_file's directory
                    parentname = directory
                else:
                    # Set parentname as loadfile's name
                    parentname = Path(load_file).stem

                try:
                    # Get parent record
                    parent = self.get_record(name=parentname) 
                except:
                    pass
                else:
                    parents.append(parent)

                    # Recursively check for ancestors
                    if ancestors is True:
                        grandparents = self.get_parent_records(record=parent)
                        parents.extend(grandparents)
        
        return parents

    def prepare(self, run_directory, calculation, input_script=None, debug=False,
                content_dict = None,
                calc_df = None,
                **kwargs):
        """
        Function for preparing any iprPy calculation for high-throughput execution.
        Input parameters for preparing can either be given within an input script
        or by passing in keyword parameters.
        
        Parameters
        ----------
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
        **kwargs : str or list
            Allows for input parameters for preparing the calculation to be
            directly specified.  Any kwargs parameters that have names matching
            input_script parameters will overwrite the input_script values.
            Values must be strings or list of strings if allowed by the
            calculation for the particular parameter.
        """
        
        # Call prepare with self as database
        return prepare(self, run_directory, calculation, input_script=input_script,
                       debug=debug, content_dict=content_dict, calc_df=calc_df, **kwargs)
    
    def master_prepare(self, input_script=None, debug=False, **kwargs):
        """
        Prepares one or more calculations according to the workflows used by the
        NIST Interatomic Potentials Repository.
        
        Parameters
        ----------
        database : iprPy.database.Database
            The database that will host the records for the prepared calculations.
        input_script : str or file-like object, optional
            The file, path to file, or contents of an input script containing
            parameters for preparing the calculation.
        **kwargs : str or list
            Allows for input parameters for preparing the calculation to be
            directly specified.  Any kwargs parameters that have names matching
            input_script parameters will overwrite the input_script values.
            Values must be strings or list of strings if allowed by the
            calculation for the particular parameter.
        """
        # Call master_prepare with self as database
        return master_prepare(self, input_script=input_script, debug=debug, **kwargs)

    def runner(self, run_directory, calc_name=None, orphan_directory=None,
               hold_directory=None, log=False, bidtries=10, bidverbose=False,
               temp=False, temp_directory=None, free=False, kwargs_calc={}):
        """
        High-throughput calculation runner.
        
        Parameters
        ----------
        run_directory : path-like object or str
            The run_directory name or path to the directory where the calculations
            to run are located.
        calc_name : str, optional
            The name of a specific calculation to run.  If not given, all
            calculations in run_directory will be performed one at a time.
        orphan_directory : path-like object, optional
            The path for the orphan directory where incomplete calculations are
            moved.  If None (default) then will use 'orphan' at the same level as
            the run_directory.
        hold_directory : str, optional
            The path for the hold directory where tar archives that failed to be
            uploaded are moved to.  If None (default) then will use 'hold' at the
            same level as the run_directory.
        log : bool, optional
            If True, the runner will create and save a log file detailing the
            status of each calculation that it runs.
        bidtries : int, optional
            The runner will stop if it fails on bidding this many times in a
            row.  This allows for the cleanup of excess competing runners.
            Default value is 10.
        bidverbose : bool, optional
            If True, info about the calculation bidding process will be printed.
            Default value is False.
        temp : bool, optional
            If True, a temporary directory will be automatically created and used
            for this run.
        temp_directory : path-like object, optional
            The path to an existing temporary directory where the calculations
            are to be copied to and executed there instead of in the run_directory.
        free : bool, optional
            Setting this to True indicates that the calculations should be ran
            without interfacing with the database.  This allows for runners to
            work even when the associated database is inaccessible.  Finished
            calculations can be uploaded later using "finish_calculations".
        kwargs_calc : dict, optional
            Keyword arguments for :meth:`iprPy.calculation.Calculation.Calculation.run`.
            Default is ``{"results_json": True}``
        
        """
        # Call runner with self as database
        runner(self, run_directory, calc_name=calc_name,
               orphan_directory=orphan_directory, hold_directory=hold_directory,
               log=log, bidtries=bidtries, bidverbose=bidverbose,
               temp=temp, temp_directory=temp_directory, free=free,
               kwargs_calc=kwargs_calc)

    def runmanager(self, run_directory, orphan_directory=None,
                    hold_directory=None, log=False):
        """
        Creates a RunManager object linked to the database.  This allows users
        more control on how to perform calculations by being able to directly
        call the RunManager's run and runall methods.

        Parameters
        ----------
        run_directory : path-like object or str
            The run_directory name or path to the directory where the calculations
            to run are located.
        orphan_directory : str, optional
            The path for the orphan directory where incomplete calculations are
            moved.  If None (default) then will use 'orphan' at the same level as
            the run_directory.
        hold_directory : str, optional
            The path for the hold directory where tar archives that failed to be
            uploaded are moved to.  If None (default) then will use 'hold' at the
            same level as the run_directory.
        log : bool, optional
            If True, the runner will create and save a log file detailing the
            status of each calculation that it runs.
        """
        return RunManager(self, run_directory, orphan_directory=orphan_directory,
                          hold_directory=hold_directory, log=log)