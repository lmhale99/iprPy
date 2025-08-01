# coding: utf-8

# Standard Python libraries

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

import atomman.unitconvert as uc
from atomman import Box, ElasticConstants2


# Local imports
from .Thermo import Thermo

class ThermoSolid(Thermo):
    """
    Collects thermodynamic data from md_solid_properties records for plotting
    and using thermodynamic transformations to estimate other properties.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes a ThermoSolid object by extracting data from
        md_solid_properties records.

        
        Parameters
        ----------
        df : pandas.DataFrame
            The metadata() information obtained from MDSolidProperties records.
            The data should all be for the same potential and relaxed_crystal_key,
            and for simulations ran at 0 pressure.
        """

        # Check that there is only one relaxed_crystal_key in the dataframe
        if len(set(df.relaxed_crystal_key)) > 1:
            raise ValueError('Multiple relaxed_crystal_key values found in df!')

        # Filter out transformed results
        parsed_df = df[df.untransformed]

        # Sort values by temperature
        sorted_df = parsed_df.sort_values('T (K)')

        # Extract pressures
        Px = sorted_df['Pxx (GPa)'].values
        Py = sorted_df['Pyy (GPa)'].values
        Pz = sorted_df['Pzz (GPa)'].values
        p = uc.set_in_units((Px + Py + Pz) / 3, 'GPa')

        # Filter by pressure
        sorted_df = sorted_df[np.isclose(p, 0.0)]
        p = p[np.isclose(p, 0.0)]

        # Compute volumes
        def get_volume(series) -> float:
            box = Box(a=series.a, b=series.b, c=series.c, alpha=series.alpha, beta=series.beta, gamma=series.gamma)
            return box.volume / series.natoms
        V = uc.set_in_units(sorted_df.apply(get_volume, axis=1), 'angstrom^3')

        # Call base Thermo's init
        super().__init__(sorted_df, p, V)

        # Extract common metadata
        self.__relaxed_crystal_key = df.relaxed_crystal_key.values[0]
        self.__family = df.family.values[0]
        
        



    @property
    def relaxed_crystal_key(self) -> str:
        """str: The UUID key for the original relaxed_crystal record"""
        return self.__relaxed_crystal_key
    
    @property
    def family(self) -> str:
        """str: The crystal prototype/reference family name"""
        return self.__family

    @property
    def symmetryfamily(self) -> str:
        """str: The crystal symmetry family"""
        return self.__symmetryfamily
    
    @property
    def Cij_df(self) -> pd.DataFrame:
        """pandas.DataFrame: The normalized elastic constants"""
        return self.__Cij_df
    

    def __extract_elastic(self, sorted_df):
        
        # Find the crystal symmetry family of the 0 K structure
        series = sorted_df.iloc[0]
        box = Box(a=series.a, b=series.b, c=series.c, alpha=series.alpha, beta=series.beta, gamma=series.gamma)
        self.__symmetryfamily = symmetryfamily = box.identifyfamily()

        # Read Cijs and normalize
        Cij_df = []
        for index in sorted_df.index:
            series = sorted_df.loc[index]
            cdict = {}
            for key in sorted_df.keys():
                if key[0] == 'C':
                    cdict[key[:3]] = series[key]
            C = ElasticConstants2(**cdict)
            Cij_df.append(C.normalized_as(symmetryfamily, return_dict=True))
        self.__Cij_df = pd.DataFrame(Cij_df)


    @property
    def property_df(self):
        """pandas.DataFrame: The table of processed properties"""
        