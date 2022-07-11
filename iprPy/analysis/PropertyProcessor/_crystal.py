# coding: utf-8

# Standard Python libraries
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# Local imports
from ... import load_record

def crystal(self, 
            upload: bool = True,
            runall: bool = False):
    """
    Main function for processing relaxed_crystal records as used for building
    the content hosted on the NIST Interatomic Potentials Repository.
    
    Processing steps:
    
    1. relaxed_crystal records with good standing are retrieved from the
       database.
    2. Tables are built from 1 and added to PotentialProperties records.
    
    Note: .csv files were generated for each implementation + composition when
    the relaxed_crystal records were generated.  This function assumes that
    those files were saved to the website 
    
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
    outputpath = self.outputpath
    props = self.props
    prop_df = self.prop_df()
    ref_proto_df = self.ref_proto_df

    # Get records
    records_df = self.crystals_df

    # Add prototype field
    self.identify_prototypes(records_df)

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
        if prop.crystals.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue

        # Build contentpath and check if it exists
        contentpath = Path(outputpath, pot_id, imp_id)
        if not contentpath.is_dir():
            contentpath.mkdir(parents=True)

        # Set main crystal data
        prop.crystals.data = imp_df

        # Build proto-ref matches
        protoref = []
        for composition in np.unique(imp_df.composition):
            comp_ref_proto_df = ref_proto_df[(ref_proto_df.composition == composition) & (ref_proto_df.prototype.notna())]
            for prototype in np.unique(comp_ref_proto_df.prototype):
                pr = {}
                pr['composition'] = composition
                pr['prototype'] = prototype
                pr['references'] = comp_ref_proto_df[comp_ref_proto_df.prototype == prototype].reference.tolist()
                protoref.append(pr)
        if len(protoref) > 0:
            protoref = pd.DataFrame(protoref)
        else:
            protoref = pd.DataFrame(columns=prop.crystals.protorefcolumns)
        prop.crystals.protoref = protoref

        # Build model component
        prop.crystals.exists = True
        model = prop.model['per-potential-properties']
        prop.crystals.build_model(model)

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