# coding: utf-8

# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

import atomman.unitconvert as uc

# Local imports
from ... import load_record

def point(self, 
          upload: bool = True,
          runall: bool = False):
    """
    Main function for processing point_defect calculations as used
    for building the content hosted on the NIST Interatomic Potentials
    Repository.
    
    Processing steps:
    
    1. calculation_point_defect_static records are retrieved from the database.
    2. PotentialProperties tables built from 1.
    3. Raw results are saved in csv format based on implementation+potential
    
    Parameters
    ----------
    upload : bool, optional
        If True (default) then the new/modified PotentialProperties records
        will be uploaded to the database automatically.
    runall : bool, optional
        If True, all plots and tables will be regenerated.  If False, only new
        ones are created.  Default value is False.
    """
    # Class attributes
    database = self.database
    getkwargs = self.getkwargs
    outputpath = self.outputpath
    props = self.props
    prop_df = self.prop_df()

    # Get records
    records_df = database.get_records_df(style='calculation_point_defect_static',
                                         status='finished', **getkwargs)
    
    # Load parent records
    parents_df = self.crystals_df
    
    # Add prototype field
    self.identify_prototypes(records_df)
    
    # Merge parent data into records
    records_df = records_df.merge(parents_df, left_on='parent_key', right_on='key',
                                  suffixes=('', '_parent'), validate='many_to_one')
    
    num_updated = 0
    num_skipped = 0
    newprops = []
    for imp_df, pot_id, pot_key, imp_id, imp_key in self.iter_imp_df(records_df):

        # Get or init a properties record
        matching_props = props[(prop_df.potential_LAMMPS_key == imp_key) & (prop_df.potential_key == pot_key)]
        if len(matching_props) == 1:
            prop = matching_props[0]
        elif len(matching_props) == 0:
            prop = load_record('PotentialProperties', potential_key=pot_key,
                               potential_id=pot_id, potential_LAMMPS_key=imp_key,
                               potential_LAMMPS_id=imp_id)
            prop.build_model()
            newprops.append(prop)
        else:
            print('multiple prop records found!')
            continue

        # Skip records with existing results
        if prop.pointdefects.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue

        # Build contentpath and check if it exists
        contentpath = Path(outputpath, pot_id, imp_id)
        if not contentpath.is_dir():
            contentpath.mkdir(parents=True)

        # Set imp data to prop
        prop.pointdefects.data = transform_imp_df(imp_df)

        # Iterate over all compositions
        for composition in np.unique(imp_df.composition):
            comp_df = imp_df[imp_df.composition == composition]

            # Build and save csv
            point_csv(comp_df, outputpath, pot_id, imp_id, composition)

        # Build model component
        prop.pointdefects.exists = True
        model = prop.model['per-potential-properties']
        prop.pointdefects.build_model(model)

        # Add/update PotentialsProperties record
        if upload:
            try:
                database.add_record(prop)
                print('added to database')
            except:
                database.update_record(prop)
                print('updated in database')
        else:
            print('created/modified')
        num_updated += 1

    if len(newprops) > 0:
        self.add_props(newprops)
    print(num_updated, 'added/updated')
    print(num_skipped, 'skipped')

