# import libraries
import numpy as np
import atomman as am
import iprPy

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

def yield_lmppot_ids(delta=100):
    """
    This function divides the total interatomic potentials into smaller sets
    for preparing.  This helps avoid having the prepare methods generating
    too many possible calculation variations to test in one go.
    
    Parameters
    ----------
    delta : int, optional
        The number of potentials to prepare at one time.  Default value is 100.
    """
    i=0
    for i in range(delta, len(all_lmppot_ids), delta):
        print(f'Using potential #s {i-delta} to {i-1}\n')
        yield all_lmppot_ids[i-delta:i]
        
    print(f'Using potential #s {i} to {len(all_lmppot_ids)-1}\n')
    yield all_lmppot_ids[i:len(all_lmppot_ids)]

# Potential settings
prepare_terms['potential_status'] = 'all'
lmppots, lmppots_df = database.potdb.get_lammps_potentials(return_df=True, status=None)
all_lmppot_ids = np.unique(lmppots_df.id).tolist()
print(len(all_lmppot_ids), 'potential ids found')
print()

# Define function for iterating over subsets of potentials
def yield_lmppot_ids(delta=100):
    for i in range(delta, len(all_lmppot_ids), delta):
        print(f'Using potential #s {i-delta} to {i-1}\n')
        yield all_lmppot_ids[i-delta:i]
    print(f'Using potential #s {i} to {len(all_lmppot_ids)-1}\n')
    yield all_lmppot_ids[i:len(all_lmppot_ids)]


# Pool #1: Basic potential evaluations and scans
num_lmppot_ids = 100
styles = [
    'isolated_atom',
    'diatom_scan',
    'E_vs_r_scan:bop',
    'E_vs_r_scan',
]
prepare_terms['styles']        = ' '.join(styles)
prepare_terms['run_directory'] = 'iprhub_1'
prepare_terms['np_per_runner'] = '1'
for lmppot_ids in yield_lmppot_ids(num_lmppot_ids):
    prepare_terms['potential_id'] = lmppot_ids
    database.master_prepare(**prepare_terms)


# Pool #2: Round 1 of crystal structure relaxations
num_lmppot_ids = 100
styles = [
    'relax_box',
    'relax_static',
    'relax_dynamic',
]
prepare_terms['styles']        = ' '.join(styles)
prepare_terms['run_directory'] = 'iprhub_3'
prepare_terms['np_per_runner'] = '1'
for lmppot_ids in yield_lmppot_ids(num_lmppot_ids):
    prepare_terms['potential_id'] = lmppot_ids
    database.master_prepare(**prepare_terms)


# Pool #3: Round 2 of crystal structure relaxations
num_lmppot_ids = 100
styles = [
    'relax_static:from_dynamic'
]
prepare_terms['styles']        = ' '.join(styles)
prepare_terms['run_directory'] = 'iprhub_3'
prepare_terms['np_per_runner'] = '1'
for lmppot_ids in yield_lmppot_ids(num_lmppot_ids):
    prepare_terms['potential_id'] = lmppot_ids
    database.master_prepare(**prepare_terms)


# Pool #4: Crystal space group analysis
num_lmppot_ids = 100
styles = [
    'crystal_space_group:relax'
]
prepare_terms['styles']        = ' '.join(styles)
prepare_terms['run_directory'] = 'iprhub_4'
prepare_terms['np_per_runner'] = '1'
for lmppot_ids in yield_lmppot_ids(num_lmppot_ids):
    prepare_terms['potential_id'] = lmppot_ids
    database.master_prepare(**prepare_terms)
