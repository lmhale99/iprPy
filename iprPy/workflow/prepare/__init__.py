from ... import load_database, load_run_directory, load_calculation
from ...input import parse

def prepare(database_name, run_directory_name, calculation_name,
            inputscript, **kwargs):
    
    print(f'Preparing {calculation_name}', flush=True)

    # Load iprPy parameters
    database = load_database(database_name)
    run_directory = load_run_directory(run_directory_name)
    calculation = load_calculation(calculation_name)

    # Read prepare input parameter file
    input_dict = parse(inputscript, singularkeys=calculation.singularkeys)
    
    # Add/overwrite extra terms (as needed)
    for key in kwargs:
        input_dict[key] = kwargs[key]
    
    # Prepare
    database.prepare(run_directory, calculation, **input_dict)

    print()

from . import crystal_space_group
from . import dislocation_monopole
from . import dislocation_periodic_array
from . import dislocation_SDVPN
from . import E_vs_r_scan 
from . import elastic_constants_static
from . import phonon
from . import point_defect_diffusion
from . import point_defect_static
from . import relax_box 
from . import relax_dynamic 
from . import relax_static 
from . import stacking_fault_map_2D
from . import surface_energy_static