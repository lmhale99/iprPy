from typing import Union, Optional, Any, Tuple
from pathlib import Path
import subprocess
import shlex
import time

from .. import load_run_directory, load_database
from ..input import parse, boolean
from ..database import IprPyDatabase

class Emperor():
    """
    Class to manage the top-level high throughput workflow for preparing
    and running iprPy calculations.
    """
    
    def __init__(self,
                 database_name: str,
                 lammps_command: str,
                 mpi_command: Optional[str] = None,
                 lammps_command_snap_1: Optional[str] = None,
                 lammps_command_snap_2: Optional[str] = None,
                 lammps_command_old: Optional[str] = None,
                 lammps_command_aenet: Optional[str] = None,
                 lammps_command_pinn: Optional[str] = None,
                 lammps_command_kim: Optional[str] = None):
        """
        Initializes the class
        
        Parameters
        ----------
        database_name : str
            The database name to use.  Note that the default run_directory
            for each calculation pool will be "{database_name}_{pool_number}".
        lammps_command : str
            The default LAMMPS executable to use.
        mpi_command : str or None, optional
            The MPI executable and options to use if LAMMPS is to be ran on
            multiple cores.
        lammps_command_snap_1 : str or None, optional
            Alternate LAMMPS executable to use with older implementations of
            SNAP potentials.  These require a LAMMPS version between
            8 Oct 2014 and 30 May 2017.
        lammps_command_snap_2 : str or None, optional
            Alternate LAMMPS executable to use with older implementations of
            SNAP potentials.   These require a LAMMPS version between
            3 Dec 2018 and 12 June 2019.
        lammps_command_old : str or None, optional
            Alternate LAMMPS executable to use with some older implementations
            that are no longer compatible with LAMMPS.  These require a LAMMPS
            version before 30 Oct 2019.
        lammps_command_aenet : str or None, optional
            Alternate LAMMPS executable to use for aenet potentials, which
            may be needed as aenet requires building LAMMPS with an external
            library.
        lammps_command_pinn : str or None, optional
            Alternate LAMMPS executable to use for pinn potentials, which
            may be needed as pinn requires building LAMMPS with an external
            library.
        lammps_command_kim : str or None, optional
            Alternate LAMMPS executable to use for kim potentials, which
            may be needed as kim requires building LAMMPS with an external
            library.
        """
        # Set database name and load database
        self.database_name = database_name

        if mpi_command is None:
            mpi_command = ''

        # Build commands dict
        self.__commands = {}
        self.commands['lammps_command'] = lammps_command
        self.commands['mpi_command'] = mpi_command
        if lammps_command_snap_1 is not None:
            self.commands['lammps_command_snap_1'] = lammps_command_snap_1
        if lammps_command_snap_2 is not None:
            self.commands['lammps_command_snap_2'] = lammps_command_snap_2
        if lammps_command_old is not None:
            self.commands['lammps_command_old'] = lammps_command_old
        if lammps_command_aenet is not None:
            self.commands['lammps_command_aenet'] = lammps_command_aenet
        if lammps_command_pinn is not None:
            self.commands['lammps_command_pinn'] = lammps_command_pinn
        if lammps_command_kim is not None:
            self.commands['lammps_command_kim'] = lammps_command_kim

        # Build prepare_pool dict
        self.__build_prepare_pool()

    @classmethod
    def from_script(cls,
                    input_script: Union[str, Path]):
        """
        Initialize an Emperor object from an input script.

        Parameters
        ----------
        input_script : str or Path
            A key value text file containing the init parameters, i.e. the
            database_name, lammps_command, and optionally mpi_command and any
            alternate lammps_commands.
        """
        kwargs = parse(input_script)
        return cls(**kwargs)

    @property
    def database(self) -> IprPyDatabase:
        """iprPy.Database: The database used to prepare the calculations"""
        return self.__database
        
    @property
    def database_name(self) -> str:
        """str: The database to use"""
        return self.__database_name
    
    @database_name.setter
    def database_name(self, val: str):
        # Set both database and database_name properties
        self.__database = load_database(val)
        self.__database_name = val

    @property
    def commands(self) -> dict:
        """dict: The LAMMPS and mpi commands to use"""
        return self.__commands

    @property
    def prepare_pool(self) -> dict:
        """dict: Links prepare pool methods to pool numbers"""
        return self.__prepare_pool

    def __build_prepare_pool(self):
        """Method to map prepare pool methods to pool numbers"""
        # Initialize prepare_pool
        self.__prepare_pool = {}

        # Search for the prepare_pool methods starting at 1
        i = 1
        while True:
            attr = f'prepare_pool_{i}'
            if hasattr(self, attr) and callable(getattr(self, attr)):
                self.prepare_pool[i] = getattr(self, attr)
                i += 1
            else:
                break

    def prepare_pool_description(self):
        """Prints a short description of all prepare_pools"""
        for number, poolfxn in self.prepare_pool.items():
            print(number, poolfxn.__doc__.split('\n')[0])



    def runner_serial(self,
                      run_directory_name: str,
                      calc_names: Optional[list] = None,
                      run_all: bool = False,
                      temp: bool = False,
                      **kwargs):
        """
        Starts a runner that runs prepared jobs one at a time.

        Parameters
        ----------
        run_directory_name : str
            The run_directory containing the calculations to run.
        calc_names : list, optional
            The list of calculations that the runner is to run.
            If None (default) then any calculations currently in the
            run_directory will be ran in random order.
        run_all : bool, optional
            Setting this to True will run all calculations currently
            in the run_directory regardless of if calc_names is given.
        temp : bool, optional
            Flag indicating if the calculations are to be performed in a
            temporary directory.  Default value is False.
        **kwargs : any, optional
            Catch-all for extra keywords ignored by this style.
        """
        # Create a run manager
        runner = self.database.runmanager(run_directory_name)
        if calc_names is None or run_all is True:
            runner.runall(temp=temp)

        else:
            for calc_name in calc_names:
                runner.run(calc_name, temp=temp)



    def runner_slurm_all(self,
                         run_directory_name: str,
                         calc_names: Optional[list] = None,
                         run_all: bool = False,
                         temp: bool = False,
                         ncores: int = 1,
                         wait: Union[bool, int] = False,
                         **kwargs):
        """
        Submits separate slurm jobs to each individually run a single prepared
        calculation.  This is best suited for large calculations or short
        wall times on clusters.

        Parameters
        ----------
        run_directory_name : str
            The run_directory containing the calculations to run.
        calc_names : list, optional
            The list of calculations to submit runners for.  If None (default)
            then will submit jobs for any free calculations currently in the
            run_directory.
        run_all : bool, optional
            Setting this to True will run all calculations currently
            in the run_directory regardless of if calc_names is given.
        temp : bool, optional
            Flag indicating if the calculations are to be performed in a
            temporary directory.  Default value is False.
        ncores : int, optional
            The number of cores to assign to each slurm job.  This dictates
            which slurm script to call.
        wait : bool, optional
            If False (default), the function will return immediately after
            submitting the jobs.  If True or an int, the function will wait to
            return until all targeted calculations are finished.  The int value
            indicates how many seconds to wait between each check.  If True,
            the wait time is taken to be 300 seconds (5 minutes).  Using wait
            can be useful for workflows of sequential calculations where later
            calculations need results from earlier calculations.
        **kwargs : any, optional
            Catch-all for extra keywords ignored by this style.
        """
        
        database_name = self.database_name

        # Find all free calcs in the run_directory
        runner = self.database.runmanager(run_directory_name)
        all_calc_names = runner.calclist

        if calc_names is None or run_all is True:
            # Prepare for all calcs
            calc_names = all_calc_names
        else:
            # Prepare only free calcs from the given list
            calc_names = list(set(calc_names).union(all_calc_names))

        # Set slurm script based on ncores
        if ncores == 1:
            script = 'iprPy_slurm'
        else:
            script = f'iprPy_slurm_{ncores}'
        
        # Add temp option
        if temp is True:
            temp_flag = ' -t'
        else:
            temp_flag = ''

        # Build slurm command and submit the job
        for calc_name in calc_names:
            cmd = f'sbatch {script} {database_name} {run_directory_name}{temp_flag} -c {calc_name}'
            subprocess.run(shlex.split(cmd))
        
        if wait is False:
            return
        
        # Wait until all finished if requested
        run_directory = load_run_directory(run_directory_name)
        if wait is True:
            wait = 300
        while True:
            count = len([calc for calc in run_directory.glob('*')])
            if count == 0:
                break
            else:
                time.sleep(wait)


    def runner_slurm(self,
                     run_directory_name: str,
                     temp: bool = False,
                     ncores: int = 1,
                     njobs: Optional[int] = None,
                     maxjobs: int = 50,
                     percentjobs: int = 10,
                     wait: Union[bool, int] = False,
                     **kwargs):
        """
        Submits slurm jobs for calculation runners such that a certain number
        of runners are active in the run directory.  Note that this method
        has no calc_names parameter as each runner will actively search for
        any free calculations in the run_directory.

        Parameters
        ----------
        run_directory_name : str
            The run_directory containing the calculations to run.
        temp : bool, optional
            Flag indicating if the calculations are to be performed in a
            temporary directory.  Default value is False.
        ncores : int, optional
            The number of cores to assign to each slurm job.  This dictates
            which slurm script to call.
        njobs : int, optional
            The target number of runner jobs that should be active in the
            run_directory.  If there are currently any calculations with .bid
            files, then those calculations are assumed to have active runners
            working on them and the number of new jobs submitted will be
            reduced accordingly.  If None (default), then the percentjobs and
            maxjobs parameters will be used to estimate a njobs value.
        percentjobs : int, optional
            If njobs is None, then a value for njobs is computed to be this
            percentage of the prepared jobs (barring number is greater than
            maxjobs).  Default value is 10 (for 10%).
        maxjobs : int, optional
            If njobs is None, this indicates the maximum njobs value allowed
            by the percentjobs calculation.  Default value is 50.
        wait : bool, optional
            If False (default), the function will return immediately after
            submitting the jobs.  If True or an int, the function will wait to
            return until all targeted calculations are finished.  The int value
            indicates how many seconds to wait between each check.  If True,
            the wait time is taken to be 300 seconds (5 minutes).  Using wait
            can be useful for workflows of sequential calculations where later
            calculations need results from earlier calculations.
        **kwargs : any, optional
            Catch-all for extra keywords ignored by this style.
        """
        # Set slurm script based on ncores
        if ncores == 1:
            script = 'iprPy_slurm'
        else:
            script = f'iprPy_slurm_{ncores}'
        
        # Add temp option
        if temp is True:
            temp_flag = ' -t'
        else:
            temp_flag = ''

        # Build the slurm job submission command
        cmd = f'sbatch {script} {self.database_name} {run_directory_name}{temp_flag}'

        # Count number of calcs and figure out how many jobs to submit
        run_directory = load_run_directory(run_directory_name)
        count = len([calc for calc in run_directory.glob('*')])
        bidcount = len([bid for bid in run_directory.glob('*/*.bid')])

        # Decide on njobs based on percentjobs, minjobs and maxjobs
        if njobs is None:
            njobs = round(count * percentjobs / 100)
            if njobs > maxjobs:
                njobs = maxjobs
        
        # Submit runner jobs so njobs total are active
        for i in range(njobs - bidcount):
            subprocess.run(shlex.split(cmd))
        
        if wait is False:
            return
        
        # Wait until all finished if requested
        if wait is True:
            wait = 300
        while True:
            count = len([calc for calc in run_directory.glob('*')])
            if count == 0:
                break
            else:
                time.sleep(wait)

    def runner(self,
               run_directory_name: str,
               style: str = 'no',
               **kwargs):
        """
        Wrapper for the different runner methods.

        Parameters
        ----------
        run_directory_name : str
            The run_directory containing the calculations to run.
        style : str , optional
            Indicates how to start runners to perform the prepared calculations.
            'no' (default) will start no runners and only prepare.  'serial'
            will start a single runner to serially run through the prepared
            calculations in the current pool before moving on to preparing the
            next pool.  'slurm' will submit a number of runner jobs to a slurm
            schedular for the pool, with each job capable of running multiple
            calculations. 'slurm_all' will submit separate jobs for each
            prepared calculation in the pool.
        **kwargs : any, optional
            Any kwargs settings to pass to the runner method.  The
            specific kwargs depend on the runner_style, and are documented
            by the runner_{runner_style} methods.
        """
        if style == 'serial':
            self.runner_serial(run_directory_name, **kwargs)
        elif style == 'slurm':
            self.runner_slurm(run_directory_name, **kwargs)
        elif style == 'slurm_all':
            self.runner_slurm_all(run_directory_name, **kwargs)
        elif style != 'no':
            raise ValueError('Invalid runner style')

    def compile_params(self,
                       pool_params: dict,
                       **kwargs) -> Tuple[dict, dict]:
        """
        Compiles calculation parameters together from the commands, the
        pool-specific parameters, and any extra/alternate settings given
        as kwargs.  The resulting parameter set is split into parameters
        for preparing calculations and parameters for starting runners.

        Parameters
        ----------
        pool_params : dict
            The master_prepare parameters as defined for a prepare pool.
        **kwargs : any
            Any extra/alternate master_prepare parameters to modify the default
            settings.

        Returns
        -------
        prepare_params : dict
            Keyword parameters for the prepare method call.
        runner_params : dict
            Keyword parameters for the runner method call.
        """
        # Combine commands, pool_params and kwargs
        prepare_params = self.commands
        prepare_params.update(pool_params)
        prepare_params.update(kwargs)

        # Separate out the runner parameters
        keys = list(prepare_params.keys())
        runner_params = {}
        for key in keys:
            if key.startswith('runner_'):
                runner_params[key[7:]] = prepare_params.pop(key)

        return prepare_params, runner_params

    def prepare(self,
                pool: int,
                input_script: Optional[str] = None,
                debug: bool = False,
                **kwargs):
        """
        Prepare calculations for a given pool
        
        Parameters
        ----------
        pool : int
            The calculation pool to prepare calculations for.
        input_script : str or file-like object, optional
            A file containing additional prepare term settings to use.
            Examples are potential limiters or replacement run/prepare settings.
        debug : bool
            If set to True, will throw errors associated with failed/invalid
            calculation builds.  Default is False.
        **kwargs : str or list
            Allows for direct specification of any additional prepare term
            settings to use.  These are treated the same as the values in
            input_script (if it was given).
        """
        # Parse input_script and join with kwargs
        if input_script is not None:
            hold_kwargs = kwargs
            kwargs = parse(input_script)
            kwargs.update(hold_kwargs)

        # Call the prepare_pool method
        prepare_pool = self.prepare_pool[pool]
        prepare_pool(debug=debug, **kwargs)


    def workflow(self,
                 pools: Optional[list] = None,
                 skip: Optional[list] = None,
                 settings_script: Union[str, Path, None] = None,
                 pool_script_directory: Union[Path, str] = '.',
                 debug: bool = False, 
                 **kwargs : Any):
        """
        Prepares (and runs) many or all pools of calculations one after another.

        Parameters
        ----------
        pools : list, optional
            The list of pools to prepare (and run) in order.  If None, then all
            supported prepare pools (not listed in skip) will be performed in
            incremental order.
        skip : list, optional
            For pools=None, skip gives a list of pools to not prepare.
        settings_script : Path or str, optional
            The path to a file containing any calculation setting changes that
            are to be applied to all calculation pools.  The settings in this
            script will override both the default settings and the pool-specific
            settings from the pool_scripts.  Default is None, meaning no script to
            load.
        pool_script_directory : Path or str
            Directory containing any "pool_{number}.in" scripts that provide
            pool-specific prepare settings.  Default value is '.' for the
            current working directory.  The settings in these scripts will override
            the default calculation settings but will be overridden themselves by
            the settings_script values.  Missing and empty pool scripts are allowed
            and indicate no modifications to make for that pool.
        debug : bool, optional
            If set to True, will throw errors associated with failed/invalid
            calculation builds.  Default is False.
        kwargs : any, optional
            Any settings to apply to all calculations given manually as
            kwargs rather than through the settings_script.  If kwargs settings
            and settings_script are both given, the kwargs values take
            precedent.
        """
        if pools is None:
            # Build list of pools to prepare
            pools = list(self.prepare_pool.keys())
            if skip is not None:
                for i in skip:
                    try:
                        pools.pop(pools.index(i))
                    except ValueError:
                        pass
        else:
            # Check all given pool values exist
            for pool in pools:
                assert pool in self.prepare_pool.keys()

        # Extract general settings from settings script
        if settings_script is not None:
            hold_kwargs = kwargs
            kwargs = parse(settings_script)
            kwargs.update(hold_kwargs)
        
        for pool in pools:
            # Set pool-specific input script
            input_script = Path(pool_script_directory, f'pool_{pool}.in')
            if not input_script.exists():
                input_script = None
            
            # Prepare calculation pool
            self.prepare(pool, input_script=input_script, debug=debug, **kwargs)



    # ----------------------------------------------------------------------- #



    def prepare_pool_1(self,
                       debug: bool = False,
                       **kwargs):
        """Basic potential evaluations and scans"""

        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'isolated_atom diatom_scan E_vs_r_scan:bop E_vs_r_scan',
            'run_directory': f'{self.database_name}_1',
            'np_per_runner': '1',
            'num_pots': '100',
        }

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_2(self,
                       debug: bool = False,
                       **kwargs):
        """Relax dynamic"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_dynamic',
            'run_directory': f'{self.database_name}_2',
            'np_per_runner': '1',
            'num_pots': '15',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_3(self,
                       debug: bool = False,
                       **kwargs):
        """Relax box and static"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_static relax_static:from_dynamic relax_box',
            'run_directory': f'{self.database_name}_3',
            'np_per_runner': '1',
            'num_pots': '15',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_4(self,
                       debug: bool = False,
                       **kwargs):
        """Crystal space group
        
        Pool-specific kwargs
        ------------------------
        include_references : bool, optional
            Indicates if crystal_space_group calculations are also to be
            prepared for any crystal prototypes or reference crystals in the
            database.  Default value is False.
        """
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'crystal_space_group:relax',
            'run_directory': f'{self.database_name}_4',
            'np_per_runner': '1',
            'num_pots': '1',
        }
        
        include_references = boolean(kwargs.pop('include_references', False))

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Add prototype and reference branches if wanted
        if include_references is True:
            
            # Specify master_prepare pool settings
            pool_params = {
                'styles': 'crystal_space_group:prototype crystal_space_group:reference',
                'run_directory': f'{self.database_name}_4',
                'np_per_runner': '1',
                'num_pots': '9999999999',
            }
            
            # Compile parameters
            prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
            calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_5(self,
                       debug: bool = False,
                       **kwargs):
        """Static elastic constants"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'elastic_constants_static',
            'run_directory': f'{self.database_name}_5',
            'np_per_runner': '1',
            'num_pots': '50',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_6(self,
                       debug: bool = False,
                       **kwargs):
        """Phonons"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'phonon',
            'run_directory': f'{self.database_name}_6',
            'np_per_runner': '1',
            'num_pots': '50',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_7(self,
                       debug: bool = False,
                       **kwargs):
        """Point defects and surfaces"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'point_defect_static surface_energy_static',
            'run_directory': f'{self.database_name}_7',
            'np_per_runner': '1',
            'num_pots': '50',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_8(self,
                       debug: bool = False,
                       **kwargs):
        """Stacking fault maps"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'stacking_fault_map_2D',
            'run_directory': f'{self.database_name}_8',
            'np_per_runner': '1',
            'num_pots': '50',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_9(self,
                       debug: bool = False,
                       **kwargs):
        """Dislocation monopoles"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'dislocation_monopole:fcc_edge_100 dislocation_monopole:bcc_screw dislocation_monopole:bcc_edge dislocation_monopole:bcc_edge_112',
            'run_directory': f'{self.database_name}_9',
            'np_per_runner': '16',
            'num_pots': '50',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_10(self,
                        debug: bool = False,
                        **kwargs):
        """Dislocation arrays"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'dislocation_periodic_array:fcc_edge_mix dislocation_periodic_array:fcc_screw',
            'run_directory': f'{self.database_name}_10',
            'np_per_runner': '16',
            'num_pots': '50',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_11(self,
                        debug: bool = False,
                        **kwargs):
        """Dynamic relax at 50K"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_dynamic:at_temp_50K',
            'run_directory': f'{self.database_name}_11',
            'np_per_runner': '16',
            'num_pots': '50',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)

        # If sizemults is manually specified, use it
        if 'sizemults' in kwargs:
            calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Otherwise dynamically change sizemults based on natoms
        else:
            sdict = {}
            sdict[16] = [1, 1]
            sdict[13] = [2, 2]
            sdict[12] = [3, 3]
            sdict[10] = [4, 5]
            sdict[9] = [6, 7]
            sdict[8] = [8, 11]
            sdict[7] = [12, 18]
            sdict[6] = [19, 31]
            sdict[5] = [32, 62]
            sdict[4] = [63, 148]
            sdict[3] = [149, 499]
            sdict[2] = [500, 1000]

            calc_names = []

            # Loop over dynamic sizemult sets
            for s in sdict:
                nmin, nmax = sdict[s]
                print(f'Preparing for natoms between {nmin} and {nmax}')

                prepare_params['sizemults'] = f'{s} {s} {s}'
                natoms = list(range(nmin, nmax+1))

                # Find all parents within the sizemults range
                parent_natoms_df = self.database.get_records_df('relaxed_crystal', method='dynamic',
                                                                standing='good', natoms=natoms)
                prepare_params['parent_key'] = parent_natoms_df.key.tolist()

                calc_names.extend(self.database.master_prepare(debug=debug, **prepare_params))

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_12(self,
                        debug: bool = False,
                        **kwargs):
        """Relax dynamic, increasing T
        
        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        sequential_runners : bool, optional
            Flag indicating when runners are started.  False (default) only
            starts the runners after calculations have been prepared for all
            temperatures.  True starts the runners after preparing each
            temperature allowing those calculations to finish before preparing
            the next temperature.  Since calculations are prepared at each
            subsequent temperature based on finished results from the previous
            temperature, False means the prepare will have to be repeatedly
            called whereas True can run all temperatures (assuming no timeouts,
            etc.)
        """
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_dynamic:at_temp',
            'run_directory': f'{self.database_name}_12',
            'np_per_runner': '16',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 3000))
        sequential_runners = bool(kwargs.pop('sequential_runners', False))

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)

        all_calc_names = []
        if runner_kwargs is None:
            runner_kwargs = {}

        # Loop from max temperature down to 50
        for temperature in range(100, max_temperature+50, 50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names = self.database.master_prepare(debug=debug, **prepare_params)

            if sequential_runners is True:
                # Run prepared calcs at the current temperature
                self.runner(run_directory_name=prepare_params['run_directory'],
                            ncores=prepare_params['np_per_runner'],
                            calc_names=calc_names, **runner_params)
            else:
                # Save calc names for running later
                all_calc_names.extend(calc_names)

        if sequential_runners is False:
            # Run all prepared calcs
            self.runner(run_directory_name=prepare_params['run_directory'],
                        ncores=prepare_params['np_per_runner'],
                        calc_names=all_calc_names, **runner_params)



    def prepare_pool_13(self,
                        debug: bool = False,
                        **kwargs):
        """Free energy solid
        
        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'free_energy',
            'run_directory': f'{self.database_name}_13',
            'np_per_runner': '16',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 3000))

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)

        calc_names = []

        # Loop from 50 up to max temperature
        for temperature in range(50, max_temperature+50, 50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names.extend(self.database.master_prepare(debug=debug, **prepare_params))

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_14(self,
                        debug: bool = False,
                        **kwargs):
        """Relax liquid at melt"""
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_liquid_redo:melt',
            'run_directory': f'{self.database_name}_14',
            'np_per_runner': '16',
            'num_pots': '50',
        }
        
        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)
        calc_names = self.database.master_prepare(debug=debug, **prepare_params)

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_15(self,
                        debug: bool = False,
                        **kwargs):
        """Relax liquid, decreasing T
        
        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        sequential_runners : bool, optional
            Flag indicating when runners are started.  False (default) only
            starts the runners after calculations have been prepared for all
            temperatures.  True starts the runners after preparing each
            temperature allowing those calculations to finish before preparing
            the next temperature.  Since calculations are prepared at each
            subsequent temperature based on finished results from the previous
            temperature, False means the prepare will have to be repeatedly
            called whereas True can run all temperatures (assuming no timeouts,
            etc.)
        """
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'relax_liquid_redo:change_temp',
            'run_directory': f'{self.database_name}_15',
            'np_per_runner': '16',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 6100))
        sequential_runners = bool(kwargs.pop('sequential_runners', False))

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)

        all_calc_names = []
        if runner_kwargs is None:
            runner_kwargs = {}

        # Loop from max temperature down to 50
        for temperature in range(max_temperature, 0, -50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)
            prepare_params['temperature_melt'] = str(temperature + 50)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names = self.database.master_prepare(debug=debug, **prepare_params)

            if sequential_runners is True:
                # Run prepared calcs at the current temperature
                self.runner(run_directory_name=prepare_params['run_directory'],
                            ncores=prepare_params['np_per_runner'],
                            calc_names=calc_names, **runner_params)
            else:
                # Save calc names for running later
                all_calc_names.extend(calc_names)

        if sequential_runners is False:
            # Run all prepared calcs
            self.runner(run_directory_name=prepare_params['run_directory'],
                        ncores=prepare_params['np_per_runner'],
                        calc_names=all_calc_names, **runner_params)



    def prepare_pool_16(self,
                        debug: bool = False,
                        **kwargs):
        """Free energy liquid
        
        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'free_energy_liquid',
            'run_directory': f'{self.database_name}_16',
            'np_per_runner': '8',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 6100))

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)

        calc_names = []

        # Loop from max temperature down to 50
        for temperature in range(max_temperature, 0, -50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names.extend(self.database.master_prepare(debug=debug, **prepare_params))

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_17(self,
                        debug: bool = False,
                        **kwargs):
        """Diffusion liquid
        
        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'diffusion_liquid',
            'run_directory': f'{self.database_name}_17',
            'np_per_runner': '8',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 6100))

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)

        calc_names = []

        # Loop from max temperature down to 50
        for temperature in range(max_temperature, 0, -50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names.extend(self.database.master_prepare(debug=debug, **prepare_params))

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_18(self,
                        debug: bool = False,
                        **kwargs):
        """Viscosity liquid calculations

        Pool-specific kwargs
        ------------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'viscosity_driving viscosity_green_kubo',
            'run_directory': f'{self.database_name}_18',
            'np_per_runner': '8',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 6100))

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)

        calc_names = []

        # Loop from max temperature down to 50
        for temperature in range(max_temperature, 0, -50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names.extend(self.database.master_prepare(debug=debug, **prepare_params))

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)



    def prepare_pool_19(self,
                        debug: bool = False,
                        **kwargs):
        """Dynamic elastic constants

        Pool-specific kwargs
        --------------------
        max_temperature : int, optional
            The maximum temperature to prepare.
        """
        # Specify master_prepare pool settings
        pool_params = {
            'styles': 'elastic_constants_dynamic',
            'run_directory': f'{self.database_name}_19',
            'np_per_runner': '1',
            'num_pots': '50',
        }

        # Pull out pool-specific settings if present
        max_temperature = int(kwargs.pop('max_temperature', 3000))

        # Compile parameters
        prepare_params, runner_params = self.compile_params(pool_params, **kwargs)

        calc_names = []

        # Loop from 50 to max temperature
        for temperature in range(50, max_temperature+50, 50):

            # Set melt and run temperatures
            prepare_params['temperature'] = str(temperature)

            # Call master prepare
            print('Starting to prepare for T=', prepare_params['temperature'])
            calc_names.extend(self.database.master_prepare(debug=debug, **prepare_params))

        # Run prepared calculations
        self.runner(run_directory_name=prepare_params['run_directory'],
                    ncores=prepare_params['np_per_runner'],
                    calc_names=calc_names, **runner_params)


