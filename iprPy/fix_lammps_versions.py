# coding: utf-8

# Standard Python libraries
from pathlib import Path

# iprPy imports
from . import load_run_directory

def fix_lammps_versions(run_directory: str,
                        **kwargs):
    """
    Iterates over all prepared calculations in a run_directory and updates
    the LAMMPS version to use.
    
    Parameters
    ----------
    run_directory_name : str
        The name of the run directory containing the prepared calculations
        to update.
    kwargs : any
        Keyword parameters including the current and old LAMMPS commands.
        The current will be replaced by the old for the potentials where it
        is required. All other kwargs are ignored.
    """
    # Handle run_directory
    try:
        run_directory = load_run_directory(run_directory)
    except:
        run_directory = Path(run_directory)

    # Construct default lammps_command line to change
    key = 'lammps_command                  '
    oldlammps = f"{key}{kwargs['lammps_command']}"

    replacementdict = {}

    # Fix for SNAP version 1
    if 'lammps_command_snap_1' in kwargs:
        for pot_id in snap1_pots():
            replacementdict[pot_id] = f"{key}{kwargs['lammps_command_snap_1']}"

    # Fix for SNAP version 2
    if 'lammps_command_snap_2' in kwargs:
        for pot_id in snap2_pots():
            replacementdict[pot_id] = f"{key}{kwargs['lammps_command_snap_2']}"

    # Fix for old potentials
    if 'lammps_command_old' in kwargs:
        for pot_id in old_pots():
            replacementdict[pot_id] = f"{key}{kwargs['lammps_command_old']}"

    # Fix for aenet potentials
    if 'lammps_command_aenet' in kwargs:
        for pot_id in aenet_pots():
            replacementdict[pot_id] = f"{key}{kwargs['lammps_command_aenet']}"

    # Fix for pinn potentials
    if 'lammps_command_pinn' in kwargs:
        for pot_id in pinn_pots():
            replacementdict[pot_id] = f"{key}{kwargs['lammps_command_pinn']}"

    # Fix for kim potentials
    if 'lammps_command_kim' in kwargs:
        for pot_id in kim_pots():
            replacementdict[pot_id] = f"{key}{kwargs['lammps_command_kim']}"

    if len(replacementdict) > 0:

        # Change the lammps commands in the input files
        for inscript in run_directory.glob('*/calc_*.in'):
            with open(inscript, encoding='UTF-8') as f:
                content = f.read()

            for pot_id, lammps in replacementdict.items():
                if pot_id in content:
                    content = content.replace(oldlammps, lammps)
                    break

            with open(inscript, 'w', encoding='UTF-8') as f:
                f.write(content)

def snap1_pots():
    """This is a list of all version 1 SNAP potentials."""
    return ['2015--Thompson-A-P--Ta--LAMMPS--ipr1']

def snap2_pots():
    """This is a list of all version 1 SNAP potentials."""
    return ['2015--Thompson-A-P--Ta--LAMMPS--ipr2']

def old_pots():
    """This is a list of all potentials that only work for older LAMMPS."""
    return [
        '1987--Ackland-G-J--Mo--LAMMPS--ipr1',
        '1987--Ackland-G-J--Mo--LAMMPS--ipr2',
        '2011--Bonny-G--Fe-Cr--LAMMPS--ipr1',
        '2013--Bonny-G--Fe-Cr-W--LAMMPS--ipr1',
        '2013--Smirnova-D-E--U-Mo-Xe--LAMMPS--ipr1',
        '2016--Zhou-X-W--Al-Cu--LAMMPS--ipr1',

        '2011--Bonny-G--Fe-Cr--LAMMPS--ipr2',
        '2011--Bonny-G--Fe-Ni-Cr--LAMMPS--ipr1',
        '2013--Bonny-G--Fe-Cr-W--LAMMPS--ipr2',
        '2013--Gao-H--AgTaO3--LAMMPS--ipr2',
        '2014--Nouranian-S--CH--ipr1',
        '2015--Asadi-E--Fe--LAMMPS--ipr1',
        '2015--Asadi-E--Ni--LAMMPS--ipr1',
        '2018--Etesami-S-A--Cu--LAMMPS--ipr1',
        '2018--Etesami-S-A--Ni--LAMMPS--ipr1',
        '2018--Etesami-S-A--Fe--LAMMPS--ipr1',
        '2018--Etesami-S-A--Pb-Sn--LAMMPS--ipr1',
        '2021--Huang-X--Hf-Nb-Ta-Ti-Zr--LAMMPS--ipr1'
    ]

def aenet_pots():
    """This is a list of aenet potentials (unofficial pair_style)."""
    return ['2020--Mori-H--Fe--LAMMPS--ipr1']

def pinn_pots():
    """This is a list of pinn potentials (unofficial pair_style)."""
    return [
        '2020--Purja-Pun-G-P--Al--LAMMPS--ipr1',
        '2022--Lin-Y-S--Ta--LAMMPS--ipr1',
    ]

def kim_pots():
    """This is a shortcut to identify all KIM models."""
    return ['__MO_']