def transform_imp_df(imp_df):
    """
    Transform imp_df to the form used by the PotentialProperties records 
    """

    new_df = []

    # Loop over each family individually
    for family in np.unique(imp_df.family):
        family_df = imp_df[imp_df.family == family]
        found_first_i = False
        
        # Loop over each row sorted by formation energy
        for i in family_df.sort_values('E_ptd_f').index:
            series = family_df.loc[i]
            pointdefect = series.pointdefect_id.replace(series.prototype+'--', '').replace('-', ' ')
            
            # Check if reconfigured
            if series.has_reconfigured:
                
                # Check if lowest energy interstitial
                if found_first_i is False and ('interstitial' in pointdefect or 'dumbbell' in pointdefect):
                    pointdefect = 'relaxed interstitial'
                else:
                    continue
            
            # Change found first interstitial flag
            if 'interstitial' in pointdefect or 'dumbbell' in pointdefect:
                found_first_i = True
            
            # Build results
            dat = {}
            dat['composition'] = series.composition
            dat['prototype'] = series.prototype
            dat['a'] = series.a
            dat['pointdefect'] = pointdefect
            dat['E_f'] = uc.get_in_units(series.E_ptd_f, 'eV')
            dat['pij'] = uc.get_in_units(series.pij, 'eV')
            new_df.append(dat)
    
    # Change into a dataframe
    if len(new_df) > 0:
        new_df = pd.DataFrame(new_df)
    else:
        new_df = pd.DataFrame(columns=['composition', 'prototype', 'a', 'pointdefect', 'E_f', 'pij'])

    # Remove relaxed interstitials if not unique
    bad_index = []
    for i in new_df[new_df.pointdefect == 'relaxed interstitial'].index:
        series = new_df.loc[i]
        
        matches = new_df[(new_df.prototype == series.prototype) &
                         np.isclose(new_df.E_f, series.E_f)]

        if len(matches) > 1:
            bad_index.append(i)
    new_df = new_df.drop(bad_index)

    return new_df
        
def point_csv(df: pd.DataFrame,
              outputpath: Path,
              potential: str,
              implementation: str,
              composition: str):

    csv_df = []
    for i in df.index:
        series = df.loc[i]

        # Build results
        dat = {}
        dat['calc_key'] = series.key
        dat['composition'] = series.composition
        dat['prototype'] = series.prototype
        dat['family'] = series.family
        dat['a'] = series.a
        dat['pointdefect_id'] = series.pointdefect_id
        dat['pointdefect'] = series.pointdefect_id.replace(series.prototype+'--', '').replace('-', ' ')
        dat['E_f'] = '%.3f' % uc.get_in_units(series.E_ptd_f, 'eV')
        dat['p11'] = '%.3f' % uc.get_in_units(series.pij[0,0], 'eV')
        dat['p12'] = '%.3f' % uc.get_in_units(series.pij[0,1], 'eV')
        dat['p13'] = '%.3f' % uc.get_in_units(series.pij[0,2], 'eV')
        dat['p22'] = '%.3f' % uc.get_in_units(series.pij[1,1], 'eV')
        dat['p23'] = '%.3f' % uc.get_in_units(series.pij[1,2], 'eV')
        dat['p33'] = '%.3f' % uc.get_in_units(series.pij[2,2], 'eV')
        dat['reconfigured'] = series.has_reconfigured
        
        try:
            dat['centrosummation_x'] = '%.5f' % series.centrosummation[0]
            dat['centrosummation_y'] = '%.5f' % series.centrosummation[1]
            dat['centrosummation_z'] = '%.5f' % series.centrosummation[2]
        except:
            dat['centrosummation_x'] = np.nan
            dat['centrosummation_y'] = np.nan
            dat['centrosummation_z'] = np.nan
        
        try:
            dat['position_shift_x'] = '%.5f' % series.position_shift[0]
            dat['position_shift_y'] = '%.5f' % series.position_shift[1]
            dat['position_shift_z'] = '%.5f' % series.position_shift[2]
        except:
            dat['position_shift_x'] = np.nan
            dat['position_shift_y'] = np.nan
            dat['position_shift_z'] = np.nan
            
        try:
            dat['db_vect_shift_x'] = '%.5f' % series.db_vect_shift[0]
            dat['db_vect_shift_y'] = '%.5f' % series.db_vect_shift[1]
            dat['db_vect_shift_z'] = '%.5f' % series.db_vect_shift[2]
        except:
            dat['db_vect_shift_x'] = np.nan
            dat['db_vect_shift_y'] = np.nan
            dat['db_vect_shift_z'] = np.nan
        csv_df.append(dat)

    sort_keys = ['prototype', 'a', 'E_f']
    csv_df = pd.DataFrame(csv_df).sort_values(sort_keys)

    filepath = Path(outputpath, potential, implementation,
                    f'pointdefect.{composition}.csv')
    csv_df.to_csv(filepath, index=False)