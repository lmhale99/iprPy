# coding: utf-8

# Standard Python libraries
from importlib.resources import open_text
import json
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# Local imports
from ..database.IprPyDatabase import IprPyDatabase

def match_reference_prototype(database: IprPyDatabase, 
                              all_spg_df: Optional[pd.DataFrame] = None,
                              verbose: bool = False
                              ) -> pd.DataFrame:
    """
    Matches reference crystals to known crystal prototype structures using
    crystal_space_group calculation results.  The relevant space group data for
    the known prototypes is pre-compiled in prototype_spg_info.json.  The
    reference crystals are matched to a prototype using the space group and the
    filled Wykoff sites.

    Parameters
    ----------
    database : IprPyDatabase
        The database to search for isolated_atom and diatom_scan results.
    verbose : bool, optional
        Setting this to True will print informative messages.

    Returns
    -------
    pandas.DataFrame
        A table that matches DFT reference structures to known prototypes.
    """
    # Get reference crystal_space_group results
    if all_spg_df is None:
        spg_df = database.get_records_df(style='calculation_crystal_space_group',
                                         branch='reference', status='finished')
    else:
        spg_df = all_spg_df[(all_spg_df.branch=='reference') & 
                            (all_spg_df.status=='finished')].reset_index(drop=True)
    if len(spg_df) == 0:
        raise ValueError('no crystal space group results found!')
    
    if verbose:
        print(len(spg_df), 'crystal space group results for reference crystals found')

    # Load prototype space group data
    proto_spg = json.load(open_text(__package__, 'prototype_spg_info.json'))

    # Set reference field
    spg_df['reference'] = spg_df.parent_key

    # Split reference into site and number for sorting
    def site(series):
        return series.reference.split('-')[0]
    spg_df['site'] = spg_df.apply(site, axis=1)
    def number(series):
        return int(series.reference.split('-')[1])
    spg_df['number'] = spg_df.apply(number, axis=1)

    # Match prototypes to the references based on space group data
    def prototype(series, proto_spg):
        for prototype in proto_spg['prototype_spg_info']['prototype']:
            if (series.spacegroup_number == prototype['spacegroup_number'] and
                series.wykoff_fingerprint in prototype['wykoff_fingerprint']):
                return prototype['name']
        return np.nan
    spg_df['prototype'] = spg_df.apply(prototype, axis=1, args=[proto_spg])

    # Sort, simplify and return
    sort_keys = ['site', 'number']
    include_keys = ['reference', 'prototype', 'composition']
    return spg_df.sort_values(sort_keys)[include_keys].reset_index(drop=True)