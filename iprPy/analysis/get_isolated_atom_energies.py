# coding: utf-8

# Standard Python libraries

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

from ..database.IprPyDatabase import IprPyDatabase

def get_isolated_atom_energies(database: IprPyDatabase,
                               verbose: bool = False
                               ) -> pd.DataFrame:
    """
    Builds a table listing the identified isolated atom energies for each
    LAMMPS potential and symbol model, which can then be used to convert
    measured potential energies into cohesive energies.  This uses finished
    results from both isolated_atom and diatom_scan calculations.
    
    Details:
    - The isolated_atom calculation directly computes the energy of
      non-interacting particles for each symbol.
    - For the diatom_scan calculations, the tabulated values for r > 2.0 are
      searched for a common cutoff energy value, which may not be found if the
      max r measured is less than the cutoff.
    - If energies are found by both methods and are different, the diatom_scan
      values are used.  This bypasses an issue with versions 1+2 of SNAP
      potentials where the energy above the cutoff is correct for a while
      before erroneously droping to zero at some higher cutoff.

    Parameters
    ----------
    database : IprPyDatabase
        The database to search for isolated_atom and diatom_scan results.
    verbose : bool, optional
        Setting this to True will print informative messages.

    Returns
    -------
    pandas.DataFrame
        The table of isolated atom energies for each LAMMPS potential and
        symbol model.
    """
    # Get isolated atom results
    records = database.get_records('calculation_isolated_atom', status='finished')
    if len(records) == 0:
        raise ValueError('No finished isolated atom results found!')

    if verbose:
        print(len(records), 'finished isolated atom results loaded')
    
    results1_df = []
    for record in records:

        # Extract values by symbol
        for symbol, energy in record.isolated_atom_energy.items():
            data = {}
            data['potential_LAMMPS_id'] = record.potential.potential_LAMMPS_id
            data['potential_LAMMPS_key'] = record.potential.potential_LAMMPS_key
            data['potential_id'] = record.potential.potential_id
            data['potential_key'] = record.potential.potential_key
            data['symbol'] = symbol
            data['isolated_atom_energy'] = energy
            results1_df.append(data)

    results1_df = pd.DataFrame(results1_df)

    # Get diatom_scan results
    records = database.get_records('calculation_diatom_scan', status='finished')
    if len(records) == 0:
        raise ValueError('No finished diatom scan results found!')
    
    if verbose:
        print(len(records), 'finished  diatom scan results loaded')
    
    results2_df = []
    for record in records:

        # Skip cross interaction results
        if record.symbols[0] != record.symbols[1]:
            continue

        data = {}
        data['potential_LAMMPS_id'] = record.potential.potential_LAMMPS_id
        data['potential_LAMMPS_key'] = record.potential.potential_LAMMPS_key
        data['potential_id'] = record.potential.potential_id
        data['potential_key'] = record.potential.potential_key
        data['symbol'] = record.symbols[0]

        # Search for common cutoff energy
        try:
            e = record.energy_values[record.r_values > 2.0]
            ii = np.where(e[1:] - e[:-1] == 0)[0][0]
        except:
            data['diatom_cutoff_energy'] = np.nan
        else:
            data['diatom_cutoff_energy'] = e[ii] / 2
        results2_df.append(data)

    results2_df = pd.DataFrame(results2_df)

    # Merge into a single dataframe
    mergekeys = ['potential_LAMMPS_key', 'potential_key',
                 'potential_LAMMPS_id', 'potential_id', 'symbol']
    results_df = pd.merge(results1_df, results2_df, on=mergekeys)
    
    # Relace values where where diatom cutoff is reached and is different 
    usediatom = (~pd.isna(results_df.diatom_cutoff_energy) & 
                 ~np.isclose(results_df.isolated_atom_energy,
                             results_df.diatom_cutoff_energy,
                             atol=0.0, rtol=1e-8))
    
    if verbose:
        print('different energies found for:')
        for potential_LAMMPS_id in results_df[usediatom].potential_LAMMPS_id:
            print(potential_LAMMPS_id)
        print('using diatom_cutoff values for those implementations')
    
    results_df.loc[usediatom, 'isolated_atom_energy'] = results_df.loc[usediatom, 'diatom_cutoff_energy']
    del results_df['diatom_cutoff_energy']

    return results_df.sort_values(['potential_LAMMPS_id', 'symbol']).reset_index(drop=True)