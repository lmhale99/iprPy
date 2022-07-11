# coding: utf-8

# Local imports
from ... import load_record

def empty(self,
          upload: bool = True):
    """
    Builds new empty PotentialProperties records based on the existing
    potential LAMMPS (and KIM) records.  Empty PotentialProperties records
    ensure that the property pages get generated, even if there is no
    calculation results yet.  The new records will be added to the props list.

    Parameters
    ----------
    upload : bool, optional
        If True (default), then any new PotentialProperties records will be
        automatically saved to the database immediately after creating them.
    """
    # Class attributes
    database = self.database
    props = self.props

    # Fetch all LAMMPS potentials
    potentials_df = self.potentials_df
    print(len(potentials_df), 'LAMMPS potentials found')

    # Get potential LAMMPS keys from existing property records
    prop_imp_keys = []
    for prop in props:
        prop_imp_keys.append(prop.potential_LAMMPS_key)
    
    # Identify good potentials that do not have property records
    missing = (~(potentials_df.key.isin(prop_imp_keys)) 
              &~(potentials_df.id.isin(database.potdb.bad_lammps_potentials)))
    print(missing.sum(), 'property records to be created')
    
    # Loop over missing potentials
    newprops = []
    for i in potentials_df[missing].index:
        series = potentials_df.loc[i]
        
        # Build a new property record
        newprop = load_record('PotentialProperties',
                              potential_key=series.potkey,
                              potential_id=series.potid,
                              potential_LAMMPS_key=series.key,
                              potential_LAMMPS_id=series.id)
        newprop.build_model()
        
        # Add it to the database
        if upload:
            database.add_record(newprop)
            print(newprop.name, 'added to database')
        else:
            print(newprop.name, 'record created')

        newprops.append(newprop)
    
    if len(newprops) > 0:
        self.add_props(newprops)