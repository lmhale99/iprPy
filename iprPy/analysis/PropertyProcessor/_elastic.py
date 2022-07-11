# coding: utf-8

# Standard Python libraries
from pathlib import Path
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

import atomman.unitconvert as uc

# Local imports
from ... import load_record

def elastic(self, 
            upload: bool = True,
            runall: bool = False):
    """
    Main function for processing elastic_constants_static calculations as used
    for building the content hosted on the NIST Interatomic Potentials
    Repository.
    
    Processing steps:
    
    1. calculation_elastic_constants_static records are retrieved from the database.
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
    if database.style == 'local':
        records = database.get_records(style='calculation_elastic_constants_static',
                                       status='finished', **getkwargs)
        records_df = []
        for record in records:
            records_df.append(record.metadata())
        records_df = pd.DataFrame(records_df)
    else:
        records_df = database.get_records_df(style='calculation_elastic_constants_static',
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
        if prop.cijs.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue

        # Build contentpath and check if it exists
        contentpath = Path(outputpath, pot_id, imp_id)
        if not contentpath.is_dir():
            contentpath.mkdir(parents=True)

        # Set imp data to prop
        prop.cijs.data = transform_imp_df(imp_df)

        # Iterate over all compositions
        for composition in np.unique(imp_df.composition):
            comp_df = imp_df[imp_df.composition == composition]

            # Build and save csv
            elastic_csv(comp_df, outputpath, pot_id, imp_id, composition)

        # Build model component
        prop.cijs.exists = True
        model = prop.model['per-potential-properties']
        prop.cijs.build_model(model)

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
    for i in imp_df.index:
        series = imp_df.loc[i]

        # Build positive strain results
        dat = {}
        dat['composition'] = series.composition
        dat['prototype'] = series.prototype
        dat['a'] = series.a
        dat['strainrange'] = series.strainrange
        dat['straindirection'] = 'positive'
        dat['Cij'] = uc.get_in_units(series.raw_Cij_positive, 'GPa')
        new_df.append(dat)

        # Build negative strain results
        dat = deepcopy(dat)
        dat['straindirection'] = 'negative'
        dat['Cij'] = uc.get_in_units(series.raw_Cij_negative, 'GPa')
        new_df.append(dat)
    new_df = pd.DataFrame(new_df)

    return new_df
        
def elastic_csv(df: pd.DataFrame,
                outputpath: Path,
                potential: str,
                implementation: str,
                composition: str):

    csv_df = []
    for i in df.index:
        series = df.loc[i]

        # Build positive strain results
        dat = {}
        dat['calc_key'] = series.key
        dat['potential_LAMMPS_key'] = series.potential_LAMMPS_key
        dat['potential_LAMMPS_id'] = series.potential_LAMMPS_id
        dat['potential_key'] = series.potential_key
        dat['potential_id'] = series.potential_id
        dat['composition'] = series.composition
        dat['prototype'] = series.prototype
        dat['family'] = series.family
        dat['a'] = series.a
        dat['b'] = series.b
        dat['c'] = series.c
        dat['alpha'] = series.alpha
        dat['beta'] = series.beta
        dat['gamma'] = series.gamma
        dat['strainrange'] = series.strainrange
        dat['straindirection'] = 'positive'
        cij = uc.get_in_units(series.raw_Cij_positive, 'GPa')
        for i in range(6):
            for j in range(6):
                dat[f'C{i+1}{j+1}'] = '%.3f' % cij[i,j]
        csv_df.append(dat)

        # Build negative strain results
        dat = deepcopy(dat)
        dat['straindirection'] = 'negative'
        cij = uc.get_in_units(series.raw_Cij_negative, 'GPa')
        for i in range(6):
            for j in range(6):
                dat[f'C{i+1}{j+1}'] = '%.3f' % cij[i,j]
        csv_df.append(dat)

    sort_keys = ['prototype', 'strainrange', 'straindirection']
    csv_df = pd.DataFrame(csv_df).sort_values(sort_keys)

    filepath = Path(outputpath, potential, implementation,
                    f'elastic.{composition}.csv')
    csv_df.to_csv(filepath, index=False)




        