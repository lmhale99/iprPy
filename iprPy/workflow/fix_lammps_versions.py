from .. import load_run_directory

def fix_lammps_versions(run_directory_name, commands):
    """
    Iterates over all prepared calculations in a run_directory and updates
    the LAMMPS version to use.
    
    Parameters
    ----------
    run_directory_name : str
        The name of the run directory containing the prepared calculations
        to update.
    commands : dict
        The current and old LAMMPS commands. The current will be replaced
        by the old for the potentials where it is required.    
    """

    oldlammps = commands['lammps_command']

    replacementdict = {}
    
    # Fix for SNAP version 1
    if 'lammps_command_snap_1' in commands:
        pots = ['2015--Thompson-A-P--Ta--LAMMPS--ipr1']
        for pot_id in pots:
            replacementdict[pot_id] = commands['lammps_command_snap_1']

    # Fix for SNAP version 2
    if 'lammps_command_snap_2' in commands:
        pots = ['2015--Thompson-A-P--Ta--LAMMPS--ipr2']
        for pot_id in pots:
            replacementdict[pot_id] = commands['lammps_command_snap_2']

    # Fix for old potentials
    if 'lammps_command_old' in commands:
        pots = [
            '1987--Ackland-G-J--Mo--LAMMPS--ipr1',
            '1987--Ackland-G-J--Mo--LAMMPS--ipr2',
            '2011--Bonny-G--Fe-Cr--LAMMPS--ipr1',
            '2013--Bonny-G--Fe-Cr-W--LAMMPS--ipr1',
            '2013--Smirnova-D-E--U-Mo-Xe--LAMMPS--ipr1',
        ]
        for pot_id in pots:
            replacementdict[pot_id] = commands['lammps_command_old']

    # Change the lammps commands in the input files
    run_directory = load_run_directory(run_directory_name)
    for inscript in run_directory.glob('*/calc_*.in'):
        with open(inscript) as f:
            content = f.read()
        
        for pot_id, lammps in replacementdict.items():
            if pot_id in content:
                content = content.replace(oldlammps, lammps)
                break
                
        with open(inscript, 'w') as f:
            f.write(content)