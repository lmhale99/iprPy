#!/usr/bin/env python
# coding: utf-8

# Standard Python libraries
import argparse

# https://github.com/usnistgov/atomman
import atomman as am

# https://github.com/usnistgov/iprPy
from . import (load_database, load_run_directory, load_calculation,
               check_modules, settings, reset_orphans)
from .calculation import run_calculation
from .database import runner, prepare
from .tools import filltemplate

def command_line():
    args = command_line_parser()
    command_line_actions(args)

def command_line_actions(args):
    """
    Calls iprPy actions based on the parsed arguments
    """   
    # Actions for subcommand check_records
    if args.action == 'check_records':
        database = load_database(args.database)
        database.check_records(args.record_style)
    
    # Actions for subcommand check_modules
    elif args.action == 'check_modules':
        check_modules()
    
    # Actions for subcommand clean_records
    elif args.action == 'clean_records':
        database = load_database(args.database)
        run_directory = load_run_directory(args.run_directory)
        database.clean_records(run_directory=run_directory,
                               record_style=args.record_style)
    
    # Actions for subcommand copy_records
    elif args.action == 'copy_records':
        database1 = load_database(args.database1)
        database2 = load_database(args.database2)
        database1.copy_records(database2, record_style=args.record_style,
                               includetar=args.notar,
                               overwrite=args.overwrite)
    
    # Actions for subcommand copy_references
    elif args.action == 'copy_references':
        database1 = load_database(args.database1)
        database2 = load_database(args.database2)
        database1.copy_references(database2,
                                  includetar=args.notar,
                                  overwrite=args.overwrite)

    # Actions for subcommand destroy_records
    elif args.action == 'destroy_records':
        database = load_database(args.database)
        database.destroy_records(args.record_style)
    
    # Actions for subcommand finish_calculations
    elif args.action == 'finish_calculations':
        database = load_database(args.database)
        run_directory = load_run_directory(args.run_directory)
        database.finish_calculations(run_directory, verbose=args.verbose)

    # Actions for subcommand reset_orphans
    elif args.action == 'reset_orphans':
        run_directory = load_run_directory(args.run_directory)
        reset_orphans(run_directory, orphan_directory=args.orphan_directory)

    # Actions for subcommand prepare
    elif args.action == 'prepare':
        database = load_database(args.database)
        run_directory = load_run_directory(args.run_directory)
        calculation = load_calculation(args.calculation)
        database.prepare(run_directory, calculation,
                         input_script=args.input_script)
    
    # Actions for subcommand master_prepare
    elif args.action == 'master_prepare':
        database = load_database(args.database)
        database.master_prepare(input_script=args.input_script)

    # Actions for subcommand template
    elif args.action == 'template':
        calculation = load_calculation(args.calculation)

        paramfile = f'calc_{calculation.calc_style}.in'
        calcdict = {}
        for key in calculation.allkeys:
            calcdict[key] = ''
        with open(paramfile, 'w', encoding='UTF-8') as f:
            f.write(filltemplate(calculation.template, calcdict, '<', '>'))
        print(f'{paramfile} created')

    # Actions for subcommand templatedoc
    elif args.action == 'templatedoc':
        calculation = load_calculation(args.calculation)
        print(calculation.templatedoc)

    # Actions for subcommand retrieve
    elif args.action == 'retrieve':
        database = load_database(args.database)
        style = args.record_style
        if args.compact is True:
            indent = None
        else:
            indent = 4

        # Call style-specific retrieve for extra functionality
        if style in ['potential_LAMMPS', 'potential_LAMMPS_KIM']:
            if args.getfiles is True:
                pot_dir_style = 'id'
                getfiles = True
            else: 
                pot_dir_style = 'local'
                getfiles = False

            database.potdb.retrieve_lammps_potential(name=args.record_name,
                                                     getfiles=getfiles,
                                                     format=args.format,
                                                     indent=indent,
                                                     pot_dir_style=pot_dir_style,
                                                     verbose=True)
        elif style == 'Citation':
            database.potdb.retrieve_citation(name=args.record_name,
                                             format=args.format, indent=indent,
                                             verbose=True)

        # Call generic retrieve
        else:
            database.potdb.retrieve_record(style=style, name=args.record_name,
                                           format=args.format, indent=indent,
                                           verbose=True)

    # Actions for subcommand run
    elif args.action == 'run':
        run_calculation(args.filename)

    # Actions for subcommand runner
    elif args.action == 'runner':
        database = load_database(args.database)
        run_directory = load_run_directory(args.run_directory)
        database.runner(run_directory,
                        calc_name=args.calc_name,
                        temp=args.temp,
                        bidtries=args.bidtries,
                        bidverbose=args.bidverbose)
    
    # Actions for subcommand set_database
    elif args.action == 'set_database':
        settings.set_database(args.name)
    
    # Actions for subcommand unset_database
    elif args.action == 'unset_database':
        settings.unset_database(args.name)
    
    # Actions for list_databases
    elif args.action == 'list_databases':
        for name in settings.list_databases:
            print(name)

    # Actions for database
    elif args.action == 'database':
        database = load_database(args.database)
        print(database)

    # Actions for subcommand set_run_directory
    elif args.action == 'set_run_directory':
        settings.set_run_directory(args.name)
    
    # Actions for subcommand unset_run_directory
    elif args.action == 'unset_run_directory':
        settings.unset_run_directory(args.name)
    
    # Actions for list_run_directories
    elif args.action == 'list_run_directories':
        for name in settings.list_run_directories:
            print(name)

    # Actions for run_directory
    elif args.action == 'run_directory':
        run_directory = load_run_directory(args.run_directory)
        print(run_directory)

    # Actions for directory
    elif args.action == 'directory':
        print(settings.directory)

    # Actions for set_directory
    elif args.action == 'set_directory':
        settings.set_directory(args.path)

    # Actions for unset_directory
    elif args.action == 'unset_directory':
        settings.unset_directory()

    # Actions for runner_log_directory
    elif args.action == 'runner_log_directory':
        print(settings.runner_log_directory)

    # Actions for set_runner_log_directory
    elif args.action == 'set_runner_log_directory':
        settings.set_runner_log_directory(args.path)

    # Actions for unset_runner_log_directory
    elif args.action == 'unset_runner_log_directory':
        settings.unset_runner_log_directory()

    else:
        raise ValueError('Unknown action argument')
    
