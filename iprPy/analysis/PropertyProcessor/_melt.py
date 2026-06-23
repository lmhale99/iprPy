# coding: utf-8

# Standard Python libraries
from pathlib import Path
from datetime import date
from math import floor, ceil

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://plotly.com/python
import plotly.graph_objects as go

import dbliquid
from atomman import Box, ElasticConstants

# Local imports
from ... import load_record



def melt(self,
             upload: bool = True,
             runall: bool = False):
    """
    Main function for processing melting_temperature
    records as used for building the content hosted on the NIST Interatomic
    Potentials Repository.
    
    Processing steps:
    
    1. md_liquid_properties records are retrieved from the database.
    2. Tables of data and Bokeh plots are constructed for each potential
       implementation.
    3. Details added to PotentialProperties records to indicate plots exist.
    
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

    num_updated = 0
    num_skipped = 0
    for prop, getkwargs in self.iter_by_prop():
        pot_id = prop.potential_id
        imp_id = prop.potential_LAMMPS_id

        # Skip records with existing results
        if prop.melt.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue
        
        # Get records
        imp_df = database.get_records_df(style='calculation_melting_temperature',
                                         status='finished', **getkwargs)
        if len(imp_df) == 0:
            print('no finished records')
            continue
        
        # Add prototype field
        self.identify_prototypes(imp_df)

        # Compute the mean solid fraction
        def mean_solid(series):
            return np.mean(series.fraction_solids[5:])
        imp_df['mean_fraction_solid'] = imp_df.apply(mean_solid, axis=1)

        # Build data
        data = []
        for composition in np.unique(imp_df.composition):
            comp_df = imp_df[imp_df.composition == composition]
            for prototype in np.unique(comp_df.prototype):
                proto_df = comp_df[comp_df.prototype == prototype]

                good_df = proto_df[(proto_df.mean_fraction_solid >= 0.25) & (proto_df.mean_fraction_solid <= 0.75)]
                if len(good_df) >= 10:
                    Tmelts = good_df.melting_temperature.values
                    Tmelt = Tmelts.mean()
                    Terr = Tmelts.std() / len(good_df)**0.5
                    
                    dat = {}
                    dat['composition'] = composition
                    dat['prototype'] = prototype
                    dat['Tmelt'] = np.around(Tmelt, decimals=2)
                    dat['Tmelt_stderr'] = np.around(Terr, decimals=2)
                    data.append(dat)
        
        if len(data) == 0:
            print('not enough finished records')
            continue

        prop.melt.data = pd.DataFrame(data)


        # Build model component
        prop.melt.exists = True
        model = prop.model['per-potential-properties']
        prop.melt.build_model(model)

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
        
    print(num_updated, 'added/updated')
    print(num_skipped, 'skipped')
