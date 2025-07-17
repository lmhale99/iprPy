import iprPy

def targeted_runner_by_potential(database_name: str,
                                 run_directory: str,
                                 calc_style: str,
                                 potential_LAMMPS_ids: list):
    """
    Example function for building a runner process that targets
    calculations based on their potential_LAMMPS_ids.
    """

    # Load database
    database = iprPy.load_database(database_name)

    # Create run_manager
    run_manager = database.runmanager(run_directory)

    # Target potentials one at a time
    for potential_LAMMPS_id in potential_LAMMPS_ids:
        records = database.get_records(f'calculation_{calc_style}',
                                    potential_LAMMPS_id=potential_LAMMPS_id,
                                    status='not calculated')
        
        # Loop over calculations unfinished at the time of the get_records call
        for record in records:
            run_manager.run(record.name)

    print('No simulations left to run', flush=True)



if __name__ == '__main__':

    # Specify database, run_directory and calc_style
    database_name = 'iprhub'
    run_directory = 'iprhub_13'
    calc_style = 'free_energy'

    # Specify potentials to target
    potential_LAMMPS_ids = [
        '1986--Foiles-S-M--Ag--LAMMPS--ipr1',
        '1986--Foiles-S-M--Au--LAMMPS--ipr1',
        '1986--Foiles-S-M--Cu--LAMMPS--ipr1',
        '1986--Foiles-S-M--Ni--LAMMPS--ipr1',
        '1986--Foiles-S-M--Pd--LAMMPS--ipr1',
        '1986--Foiles-S-M--Pt--LAMMPS--ipr1',
    ]

    # Call function
    targeted_runner_by_potential(database_name, run_directory,
                                 calc_style, potential_LAMMPS_ids)

