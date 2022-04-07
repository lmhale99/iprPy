# import libraries
import numpy as np
import iprPy

def main():
    """
    Primary prepare workflow for setting up calculations consistent with how
    they are performed for the NIST Interatomic Potentials Repository.

    GLOBAL SETTINGS:
    - database - The iprPy.Database to use
    - prepare_terms - A dict of prepare settings to use.
    - all_lmppot_ids - The list of LAMMPS potential ids to use.

    INDIVIDUAL POOL SETTINGS:
    - styles - The list of calculation + workflow branch styles to prepare.
    - run_directory - The run directory where the prepared calculations are put.
    - np_per_runner - The expected number of processors per calculation.
    - num_lmppot_ids - The max number of LAMMPS potentials to prepare at a time.
    """
    
    ################### Set database and global prepare_terms #################

    # Load database
    database = iprPy.load_database('iprhub')
    print(database)

    # Define executables and commands
    prepare_terms = {}
    prepare_terms['lammps_command'] =        '/users/lmh1/LAMMPS/2020_03_03/src/lmp_mpi'
    prepare_terms['mpi_command'] =           '/cluster/deb9/bin/mpirun -n {np_per_runner}'
    prepare_terms['lammps_command_snap_1'] = '/users/lmh1/LAMMPS/2017_03_31/src/lmp_mpi'
    prepare_terms['lammps_command_snap_2'] = '/users/lmh1/LAMMPS/2019_06_05/src/lmp_mpi'
    prepare_terms['lammps_command_old'] =    '/users/lmh1/LAMMPS/2019_06_05/src/lmp_mpi'
    prepare_terms['lammps_command_aenet'] =  '/users/lmh1/LAMMPS/bin/lmp_mpi_2020_03_03_aenet'

    ######################## Specify potentials to use ########################

    # Option #1: Select potentials from database to use
    lmppots_df = database.potdb.get_lammps_potentials(return_df = True,
        status = None, 
        #potid = ['1999--Mishin-Y-Farkas-D-Mehl-M-J-Papaconstantopoulos-D-A--Ni'],
        #pair_style = ['eam', 'eam/alloy', 'eam/fs'],
        #symbols = ['Cu'],
    )[1]
    all_lmppot_ids = np.unique(lmppots_df.id).tolist()

    # Option #2: Specify potential ids directly
    #all_lmppot_ids = [
    #    '2019--Plummer-G--Ti-Al-C--LAMMPS--ipr1',
    #    '2019--Plummer-G--Ti-Si-C--LAMMPS--ipr1',
    #    '2021--Plummer-G--Ti-Al-C--LAMMPS--ipr1',
    #    '2022--Hiremath-P--W--LAMMPS--ipr1',
    #    '2022--Mendelev-M-I--Ni-Nb--LAMMPS--ipr1'
    #]
    
    print(len(all_lmppot_ids), 'potential ids found')
    print()

    ########################### Pool settings #################################

    # Pool #1: Basic potential evaluations and scans
    styles = [
        'isolated_atom',
        'diatom_scan',
        'E_vs_r_scan:bop',
        'E_vs_r_scan',
    ]
    run_directory = 'iprhub_1'
    np_per_runner = '1'
    num_lmppot_ids = 100
    prepare_pool(database, styles, run_directory, np_per_runner,
                 all_lmppot_ids, num_lmppot_ids, prepare_terms)

    # Pool #2: Round 1 of crystal structure relaxations
    styles = [
        'relax_box',
        'relax_static',
        'relax_dynamic',
    ]
    run_directory = 'iprhub_2'
    np_per_runner = '1'
    num_lmppot_ids = 100
    prepare_pool(database, styles, run_directory, np_per_runner,
                 all_lmppot_ids, num_lmppot_ids, prepare_terms)


    # Pool #3: Round 2 of crystal structure relaxations
    styles = [
        'relax_static:from_dynamic'
    ]
    run_directory = 'iprhub_3'
    np_per_runner = '1'
    num_lmppot_ids = 100
    prepare_pool(database, styles, run_directory, np_per_runner,
                 all_lmppot_ids, num_lmppot_ids, prepare_terms)

    # Pool #4: Crystal space group analysis
    styles = [
        'crystal_space_group:relax'
    ]
    run_directory = 'iprhub_4'
    np_per_runner = '1'
    num_lmppot_ids = 100
    prepare_pool(database, styles, run_directory, np_per_runner,
                 all_lmppot_ids, num_lmppot_ids, prepare_terms)



def prepare_pool(database, styles, run_directory, np_per_runner,
                 all_lmppot_ids, num_lmppot_ids, prepare_terms):
    """
    Prepares a pool of calculations

    Parameters
    ----------
    database : iprPy.Database
        The database to tie with the calculations.
    styles : list
        The calculations and master prepare branches to prepare.
    run_directory : str
        The name of the run directory where the calculations will be prepared.
    np_per_runner : int
        The number of processors that each calculation expects to use.
    num_lmppot_ids : int
        The max number of lammps potentials to prepare at a time
    prepare_terms : dict
        The global prepare terms to use.
    """
    # Setup and run master_prepare
    prepare_terms['styles']        = ' '.join(styles)
    prepare_terms['run_directory'] = run_directory
    prepare_terms['np_per_runner'] = np_per_runner
    for lmppot_ids in yield_lmppot_ids(all_lmppot_ids, num_lmppot_ids):
        prepare_terms['potential_id'] = lmppot_ids
        database.master_prepare(**prepare_terms)

def yield_lmppot_ids(all_lmppot_ids, delta=100):
    """
    This function divides the total interatomic potentials into smaller sets
    for preparing.  This helps avoid having the prepare methods generating
    too many possible calculation variations to test in one go.
    
    Parameters
    ----------
    all_lmppot_ids : list
        The list of all LAMMPS potentials that calculations are to be prepared
        for.
    delta : int, optional
        The number of potentials to prepare at one time.  Default value is 100.
    """
    i=0
    for i in range(delta, len(all_lmppot_ids), delta):
        print(f'Using potential #s {i-delta} to {i-1}\n')
        yield all_lmppot_ids[i-delta:i]
        
    print(f'Using potential #s {i} to {len(all_lmppot_ids)-1}\n')
    yield all_lmppot_ids[i:len(all_lmppot_ids)]

if __name__ == '__main__':
    main()