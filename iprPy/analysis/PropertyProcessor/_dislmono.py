# coding: utf-8

def dislmono(self,
             upload: bool = True,
             runall: bool = False):
    """
    Main function for processing dislocation_monopole
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
        if prop.dislmono.exists and runall is False:
            print('skipped')
            num_skipped += 1
            continue
        
        # Get records
        imp_df = database.get_records_df(style='calculation_dislocation_monopole',
                                         status='finished', **getkwargs)
        if len(imp_df) == 0:
            print('no finished records')
            continue

        # Parse out core structure data
        sort_keys = ['composition', 'dislocation_id']
        include_keys = ['composition', 'dislocation_id', 'key']
        prop.dislmono.cores = imp_df.sort_values(sort_keys)[include_keys]


        # Build model component
        prop.dislmono.exists = True
        model = prop.model['per-potential-properties']
        prop.dislmono.build_model(model)

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
