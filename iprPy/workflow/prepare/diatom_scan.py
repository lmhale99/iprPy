# Standard Python libraries
import sys

# iprPy imports
from . import prepare
from ... import load_database

calculation_name = 'diatom_scan'

def main(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares diatom_scan calculations for potentials.

    buildcombos
    - None, custom code here

    Parameters
    ----------
    database_name : str
        The name of the pre-set database to use.
    run_directory_name : str
        The name of the pre-set run_directory to use.
    lammps_command : str
        The LAMMPS executable to use.
    **kwargs : str or list, optional
        Values for any additional or replacement prepare parameters. 
    """
    # Set default branch value to match current function's name
    kwargs['branch'] = kwargs.get('branch', sys._getframe().f_code.co_name)

    pot_kwargs = {}
    for key in kwargs:
        if 'potential_' in key:
            pot_kwargs[key[10:]] = kwargs[key]

    # Fetch potential records and df
    database = load_database(database_name)
    potentials, potential_df = database.get_records(style='potential_LAMMPS', return_df=True, **pot_kwargs)

    kwargs['symbols'] = []
    kwargs['potential_file'] = []
    kwargs['potential_content'] = []
    kwargs['potential_dir'] = []
    kwargs['potential_dir_content'] = []
    
    # Loop over all potentials 
    for i, potential_series in potential_df.iterrows():
        potential = potentials[i]

        # Loop over symbol sets
        for i in range(0, len(potential_series.symbols)):
            symbol_i = potential_series.symbols[i]
            for j in range(i, len(potential_series.symbols)):
                symbol_j = potential_series.symbols[j]
                if symbol_i == symbol_j:
                    kwargs['symbols'].append(symbol_i)
                else:
                    kwargs['symbols'].append(' '.join([symbol_i, symbol_j]))
                kwargs['potential_file'].append(f'{potential.name}.json')
                kwargs['potential_content'].append(f'record {potential.name}')
                kwargs['potential_dir'].append(potential.name)
                kwargs['potential_dir_content'].append(f'tar {potential.name}')
            
    script = "\n".join(
        [
        # Run parameters
        'minimum_r                   0.02',
        'maximum_r                   6.0',
        'number_of_steps_r           300', 
        ]) 
    
    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)
