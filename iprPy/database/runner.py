# coding: utf-8
# Standard Python libraries
import os
import sys
from pathlib import Path
import subprocess
import random
import shutil
import time
import tempfile
import datetime
import requests

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Settings, load_run_directory

def runner(database, run_directory, calc_name=None, orphan_directory=None,
           hold_directory=None, python_exe=None, log=True,
           bidtries=10, temp=False, temp_directory=None):
    """
    High-throughput calculation runner.
    
    Parameters
    ----------
    database : iprPy.Database
        The database to interact with.
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
    python_exe : str, optional
        The Python executable to use when running the calculations.  If not given,
        will try to use the current Python executable, and if not available will use
        'python'.
    log : bool, optional
        If True (default), the runner will create and save a log file detailing the
        status of each calculation that it runs.
    bidtries : int, optional
        The runner will stop if it fails on bidding this many times in a
        row.  This allows for the cleanup of excess competing runners.
        Default value is 10.
    temp : bool, optional
        If True, a temporary directory will be automatically created and used
        for this run.
    temp_directory : path-like object, optional
        The path to an existing temporary directory where the calculations
        are to be copied to and executed there instead of in the run_directory.
    
    """
    # Initialize a RunManager
    runmanager = RunManager(database, run_directory,
                             orphan_directory=orphan_directory,
                             hold_directory=hold_directory,
                             python_exe=python_exe, log=log)
    
    # Run all calculations
    if calc_name is None:
        print(f'Runner started with pid {runmanager.pid}', flush=True)
        runmanager.runall(bidtries=bidtries, temp=temp,
                           temp_directory=temp_directory)
    
    else:
        print(f'Runner operating on {calc_name} with pid {runmanager.pid}')
        status = runmanager.run(calc_name=calc_name, temp=temp,
                                 temp_directory=temp_directory)
        print(status)

