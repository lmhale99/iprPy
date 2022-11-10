import iprPy
import atomman as am
import numpy as np

# Database/run_directory names
database_name = 'iprhub'
run_directory_name = 'iprhub_8'

# Phase options
np_per_runner = 1
sizemults = '10 10 10'
family = 'A1--Cu--fcc'
crystal_family = 'cubic'
rtol = 0.05


# Load database
database = iprPy.load_database(database_name)


# Build common prepare kwargs
prepare_kwargs = {}

prepare_kwargs['np_per_runner'] = np_per_runner
prepare_kwargs['sizemults'] = sizemults
prepare_kwargs['run_directory'] = run_directory_name

prepare_kwargs['lammps_command'] = '/toolbox/lmh1/LAMMPS/2022_06_23/build/lmp'
prepare_kwargs['lammps_command_snap_1'] = '/toolbox/lmh1/LAMMPS/2017_03_31/src/lmp_mpi'
prepare_kwargs['lammps_command_snap_2'] = '/toolbox/lmh1/LAMMPS/2019_06_05/src/lmp_mpi'
prepare_kwargs['lammps_command_old'] = '/toolbox/lmh1/LAMMPS/2019_06_05/src/lmp_mpi'
prepare_kwargs['lammps_command_aenet'] = '/toolbox/lmh1/LAMMPS/2022_06_23_aenet/src/lmp_mpi'
prepare_kwargs['lammps_command_pinn'] = '/toolbox/lmh1/LAMMPS/2020_10_29_pinn/src/lmp_mpi'




def check_crystal_family(df, crystal_family, atol=0.0, rtol=0.05):
    """
    Checks if the 'box' field of df, which should be an atomman.Box object,
    is of the indicated crystal family within rtol.
    """
    
    # Define box_parameters apply function based on crystal_family
    
    if crystal_family == 'cubic':
        def box_parameters(series):
            """Check values and build the box_parameter term for cubic systems"""
            if series.box.iscubic(atol=atol, rtol=rtol):
                a = np.mean([series.box.a, series.box.b, series.box.c])
                return f'{a} {a} {a}'
            else:
                return np.nan
    
    elif crystal_family == 'hexagonal':
        def box_parameters(series):
            """Check values and build the box_parameter term for hexagonal systems"""
            if series.box.ishexagonal(atol=atol, rtol=rtol):
                a = np.mean([series.box.a, series.box.b])
                c = series.box.c
                return f'{a} {a} {c} 90.0 90.0 120.0'
            else:
                return np.nan
            
    elif crystal_family == 'tetragonal':     
        def box_parameters(series):
            """Check values and build the box_parameter term for tetragonal systems"""
            if series.box.istetragonal(atol=atol, rtol=rtol):
                a = np.mean([series.box.a, series.box.b])
                c = series.box.c
                return f'{a} {a} {c}'
            else:
                return np.nan
    
    elif crystal_family == 'rhombohedral':
        def box_parameters(series):
            """Check values and build the box_parameter term for rhombohedral systems"""
            if series.box.isrhombohedral(atol=atol, rtol=rtol):
                a = np.mean([series.box.a, series.box.b, series.box.c])
                alpha = np.mean([series.box.alpha, series.box.beta, series.box.gamma])
                return f'{a} {a} {a} {alpha} {alpha} {alpha}'
            else:
                return np.nan
        
    elif crystal_family == 'orthorhombic':
        def box_parameters(series):
            """Check values and build the box_parameter term for orthorhombic systems"""
            if series.box.isorthorhombic(atol=atol, rtol=rtol):
                a = series.box.a
                b = series.box.b
                c = series.box.c
                return f'{a} {b} {c}'
            else:
                return np.nan
        
    elif crystal_family == 'monoclinic':
        def box_parameters(series):
            """Check values and build the box_parameter term for monoclinic systems"""
            if series.box.ismonoclinic(atol=atol, rtol=rtol):
                a = series.box.a
                b = series.box.b
                c = series.box.c
                beta = series.box.beta
                return f'{a} {b} {c} 90.0 {beta} 90.0'
            else:
                return np.nan
            
    elif crystal_family == 'triclinic':
        def box_parameters(series):
            """Check values and build the box_parameter term for triclinic systems"""
            if series.box.istriclinic(atol=atol, rtol=rtol):
                a = series.box.a
                b = series.box.b
                c = series.box.c
                alpha = series.box.alpha
                beta = series.box.beta
                gamma = series.box.gamma
                return f'{a} {b} {c} {alpha} {beta} {gamma}'
            else:
                return np.nan
            
    else:
        raise ValueError(f'unknown crystal family: {crystal_family}')
    
    # Use the apply function on the dataframe
    df['box_parameters'] = df.apply(box_parameters, axis=1)
        
    # Return only the dataframe entries with good box_parameters
    return df[df.box_parameters.notna()]



###################################### 50 K ######################################

# Load relaxed_crystal records
relaxed_df = database.get_records_df('relaxed_crystal', method='dynamic', standing='good',
                                     family=family)

parent_keys = relaxed_df.key.tolist()

database.master_prepare(
    styles = 'relax_dynamic:at_temp',
    num_pots = 900,
    temperature = '50',
    parent_key = parent_keys,
    **prepare_kwargs)


#################################### Higher T ####################################

temperatures = np.arange(100, 3050, 50, dtype=int)

# Fetch all currently finished relax_dynamic:at_temp calculations
relaxed_df = database.get_records_df('calculation_relax_dynamic', branch='at_temp', status='finished',
                                     family=family)

# Create a box object from average lengths and tilts
def make_box(series):
    """Create cell Box from relaxed lengths and tilts"""
    return am.Box(lx=series.lx, ly=series.ly, lz=series.lz,
                  xy=series.xy, xz=series.xz, yz=series.yz)
relaxed_df['box'] = relaxed_df.apply(make_box, axis=1)

for temperature in temperatures:
    print(temperature)
    
    # Get finished calculations for the previous temperature
    previous_temperature = temperature - 50
    previous_df = relaxed_df[relaxed_df.temperature == previous_temperature].reset_index(drop=True)
    if len(previous_df) == 0:
        print('No good parents found')
        continue

    # Check if relaxed box is still the correct crystal family, within rtol.
    previous_df = check_crystal_family(previous_df, crystal_family, rtol=rtol)

    # Get good relaxed_crystal parent keys
    parent_keys = previous_df.parent_key.tolist()
    if len(parent_keys) == 0:
        print('No good parents found')
        continue
    print(len(parent_keys), 'good parents found')
    
    # Prepare calculations at the temperature for the good parents
    database.master_prepare(
        styles = 'relax_dynamic:at_temp',
        num_pots = 900,
        temperature = str(temperature),
        parent_key = parent_keys,
        **prepare_kwargs)