def command_line_parser():
    """
    Defines the command line parsing logic for the iprPy command line executable.
    """
    parser = argparse.ArgumentParser(description='iprPy high-throughput commands')
    subparsers = parser.add_subparsers(title='actions', dest='action')
    
    # Define subparser for check_records
    subparser = subparsers.add_parser('check_records', 
                        help='checks status of a run_directory or database')
    subparser.add_argument('database', nargs='?', default=None,
                        help='database name')
    subparser.add_argument('record_style', nargs='?', default=None,
                        help='optional record style to limit by')
    
    # Define subparser for check_modules
    subparser = subparsers.add_parser('check_modules',
                        help='prints load status of all modules in iprPy')
    
    # Define subparser for clean_records
    subparser = subparsers.add_parser('clean_records',
                        help='resets prepared calculations for running again')
    subparser.add_argument('database', nargs='?', default=None,
                        help='database name')
    subparser.add_argument('run_directory', nargs='?', default=None,
                        help='run_directory name')
    subparser.add_argument('record_style', nargs='?', default=None,
                        help='optional record style')
    
    # Define subparser for copy_records
    subparser = subparsers.add_parser('copy_records',
                        help='copy records of a given style from one database to another')
    subparser.add_argument('database1', nargs='?', default=None,
                        help='database name to copy from')
    subparser.add_argument('database2', nargs='?', default=None,
                        help='database name to copy to')
    subparser.add_argument('record_style', nargs='?', default=None,
                        help='optional record style')
    subparser.add_argument('-n', '--notar', action='store_false',
                        help="don't copy tar archives associated with the records")
    subparser.add_argument('-o', '--overwrite', action='store_true',
                        help='overwrite and update any records already in database2')

    # Define subparser for copy_references
    subparser = subparsers.add_parser('copy_references',
                        help='copy all reference record styles from one database to another')
    subparser.add_argument('database1', nargs='?', default=None,
                        help='database name to copy from')
    subparser.add_argument('database2', nargs='?', default=None,
                        help='database name to copy to')
    subparser.add_argument('-n', '--notar', action='store_false',
                        help="don't copy tar archives associated with the records")
    subparser.add_argument('-o', '--overwrite', action='store_true',
                        help='overwrite and update any records already in database2')
    
    # Define subparser for destroy_records
    subparser = subparsers.add_parser('destroy_records',
                        help='delete all records of a given style from a database')
    subparser.add_argument('database', nargs='?', default=None,
                        help='database name')
    subparser.add_argument('record_style', nargs='?', default=None,
                        help='record style')
    
    # Define subparser for finish_calculations
    subparser = subparsers.add_parser('finish_calculations',
                        help='moves finished calculations to a database')
    subparser.add_argument('database', nargs='?', default=None,
                        help='database name')
    subparser.add_argument('run_directory', nargs='?', default=None,
                        help='run_directory name')
    subparser.add_argument('-v', '--verbose', action='store_true',
                        help='calculations will be listed as added to the database')

    # Define subparser for reset_orphans
    subparser = subparsers.add_parser('reset_orphans',
                        help='moves calculations in an orphan directory back to a run directory')
    subparser.add_argument('run_directory', nargs='?', default=None,
                        help='run_directory name')
    subparser.add_argument('orphan_directory', nargs='?', default=None,
                        help='orphan_directory path')

    # Define subparser for prepare
    subparser = subparsers.add_parser('prepare',
                        help='prepare calculations')
    subparser.add_argument('database',
                        help='database name')
    subparser.add_argument('run_directory',
                        help='run_directory name')
    subparser.add_argument('calculation',
                        help='calculation name')
    subparser.add_argument('input_script',
                        help='input parameter script')
    
    # Define subparser for master_prepare
    subparser = subparsers.add_parser('master_prepare',
                        help='prepare multiple calculations using iprPy workflow')
    subparser.add_argument('database',
                        help='database name')
    subparser.add_argument('input_script',
                        help='input parameter script')

    # Define subparser for template
    subparser = subparsers.add_parser('template',
                        help='save an empty input script for a calculation to the working directory')
    subparser.add_argument('calculation',
                        help='calculation name')

    # Define subparser for templatedoc
    subparser = subparsers.add_parser('templatedoc',
                        help="view the documentation for a calculation's input script")
    subparser.add_argument('calculation',
                        help='calculation name')

    # Define subparser for retrieve
    subparser = subparsers.add_parser('retrieve',
                        help="copy/download a record to the working directory")
    subparser.add_argument('database',
                        help='database name')
    subparser.add_argument('record_style', 
                        help='style of the record to retrieve')
    subparser.add_argument('record_name',
                        help='the name of the record in the database to retrieve')
    subparser.add_argument('-f', '--format', default='json', type=str,
                        help='the format to save the record as')
    subparser.add_argument('-c', '--compact', action='store_true',
                        help='indicates if the record is saved in compact format')
    subparser.add_argument('-g', '--getfiles', action='store_true',
                        help='if used, any files associated with the record will also be retrieved')    

    # Define subparser for run
    subparser = subparsers.add_parser('run',
                        help='run a single calculation from a parameter file')
    subparser.add_argument('filename',
                        help='path to a parameter file')

    # Define subparser for runner
    subparser = subparsers.add_parser('runner',
                        help='start runner working on prepared calculations')
    subparser.add_argument('database', nargs='?', default=None,
                        help='database name')
    subparser.add_argument('run_directory', nargs='?', default=None,
                        help='run_directory name')
    subparser.add_argument('-c', '--calc_name', default=None,
                        help='specifies a single calculation in run_directory to run')
    subparser.add_argument('-t', '--temp', action='store_true',
                        help='indicates that the calculations are to run in a temporary directory')
    subparser.add_argument('-b', '--bidtries', default=10, type=int,
                        help='number of sequential bid failures before stopping the runner')
    subparser.add_argument('-v', '--bidverbose', action='store_true',
                        help='bid action info will be printed')
    
    # Define subparser for list_databases
    subparser = subparsers.add_parser('list_databases',
                        help='prints the names of all set databases')

    # Define subparser for set_database
    subparser = subparsers.add_parser('set_database',
                        help='define database access information')
    subparser.add_argument('name', nargs='?', default=None,
                        help='name to assign to the database')
    
    # Define subparser for unset_database
    subparser = subparsers.add_parser('unset_database',
                        help='forget settings for a defined database')
    subparser.add_argument('name', nargs='?', default=None,
                        help='name assigned to the database')
    
    # Define subparser for database
    subparser = subparsers.add_parser('database',
                        help='check info on a set database')
    subparser.add_argument('database', nargs='?', default=None,
                        help='database name')

    # Define subparser for list_run_directories
    subparser = subparsers.add_parser('list_run_directories',
                        help='prints the names of all set run_directory paths')

    # Define subparser for set_run_directory
    subparser = subparsers.add_parser('set_run_directory',
                        help='define run_directory path')
    subparser.add_argument('name', nargs='?', default=None,
                        help='name to assign to the run_directory')
    
    # Define subparser for unset_run_directory
    subparser = subparsers.add_parser('unset_run_directory',
                        help='forget settings for a defined run_directory')
    subparser.add_argument('name', nargs='?', default=None,
                        help='name assigned to the run_directory')
    
    # Define subparser for run_directory
    subparser = subparsers.add_parser('run_directory',
                        help='check info on a set run_directory')
    subparser.add_argument('run_directory', nargs='?', default=None,
                        help='run_directory name')

    # Define subparser for directory
    subparser = subparsers.add_parser('directory',
                        help='prints the path where iprPy settings are saved')

    # Define subparser for set_directory
    subparser = subparsers.add_parser('set_directory',
                        help='define directory path where iprPy settings are saved')
    subparser.add_argument('path', nargs='?', default=None,
                        help='path for the directory')
    
    # Define subparser for unset_directory
    subparser = subparsers.add_parser('unset_directory',
                        help="revert to using iprPy's default settings directory path <home>/.iprPy/")

    # Define subparser for runner_log_directory
    subparser = subparsers.add_parser('runner_log_directory',
                        help='prints the path where runner scripts will save their log files to')

    # Define subparser for set_library_directory
    subparser = subparsers.add_parser('set_library_directory',
                        help='define the path where runner scripts will save their log files to')
    subparser.add_argument('path', nargs='?', default=None,
                        help='path for the directory')
    
    # Define subparser for unset_library_directory
    subparser = subparsers.add_parser('unset_library_directory',
                        help="revert to using default location of <directory>/runner-logs/")

    # Parse command line arguments
    return parser.parse_args()

if __name__ == '__main__':
    command_line()