from typing import Union, Optional
from pathlib import Path
from tqdm import tqdm

from . import load_transition_temp, noval

def update_untransformed_flag_old(database,
                              transition_temp: Optional[dict] = None,
                              transition_temp_csv: Union[Path, str] = 'transition_temp.csv'):
    """
    Updates the untransformed flag parameter in md_solid_properties records
    according to known transition temperatures.

    Parameters
    ----------
    database : iprPy.database.Database
        The database containing the md_solid_properties records to evaluate.
    transition_temp : dict or None, optional
        A dict containing already known transition temperatures on a
        relaxed_crystal basis.  If not given, will load from the csv file
        indicated by the transition_temp_csv parameter.
    transition_temp_csv : str or Path, optional
        A csv file containing already known transition temperatures on a
        relaxed_crystal basis.  Is ignored if the transition_temp dict is
        given.  Default is 'transition_temp.csv'.
    """
    results, results_df = database.get_records('md_solid_properties', return_df=True)


    # Load transition_temp from csv if needed
    if transition_temp is None:
        transition_temp = load_transition_temp(transition_temp_csv=transition_temp_csv)

    
    num_updated = 0
    for relaxed_crystal_key, T_trans in transition_temp.items():
        crystal_results_df = results_df[results_df.relaxed_crystal_key == relaxed_crystal_key]


        # Update "untransformed" entries >= T_trans to "transformed"
        update_results_df = crystal_results_df[(crystal_results_df.untransformed) & (crystal_results_df['T (K)'] >= T_trans)]
        for index in update_results_df.index:
            record = results[index]
            record.untransformed = False
            record.build_model()
            database.update_record(record = record)
            num_updated += 1

        # Update "transformed" entries < T_trans to "untransformed"
        update_results_df = crystal_results_df[(~crystal_results_df.untransformed) & (crystal_results_df['T (K)'] < T_trans)]
        for index in update_results_df.index:
            record = results[index]
            record.untransformed = True
            record.build_model()
            database.update_record(record = record)
            num_updated += 1

    print(num_updated, 'md_solid_properties records had their untransformed flags updated')


def update_untransformed_flag(database,
                              transition_temp: Optional[dict] = None,
                              transition_temp_csv: Union[Path, str] = 'transition_temp.csv',
                              **kwargs):
    """
    Updates the untransformed flag parameter in md_solid_properties records
    according to known transition temperatures.

    Parameters
    ----------
    database : iprPy.database.Database
        The database containing the md_solid_properties records to evaluate.
    transition_temp : dict or None, optional
        A dict containing already known transition temperatures on a
        relaxed_crystal basis.  If not given, will load from the csv file
        indicated by the transition_temp_csv parameter.
    transition_temp_csv : str or Path, optional
        A csv file containing already known transition temperatures on a
        relaxed_crystal basis.  Is ignored if the transition_temp dict is
        given.  Default is 'transition_temp.csv'.
    """
    
    # Fetch all matching md_solid_properties records
    records = database.get_records('md_solid_properties', **kwargs)

    # Load transition_temp from csv if needed
    if transition_temp is None:
        transition_temp = load_transition_temp(transition_temp_csv=transition_temp_csv)

    # Loop over all loaded records
    num_updated = 0
    for record in tqdm(records):
        
        # Get transition temperature based on the relaxed_crystal family
        T_trans = transition_temp.get(record.relaxed_crystal_key, 999999)

        # Update to transformed if T >= T_trans
        if record.untransformed is True and record.temperature >= T_trans:
            record.untransformed = False
            record.build_model()
            database.update_record(record = record)
            num_updated += 1

        # Update to untransformed if T < T_trans
        elif record.untransformed is False and record.temperature < T_trans:
            record.untransformed = True
            record.build_model()
            database.update_record(record = record)
            num_updated += 1

    print(num_updated, 'md_solid_properties records had their untransformed flags updated')