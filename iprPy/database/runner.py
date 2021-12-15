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
from .. import settings, load_run_directory

def runner(database, run_directory, calc_name=None, orphan_directory=None,
           hold_directory=None, log=True, bidtries=10, bidverbose=False,
           temp=False, temp_directory=None):
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
    log : bool, optional
        If True (default), the runner will create and save a log file detailing the
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
    """
    # Initialize a RunManager
    runmanager = RunManager(database, run_directory,
                            orphan_directory=orphan_directory, 
                            hold_directory=hold_directory, log=log)
    
    # Run all calculations
    if calc_name is None:
        print(f'Runner started with pid {runmanager.pid}', flush=True)
        runmanager.runall(bidtries=bidtries, temp=temp,
                          temp_directory=temp_directory,
                          bidverbose=bidverbose)
    
    else:
        print(f'Runner started with pid {runmanager.pid} for calculation {calc_name}', flush=True)
        status = runmanager.run(calc_name=calc_name, temp=temp,
                                temp_directory=temp_directory,
                                bidverbose=bidverbose)

class RunManager():
    """
    Manages the execution of iprPy calculations
    """
    
    def __init__(self, database, run_directory, orphan_directory=None,
                 hold_directory=None, log=True):
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
        log : bool, optional
            If True (default), the runner will create and save a log file detailing the
            status of each calculation that it runs.
        """
        
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
            log_directory = settings.runner_log_directory
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
        """pathlib.Path : The name/path of the log file the runner saves info to."""
        return self.__logfilename
    
    @property
    def calclist(self):
        """list : The current list of calculation names in the run directory."""
        calcs = []
        for calc in self.run_directory.iterdir():
            if calc.is_dir():
                calcs.append(calc.name)
        return calcs
    
    def __bid(self, calc_directory, verbose=False):
        """
        Bids for the chance to run a calculation. Used to help avoid
        runner collisions.

        Parameters
        ----------
        calc_directory : path-like object
            The calculation directory to bid on.
        verbose : bool, optional
            If True, info about the calculation bidding process will be printed.
            Default value is False.

        Returns
        -------
        bool
            True if bidding is successful, False if bidding fails.
        """        
        # Wait as calc folder may be in the process of being deleted
        time.sleep(1)

        # Check if calc_directory exists and if bids have been made
        if not calc_directory.is_dir():
            if verbose:
                print(f'Bid fail - {calc_directory.name} no longer exists')
            return False

        # Check if bids have been made
        try:
            for filename in calc_directory.iterdir():
                assert filename.suffix != '.bid'
        except:
            if verbose:
                print(f'Bid fail - {calc_directory.name} has bids')
            return False
        
        # Try to place a bid - may fail if calc_directory gets deleted
        bidfile = Path(calc_directory, f'{self.pid}.bid')
        try:
            with open(bidfile, 'w') as f:
                f.write(f'bid made using id: {self.pid}')
        except:
            if verbose:
                print(f'Bid fail - {calc_directory.name} could not place bid')
            return False

        # Wait to make sure all bids are in
        time.sleep(1)

        # Build list of submitted bids
        bids = []
        try:
            for filename in calc_directory.iterdir():
                if filename.suffix == '.bid':
                    bids.append(int(filename.stem))
            assert len(bids) > 0
        except:
            if verbose:
                print(f'Bid fail - {calc_directory.name} failed to read bids')
            try:
                bidfile.unlink()
            except:
                pass
            return False
        
        # Competing bids go to the smallest pid
        if min(bids) == self.pid:
            return True
        else:
            if verbose:
                print(f'Bid fail - {calc_directory.name} bid {self.pid} > {min(bids)}')
            try:
                bidfile.unlink()
            except:
                pass
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
        print(content, end='', flush=True)
        if self.logfilename is not None:
            with open(self.logfilename, 'a+') as log:
                log.write(content)
    
    def __filecheck(self, calc_directory):
        """
        Check if the calculation has a calc_*.in file and an
        associated record in the database. If one or more are missing, then
        will return all None values.
        
        Parameters
        ----------
        calc_directory : str
            The calculation directory to check
        
        Returns
        -------
        calculation : iprPy.Calculation or None
            The calculation record object.
        calc_in : path-like object or None
            The location of the calculation's input parameter file. 
        """
        calc_name = calc_directory.name
        incomplete = False
        
        # Search for calc_*.in file 
        calc_ins = [i for i in calc_directory.glob('calc_*.in')]
        if len(calc_ins) == 1:
            calc_in = calc_ins[0]
            style = calc_in.stem.replace('calc_', 'calculation_')
        elif len(calc_ins) == 0:
            incomplete = True
            message = 'No calc_*.in file found: moved to orphan directory\n\n'
        else:
            incomplete = True
            message = 'Multiple calc_*.in files found: moved to orphan directory\n\n'

        # Search database for calculation record
        if incomplete is False:
            try:
                calculation = self.database.get_record(style=style, name=calc_name)
            
            # Kill runner for ConnectionErrors
            except requests.ConnectionError as e:
                self.__logwrite(e)
                raise requests.ConnectionError(e)
            
            except:
                incomplete = True
                message = f'Failed to find matching record in database: moved to orphan directory\n\n'
            
        if incomplete is False:
            return calculation, calc_in.name

        else:
            # If not complete, zip and move to the orphan directory
            self.__logwrite(message)
            shutil.make_archive(Path(self.orphan_directory, calc_name), 'gztar',
                                root_dir=self.run_directory,
                                base_dir=calc_name)
            self.__removecalc(Path(calc_directory))
            
            return None, None

    
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
                    continue
                
                # Get status of local record copy
                parent = DM(path)
                try:
                    parentstatus = parent.find('status')
                except:
                    parentstatus = 'finished'

                if parentstatus == 'not calculated':
                    # Get status of remote copy
                    parent = self.database.get_record(name=parent_name)
                    try:
                        parentstatus = parent.status
                    except:
                        parentstatus = 'finished'
                    
                    # Update local record copy if needed
                    if parentstatus in ['finished', 'error']:
                        with open(path, 'w', encoding='utf-8') as f:
                            if path.suffix == '.json':
                                parent.build_model().json(fp=f, indent=4, ensure_ascii=False)
                            elif path.suffix == '.xml':
                                parent.build_model().xml(fp=f)
                        self.__logwrite(f'parent {parent_name} copied to sim folder\n')
                
                # Identify errors and not calculated parents
                if parentstatus == 'error':
                    status = 'error'
                    message = f'parent {parent_name} issued an error'
                    break

                elif parentstatus == 'not calculated':
                    status = 'not ready'
                    message = parent_name
                    self.__logwrite(f'parent {parent_name} not calculated yet\n\n')

        return status, message
    
    def run(self, calc_name, temp=False, temp_directory=None, bidverbose=False):
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
        bidverbose : bool, optional
            If True, info about the calculation bidding process will be printed.
            Default value is False. 

        Returns
        -------
        status : str
            The status of the calculation after calling run.    
        """
        # Strip slashes from calc_name due to shell autofills
        calc_name = calc_name.strip('/')

        calc_directory = Path(self.run_directory, calc_name)
        
        # Try bidding for the calc_directory
        if self.__bid(calc_directory, verbose=bidverbose) is False:
            return 'bidfail'
        
        # Write calc_name to log file
        self.__logwrite(f'{calc_name}\n')

        # Find calculation and calc script
        calculation, calc_in = self.__filecheck(calc_directory)
        if calculation is None:
            return 'orphan'
        
        # Check on the status of the parent calculations
        status, message = self.__parentcheck(calc_directory)

        # Remove bidfile and move to another calc if parents are not ready
        if status == 'not ready':
            for bidfile in calc_directory.glob('*.bid'):
                bidfile.unlink()
            return 'need to run ' + message
        
        # Change calculation's status to error if parents issued errors
        elif status == 'error':
            calculation.status = 'error'
            calculation.error = message
            exe_directory = calc_directory
            zip_directory = self.run_directory
            self.__logwrite(f'error: {message}')

        # Setup and run calculation
        elif status == 'ready':
            
            if temp:
                # Create new temp directory
                td = tempfile.TemporaryDirectory()
                temp_directory = td.name
                self.__logwrite(f'using temporary directory {temp_directory}\n')
            
            if temp_directory is not None and status != 'error':
                # Copy files to temp directory
                exe_directory = Path(temp_directory, calc_name)
                zip_directory = temp_directory
                shutil.copytree(calc_directory, exe_directory)
            
            else:
                # Default locations
                exe_directory = calc_directory
                zip_directory = self.run_directory

            # Run calc
            os.chdir(exe_directory)
            calculation.load_parameters(calc_in)
            calculation.run(results_json=True)
            os.chdir(self.run_directory)

            # Check status
            if calculation.status == 'finished':
                self.__logwrite('sim calculated successfully\n')
                status = 'success'
            
            # If no results file, then calc failed - add error to record
            elif calculation.status == 'error':
                status = 'error'
                self.__logwrite(f'error: {calculation.error}')

        else:
            raise RuntimeError(f'Unknown status {status}')

        # Update record
        tries = 0
        while tries < 10:
            try:
                self.database.update_record(record=calculation)
                break
            except:
                tries += 1
        if tries == 10:
            self.__logwrite('failed to update record\n')
            status += ' - record upload failed'
        else:
            if True:
            #try:
                # tar.gz calculation and add to database
                self.database.add_tar(root_dir=zip_directory, name=calc_name)
            else:
            #except:
                status += ' - tar upload failed'
                self.__logwrite('failed to upload archive\n')
                
                # Move tar file to hold if it was created 
                tarname = Path(exe_directory, f'{calc_name}.tar.gz')
                if tarname.is_file():
                    shutil.move(tarname, self.hold_directory)

            self.__removecalc(calc_directory)

        # Clean temp_directory if needed
        if temp:
            td.cleanup()
            
        self.__logwrite('\n')
        return status
    
    def runall(self, bidtries=10, temp=False, temp_directory=None,
               bidverbose=False):
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
        bidverbose : bool, optional
            If True, info about the calculation bidding process will be printed.
            Default value is False. 
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
            status = self.run(calc_name, temp_directory=temp_directory,
                              bidverbose=bidverbose)

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