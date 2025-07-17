from pathlib import Path

import pandas as pd
import numpy as np

import atomman as am

######## To be added to PropertyProcessor! ########

def md_solid_properties(self,
                        upload: bool = True,
                        runall: bool = False):
    
    # Class attributes
    database = self.database
    getkwargs = self.getkwargs
    outputpath = self.outputpath
    props = self.props
    prop_df = self.prop_df()

    
     # Get finished records
    records_df = database.get_records_df(style='md_solid_properties', **getkwargs)


    # Compute atomic volumes
    records_df['V (Å^3/atom)'] = records_df.apply(find_volume, axis=1)

    # Iterate over all potential-implementations
    for imp_df, pot_id, pot_key, imp_id, imp_key in self.iter_imp_df(records_df):

        # Iterate over all crystals
        for relaxed_crystal_key in np.unique(imp_df.relaxed_crystal_key):
            crystal_df = imp_df[imp_df.relaxed_crystal_key == relaxed_crystal_key].sort_values('T (K)')

            # Build csv for the crystal
            md_solid_properties_csv(crystal_df, outputpath, pot_id, imp_id, relaxed_crystal_key)


def find_volume(series):
    """DataFrame apply function for computing the per-atom volume"""
    box = am.Box(a=series.a, b=series.b, c=series.c, alpha=series.alpha, beta=series.beta, gamma=series.gamma)
    return box.volume / series.natoms




def md_solid_properties_csv(df: pd.DataFrame,
                            outputpath: Path,
                            potential: str,
                            implementation: str,
                            crystal_key: str):
    """
    Generates the csv file containing the T-dependent data for one crystal
    """

    include_keys = [
        'key', 'untransformed',
        'relax_dynamic_key', 'free_energy_key', 'elastic_constants_key',
        'T (K)', 'a', 'b', 'c', 'alpha', 'beta', 'gamma',
        'V (Å^3/atom)', 'U (eV/atom)', 'H (eV/atom)', 'G (eV/atom)', 'F (eV/atom)',
        'C11 (GPa)', 'C12 (GPa)', 'C13 (GPa)', 'C14 (GPa)', 'C15 (GPa)', 'C16 (GPa)',
        'C22 (GPa)', 'C23 (GPa)', 'C24 (GPa)', 'C25 (GPa)', 'C26 (GPa)',
        'C33 (GPa)', 'C34 (GPa)', 'C35 (GPa)', 'C36 (GPa)',
        'C44 (GPa)', 'C45 (GPa)', 'C46 (GPa)',
        'C55 (GPa)', 'C56 (GPa)',
        'C66 (GPa)']

    csv_df = df[include_keys]

    filepath = Path(outputpath, potential, implementation,
                    f'solid.{crystal_key}.csv')
    csv_df.to_csv(filepath, index=False)