class RunManager():
    """
    Manages the execution of iprPy calculations
    """
    
    def __init__(self, database, run_directory, orphan_directory=None,
                 hold_directory=None, python_exe=None, log=True):
        """
        Class initializer
        
        Parameters
        ----------
        database : iprPy.Database
            The database to interact with.
        run_directory : str
            The path to the directory where the calculation instances to run are
            located.
        orphan_directory : str, optional
            The path for the orphan directory where incomplete calculations are
            moved.  If None (default) then will use 'orphan' at the same level as
            the run_directory.
        hold_directory : str, optional
            The path for the hold directory where tar archives that failed to be
            uploaded are moved to.  If None (default) then will use 'hold' at the
            same level as the run_directory.
        python_exe : str, optional
            The Python executable to use when running the calculations.  If not given,
            will try to use the current Python executable, and if not available will use
            'python'.
        log : bool, optional
            If True (default), the runner will create and save a log file detailing the
            status of each calculation that it runs.
        """
        
        # Set python executable for subprocesses
        self.python_exe = python_exe
        
        # Set database
        self.__database = database
        
        # Set run_directory
        self.run_directory = run_directory
        
        # Set orphan_directory
        self.orphan_directory = orphan_directory
        
        # Set hold_directory
        self.hold_directory = hold_directory
        
        # Get pid
        self.__pid = os.getpid()
        
        # Build log file name
        if log is True:
            log_directory = Settings().runner_log_directory
            if not log_directory.is_dir():
                log_directory.mkdir(parents=True)
            self.__logfilename = Path(log_directory, f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S-%f}-{self.pid}.log')   
        else:
            self.__logfilename = None
    
    def __str__(self):
        """Class string representation"""
        string = f'Runner class operating in {self.run_directory}\n'
        string += f'for {self.database}\n'
        string += f'with pid {self.pid}'

        return string

    @property
    def python_exe(self):
        """str : The Python executable to use for the subprocess calculations."""
        return self.__python_exe
    
    @python_exe.setter
    def python_exe(self, exe):
        if exe is None:
            exe = sys.executable
            if exe is None:
                exe = 'Python'
        self.__python_exe = exe
        
    @property
    def database(self):
        """iprPy.Database : The records database for the calculations to interact with."""
        return self.__database
    
    @property
    def run_directory(self):
        """pathlib.Path : The path to the run_directory containing the calculation folders."""
        return self.__run_directory
    
    @run_directory.setter
    def run_directory(self, path):
        try:
            path = load_run_directory(path)
        except:
            path = Path(path)
        if not path.is_absolute():
            path = Path(Path.cwd(), path)
        path.resolve()
        if not path.is_dir():
            raise ValueError('run_directory not found')
        self.__run_directory = path
        
    @property
    def orphan_directory(self):
        """pathlib.Path : The directory where calculations missing .py or .in files, or database records are sent."""
        return self.__orphan_directory
    
    @orphan_directory.setter
    def orphan_directory(self, path):
        if path is None:
            path = Path(self.run_directory.parent, 'orphan')
        else:
            path = Path(path)
            if not path.is_absolute():
                path = Path(Path.cwd(), path)
        path.resolve()
        self.__orphan_directory = path
    
    @property
    def hold_directory(self):
        """pathlib.Path : The directory where calculations are sent if uploading to the database fails."""
        return self.__hold_directory
    
    @hold_directory.setter
    def hold_directory(self, path):
        if path is None:
            path = Path(self.run_directory.parent, 'hold')
        else:
            path = Path(path)
            if not path.is_absolute():
                path = Path(Path.cwd(), path)
        path.resolve()
        self.__hold_directory = path
        
    @property
    def pid(self):
        """str : The processor id for the runner."""
        return self.__pid
    
    @property
    def logfilename(self):
        """pathlib.Path : The name/path of the log file the runner save info to."""
        return self.__logfilename
    
    @property
    def calclist(self):
        """list : The current list of calculation names in the run directory."""
        calcs = []
        for calc in self.run_directory.iterdir():
            if calc.is_dir():
                calcs.append(calc.name)
        return calcs
    
    def __bid(self, calc_directory):
        """
        Bids for the chance to run a calculation. Used to help avoid
        runner collisions.

        Parameters
        ----------
        calc_directory : path-like object
            The calculation directory to bid on.

        Returns
        -------
        bool
            True if bidding is successful, False if bidding fails.
        """        
        # Wait as calc folder may be in the process of being deleted
        time.sleep(1)

        # Check if calc_directory still exists and if bids mave been made
        try:
            assert calc_directory.is_dir()
            for filename in calc_directory.iterdir():
                assert filename.suffix != '.bid'
        except:
            return False
        
        # Try to place a bid - may fail if calc_directory gets deleted
        try:
            with open(Path(calc_directory, f'{self.pid}.bid'), 'w') as f:
                f.write(f'bid for pid: {self.pid}')
        except:
            return False

        # Wait to make sure all bids are in
        time.sleep(1)

        # Build list of submitted bids
        bids = []
        try:
            for filename in calc_directory.iterdir():
                if filename.suffix == '.bid':
                    bids.append(int(filename.stem))
        except:
            return False
        
        # Competing bids go to the smallest pid
        if min(bids) == self.pid:
            return True
        else:
            return False
        
    def __removecalc(self, calc_directory):
        """
        Removes the specified calculation from the run directory leaving .bid files
        for last to help avoid runner collisions.

        Parameters
        ----------
        calc_directory : path-like object
            The calculation directory to delete.
        """
        
        # Loop over all files and directories in calc_directory
        for path in calc_directory.iterdir():

            # If path is a directory, try rmtree up to 10 times
            if path.is_dir():
                tries = 0
                while tries < 10:
                    try:
                        shutil.rmtree(path)
                        break
                    except:
                        tries += 1

            # If path is a non-.bid file, try remove up to 10 times
            elif path.is_file() and path.suffix != '.bid':
                tries = 0
                while tries < 10:
                    try:
                        path.unlink()
                        break
                    except:
                        tries += 1

        # Use rmtree on remaining content (hopefully only *.bid and the calc_directory folder)
        tries = 0
        while tries < 10:
            try:
                shutil.rmtree(calc_directory)
                break
            except:
                tries += 1
        
        if tries == 10:
            print(f'failed to delete {calc_directory}', flush=True)
    
    def __logwrite(self, content):
        if self.logfilename is not None:
            with open(self.logfilename, 'a+') as log:
                log.write(content)
    
    def __filecheck(self, calc_directory):
        """
        Check if the calculation has calc_*.py and calc_*.in files and an
        associated record in the database. If one or more are missing, then
        will return all None values.
        
        Parameters
        ----------
        calc_directory : str
            The calculation directory to check
        
        Returns
        -------
        record : iprPy.Record or None
            The record object associated with the calculation.
        calc_py : path-like object or None
            The location of the calculation's Python script.
        calc_in : path-like object or None
            The location of the calculation's input parameter file. 
        """
        calc_name = calc_directory.name
        
        # Count py and in files
        calc_pys = [i for i in calc_directory.glob('calc_*.py')]
        calc_ins = [i for i in calc_directory.glob('calc_*.in')]
        
        try:  
            # Check for matching database record
            record = self.database.get_record(name=calc_name)
    
            # Assert one py and in file
            assert len(calc_pys) == 1
            assert len(calc_ins) == 1
            
        # Pass ConnectionErrors forward killing runner
        except requests.ConnectionError as e:
            raise requests.ConnectionError(e)

        # If not complete, zip and move to the orphan directory
        except:
            self.__logwrite('Incomplete simulation: moved to orphan directory\n\n')
            shutil.make_archive(Path(self.orphan_directory, calc_name), 'gztar',
                                root_dir=self.run_directory,
                                base_dir=calc_name)
            self.__removecalc(Path(calc_directory))
            
            return None, None, None
        else:
            return record, calc_pys[0].name, calc_ins[0].name
    
    def __parentcheck(self, calc_directory):
        """
        Check status of parent calculations
        
        Parameters
        ----------
        calc_directory : path-like object
            The calculation directory to check
            
        Returns
        -------
        status : str
            The status of the parent calculations: 'error', 'not calculated', 'finished'
        """
        message = ''
        status = 'ready'

        # Loop over all json and xml files
        for path in calc_directory.iterdir():
            
            if path.suffix in ('.json', '.xml'):
                parent_name = path.stem
                
                # Delete pre-existing results file
                if parent_name == 'results':
                    path.unlink()
                
                # Get status of local record copy
                parent = DM(path)
                try:
                    parentstatus = parent.find('status')
                except:
                    parentstatus = 'finished'

                if parentstatus == 'not calculated':
                    # Get status of remote copy
                    parent = self.database.get_record(name=parent_name).content
                    try:
                        parentstatus = parent.find('status')
                    except:
                        parentstatus = 'finished'
                    
                    # Update local record copy if needed
                    if parentstatus in ['finished', 'error']:
                        with open(path, 'w', encoding='utf-8') as f:
                            if path.suffix == '.json':
                                parent.json(fp=f, indent=4, ensure_ascii=False)
                            elif path.suffix == '.xml':
                                parent.xml(fp=f)
                        self.__logwrite(f'parent {parent_name} copied to sim folder\n')
                
                # Identify errors and not calculated parents
                if parentstatus == 'error':
                    status = 'error'
                    message = f'parent {parent_name} issued an error'
                    break

                elif parentstatus == 'not calculated':
                    status = 'not'
                    message = parent_name
                    self.__logwrite(f'parent {parent_name} not calculated yet\n\n')

        return status, message
    
    def __error_results(self, exe_directory, record, message):
        """
        Creates results.json with error status
        """
        # Load content
        model = record.content
        
        # Update status and error fields
        root = list(model.keys())[0]
        model[root]['status'] = 'error'
        model[root]['error'] = message
        
        # Save to execution directory
        with open(Path(exe_directory, 'results.json'), 'w', encoding='utf-8') as f:
            model.json(fp=f, indent=4, ensure_ascii=False)
            
        self.__logwrite(f"error: {message}\n")

        return model
    
    def run(self, calc_name, temp=False, temp_directory=None):
        """
        Runs one calculation from the run_directory.
        
        Parameters
        ----------
        calc_name :str
            The name of the calculation in run_directory to run.
        use_temp : bool, optional
            If True, a new temporary directory will be created and used for this
            run.  
        temp_directory : path-like object, optional
            The path to an existing temporary directory where the calculations
            are to be performed.
            
        Returns
        -------
        status : str
            The status of the calculation after calling run.    
        """
        calc_directory = Path(self.run_directory, calc_name)
        
        # Try bidding for the calc_directory
        if self.__bid(calc_directory) is False:
            return 'bidfail'
        
        # Write calc_name to log file
        self.__logwrite(f'{calc_name}\n')

        # Check that record and calc scripts exist
        record, calc_py, calc_in = self.__filecheck(calc_directory)
        
        if record is None:
            return 'orphan'
        
        # Check on the status of the parent calculations
        status, message = self.__parentcheck(calc_directory)

        if status == 'not':
            for bidfile in calc_directory.glob('*.bid'):
                bidfile.unlink()
            return 'need to run ' + message
        
        elif status == 'error':
            model = self.__error_results(calc_directory, record, message)
            exe_directory = calc_directory
            zip_directory = self.run_directory

        elif status == 'ready':
            
            # Move to temp_directory if needed
            if temp:
                td = tempfile.TemporaryDirectory()
                temp_directory = td.name
                print(f'using temporary directory {temp_directory}')
            
            if temp_directory is not None and status != 'error':
                exe_directory = Path(temp_directory, calc_name)
                zip_directory = temp_directory
                shutil.copytree(calc_directory, exe_directory)
            else:
                exe_directory = calc_directory
                zip_directory = self.run_directory

            # Run calc as subprocess
            command = self.python_exe.split() + calc_py.split() + calc_in.split() + [calc_name]
            run = subprocess.run(command, cwd=exe_directory, capture_output=True, encoding='UTF-8')

            # Load results
            resultsfile = Path(exe_directory, 'results.json')
            if resultsfile.is_file():
                model = DM(resultsfile)
                self.__logwrite('sim calculated successfully\n')
                status = 'success'
            
            # If no results file, then calc failed - add error to record
            else:
                model = self.__error_results(exe_directory, record, run.stderr)
                status = 'error'
        else:
            raise ValueError(f'Unknown calculation status {status}')

        # Update record
        tries = 0
        while tries < 10:
            try:
                self.database.update_record(content=model, name=calc_name)
                break
            except:
                tries += 1
        if tries == 10:
            self.__logwrite('failed to update record\n')
            status += ' - record upload failed'
        else:
            try:
                # tar.gz calculation and add to database
                self.database.add_tar(root_dir=zip_directory, name=calc_name)
            except:
                status += ' - tar upload failed'
                self.__logwrite('failed to upload archive\n')
                
                # Move tar file to hold if it was created 
                tarname = Path(exe_directory, f'{calc_name}.tar.gz')
                if tarname.is_file():
                    shutil.move(tarname, self.hold_directory)

            self.__removecalc(calc_directory)

        if temp:
            td.cleanup()
            
        self.__logwrite('\n')
        return status
    
    def runall(self, bidtries=10, temp=False, temp_directory=None):
        """
        Sequentially runs calculations within the run_directory until all
        are finished.

        Parameters
        ----------
        bidtries : int, optional
            The runner will stop if it fails on bidding this many times in a
            row.  This allows for the cleanup of excess competing runners.
            Default value is 10.
        temp : bool, optional
            If True, a new temporary directory will be created and used for this
            run.  
        temp_directory : path-like object, optional
            The path to an existing temporary directory where the calculations
            are to be performed.
        """

        # Create temp_directory if needed
        if temp:
            td = tempfile.TemporaryDirectory()
            temp_directory = td.name
            print(f'using temporary directory {temp_directory}', flush=True)

        bidcount = 0

        calclist = self.calclist
        while len(calclist) > 0:
            
            # Select a calculation at ramdon
            calc_name = calclist[random.randint(0, len(calclist)-1)]

            # Run the calculation
            status = self.run(calc_name, temp_directory=temp_directory)

            if status == 'bidfail':
                bidcount += 1
                
                # Stop unproductive workers
                if bidcount >= bidtries:
                    print("Didn't find an open simulation", flush=True)
                    break

                # Pause for 10 seconds before trying again
                time.sleep(1)
                calclist = self.calclist
            
            # Try parent next if not calculated
            elif 'need to run' in status:
                calclist = [status.split()[-1]]
            
            # Reset bidcount and reload calclist
            else:
                bidcount = 0
                calclist = self.calclist

        print('No simulations left to run', flush=True)
        
        # Clean temp_directory if needed
        if temp:
            td.cleanup()