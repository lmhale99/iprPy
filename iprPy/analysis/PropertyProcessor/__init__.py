from pathlib import Path
from typing import Optional, Union


import pandas as pd
import numpy as np
import numpy.typing as npt

# Local imports
from ...database import IprPyDatabase
from ... import load_database
from .. import match_reference_prototype

class PropertyProcessor():
    """
    Class that manages the generation of web content files and
    PotentialProperties records based on finished calculation results.
    """

    # Class imports
    from ._empty import empty
    from ._diatom import diatom
    from ._evsr import evsr
    from ._crystal import crystal
    from ._elastic import elastic
    from ._surface import surface
    from ._stacking import stacking
    from ._point import point
    from ._phonon import phonon

    def __init__(self,
                 database: Union[IprPyDatabase, str],
                 outputpath: Union[Path, str]):
        """
        Initializes a PropertyProcessor object to manage creating and updating
        property results content for the website based on finished calculation
        results.

        Parameters
        ----------
        database : irpPy.database.IprPyDatabase or str
            The database or name of the database to use for obtaining existing
            records and where the PotentialProperties records will be saved.
        outputpath : pathlib.Path or str
            The root location where all generated web content files are saved.
            For the Interatomic Potentials Repository website, this corresponds
            to https://www.ctcms.nist.gov/potentials/entry/
        """
        # Set values given
        self.database = database
        self.outputpath = outputpath

        self.__getkwargs = {}
        if self.database.style == 'local':
            self.getkwargs['refresh_cache'] = True

        # Set defaults
        self.__ref_proto_df = None
        self.__potentials_df = None
        self.__crystals_df = None

        self.get_props()

    @property
    def database(self):
        """irpPy.database.IprPyDatabase : The database to interact with."""
        return self.__database

    @database.setter
    def database(self, value: Union[IprPyDatabase, str]):
        if isinstance(value, IprPyDatabase):
            self.__database = value
        elif isinstance(value, str):
            self.__database = load_database(value)
        else:
            raise TypeError('database must be specified as an IprPyDatabase object or a str name')

    @property
    def outputpath(self) -> Path:
        """
        pathlib.Path: The root location where all generated web content files
        are saved.
        """
        return self.__outputpath

    @outputpath.setter
    def outputpath(self, value: Union[Path, str]):
        self.__outputpath = Path(value)

    @property
    def getkwargs(self):
        return self.__getkwargs

    @property
    def ref_proto_df(self) -> pd.DataFrame:
        """
        pandas.DataFrame: A table that matches DFT reference structures to
        known prototypes.
        """
        # Build if needed
        if self.__ref_proto_df is None:
            self.__ref_proto_df = match_reference_prototype(self.database)
        return self.__ref_proto_df

    @property
    def potentials_df(self) -> pd.DataFrame:
        """
        pandas.DataFrame: The metadata for all potential_LAMMPS and
        potential_LAMMPS_KIM records.
        """
        # Build if needed
        if self.__potentials_df is None:
            self.__potentials_df = self.database.potdb.get_lammps_potentials(return_df=True,
                                                                             remote=False,
                                                                             **self.getkwargs)[-1]
        return self.__potentials_df

    @property
    def crystals_df(self) -> pd.DataFrame:
        """
        pandas.DataFrame: The metadata for all relaxed_crystal records.
        """
        # Build if needed
        if self.__crystals_df is None:
            self.__crystals_df = self.database.get_records_df(style='relaxed_crystal',
                                                              standing='good',
                                                              **self.getkwargs)
        return self.__crystals_df

    @property
    def props(self) -> np.ndarray:
        """numpy.ndarray: All PotentialProperties records"""
        return self.__props

    def prop_df(self) -> pd.DataFrame:
        """
        Generates a DataFrame for the metadata associated with the current
        PotentialProperties records in the props list.
        """
        prop_df = []
        for prop in self.props:
            prop_df.append(prop.metadata())
        prop_df = pd.DataFrame(prop_df)
        return prop_df

    def get_props(self):
        """
        Fetches PotentialProperties records from the database to (re)build the
        props list.
        """
        self.__props = self.database.get_records('PotentialProperties',
                                                 **self.getkwargs)

    def add_props(self, newprops: npt.ArrayLike):
        """
        Adds new property records to the props list.
        """
        self.__props = np.hstack([self.props, newprops])

    def iter_imp_df(self, records_df: pd.DataFrame):
        """
        Iterates through dataframe subsets that correspond to unique
        potential-implementations.

        Parameters
        ----------
        records_df : pandas.DataFrame
            The dataframe of all records.  Should contain fields potential_id,
            potential_key, potential_LAMMPS_id and potential_LAMMPS_key.
        
        Yields
        ------
        imp_df : pandas.DataFrame
            The subset of records_df that corresponds to a unique set of
            potential_key - potential_LAMMPS_key values.  The yield order
            is sorted based on the potential_id and potential_LAMMPS_id fields.
        potential_id : str
            The potential_id associated with the subset.
        potential_key : str
            The potential_key associated with the subset.
        potential_LAMMPS_id : str
            The potential_LAMMPS_id associated with the subset.
        potential_LAMMPS_key : str
            The potential_LAMMPS_key associated with the subset.
        """
        pot_key_id = []
        for potential_key in np.unique(records_df.potential_key):
            pot_df = records_df[records_df.potential_key == potential_key]

            potential_ids = np.unique(pot_df.potential_id)            
            if len(potential_ids) == 1:
                potential_id = potential_ids[0]
            else:
                print(f'multiple ids for potential_key {potential_key}!')
                potential_id = potential_ids[0]

            for potential_LAMMPS_key in np.unique(pot_df.potential_LAMMPS_key):
                imp_df = pot_df[pot_df.potential_LAMMPS_key == potential_LAMMPS_key]

                potential_LAMMPS_ids = np.unique(imp_df.potential_LAMMPS_id)            
                if len(potential_LAMMPS_ids) == 1:
                    potential_LAMMPS_id = potential_LAMMPS_ids[0]
                else:
                    print(f'multiple ids for potential_LAMMPS_key {potential_LAMMPS_key}!')
                    potential_LAMMPS_id = potential_LAMMPS_ids[0]

                key_id_dict = {}
                key_id_dict['potential_key'] = potential_key
                key_id_dict['potential_id'] = potential_id
                key_id_dict['potential_LAMMPS_key'] = potential_LAMMPS_key
                key_id_dict['potential_LAMMPS_id'] = potential_LAMMPS_id
                pot_key_id.append(key_id_dict)

        pot_key_id = pd.DataFrame(pot_key_id).sort_values(['potential_id', 'potential_LAMMPS_id'])
        print(len(pot_key_id), 'potential-implementations have results')
        
        for i, j in enumerate(pot_key_id.index):
            potential_key = pot_key_id.loc[j, 'potential_key']
            potential_id = pot_key_id.loc[j, 'potential_id']
            potential_LAMMPS_key = pot_key_id.loc[j, 'potential_LAMMPS_key']
            potential_LAMMPS_id = pot_key_id.loc[j, 'potential_LAMMPS_id']
            print(i, potential_id, potential_LAMMPS_id, end=' ')
            
            imp_df = records_df[(records_df.potential_key == potential_key) &
                                (records_df.potential_LAMMPS_key == potential_LAMMPS_key)]
            yield imp_df, potential_id, potential_key, potential_LAMMPS_id, potential_LAMMPS_key


    def identify_prototypes(self,
                            records_df: pd.DataFrame):
        """
        Adds a 'prototype' field to the given dataframe based on the values
        of the 'family' field and the known reference-prototype matches in
        ref_proto_df.

        Parameters
        ----------
        records_df : pd.DataFrame
            The dataframe of record metadata to add the 'prototype' field to.
            Must contain a 'family' field.
        """
        if 'family' not in records_df:
            raise ValueError("records_df is missing 'family' values")

        ref_proto_df = self.ref_proto_df

        # Define apply function
        def get_prototype(series, ref_proto_df):
            """
            If 'family' is a reference structure that has a known prototype
            match, return the prototype name. Otherwise return the family
            value.
            """
            # Match relax family to ref in ref_proto_df
            matches = ref_proto_df[ref_proto_df.reference == series.family]
            try:
                # Check if a match exists and has an associated prototype 
                ref_proto_series = matches.iloc[0]
                assert not pd.isnull(ref_proto_series.prototype)
            except:
                # Return relax family as default
                return series.family
            else:
                # Return ref's prototype if known
                return ref_proto_series.prototype

        # Apply get_prototype
        records_df['prototype'] = records_df.apply(get_prototype, axis=1, args=[ref_proto_df])
