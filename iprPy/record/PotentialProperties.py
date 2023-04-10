# coding: utf-8

# Standard Python imports
import io
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba import load_query

# iprPy imports
from . import Record
from .PotentialPropertiesSubsets import (DiatomScan, EvsRScan, CrystalStructure,
                                         ElasticConstants, FreeSurface, StackingFault,
                                         PointDefect, Phonon)

class PotentialProperties(Record):
    """
    Class for representing PotentialProperties records that contain the data
    necessary to generate the properties pages for an interatomic potential.
    """
    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 **kwargs: any):
        """
        Initialize a PotentialProperties object.  Calculation-specific content
        is managed by PotentialPropertiesSubsets.

        Parameters
        ----------
        model : str, file-like object, DataModelDict
            The contents of the record.
        name : str, optional
            The unique name to assign to the record.  If model is a file
            path, then the default record name is the file name without
            extension.
        potential : BaseLAMMPSPotential, optional
            A record entry for a LAMMPS-compatible potential that the computed
            properties being compiled here are for.  Cannot be given with model
            or the other potential_ parameters as they provide the same
            information.
        potential_key : str, optional
            The UUID key of the potential that the computed properties being
            compiled here are for.  Cannot be given with model or potential as
            they provide the same information.
        potential_id : str, optional
            The id of the potential that the computed properties being compiled
            here are for.  Cannot be given with model or potential as they
            provide the same information.
        potential_LAMMPS_key : str, optional
            The UUID key of the potential implementation that the computed
            properties being compiled here are for.  Cannot be given with model
            or potential as they provide the same information.
        potential_LAMMPS_id : str, optional
            The id of the potential implementation that the computed properties
            being compiled here are for.  Cannot be given with model or
            potential as they provide the same information.
        """

        # Define default core properties
        self.__potential_key = None
        self.__potential_id = None
        self.__potential_LAMMPS_key = None
        self.__potential_LAMMPS_id = None

        # Link to subsets
        self.diatom = DiatomScan(self)
        self.evsr = EvsRScan(self)
        self.crystals = CrystalStructure(self)
        self.cijs = ElasticConstants(self)
        self.freesurfaces = FreeSurface(self)
        self.stackingfaults = StackingFault(self)
        self.pointdefects = PointDefect(self)
        self.phonons = Phonon(self)

        # Build list of all available subsets
        self.subsets = [
            self.diatom,
            self.evsr,
            self.crystals,
            self.cijs,
            self.freesurfaces,
            self.stackingfaults,
            self.pointdefects,
            self.phonons
        ]

        # Call parent init
        super().__init__(model=model, name=name, **kwargs)

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'PotentialProperties'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        raise NotImplementedError('No xsl for this record yet')
        #return ('iprPy.xsl', 'PotentialProperties.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('iprPy.xsd', 'PotentialProperties.xsd')

    @property
    def potential_key(self) -> str:
        """str: UUID4 key assigned to the potential model"""
        return self.__potential_key

    @potential_key.setter
    def potential_key(self, value: str):
        self.__potential_key = str(value)

    @property
    def potential_id(self) -> str:
        """str: Unique id assigned to the potential model"""
        return self.__potential_id

    @potential_id.setter
    def potential_id(self, value: str):
        self.__potential_id = str(value)

    @property
    def potential_LAMMPS_key(self) -> str:
        """str: UUID4 key assigned to the LAMMPS implementation"""
        return self.__potential_LAMMPS_key

    @potential_LAMMPS_key.setter
    def potential_LAMMPS_key(self, value: str):
        self.__potential_LAMMPS_key = str(value)

    @property
    def potential_LAMMPS_id(self) -> str:
        """str: Unique id assigned to the LAMMPS implementation"""
        return self.__potential_LAMMPS_id

    @potential_LAMMPS_id.setter
    def potential_LAMMPS_id(self, value: str):
        self.__potential_LAMMPS_id = str(value)

    @property
    def webdir(self) -> str:
        """str : Root URL for the potential properties content"""
        return f'https://www.ctcms.nist.gov/potentials/entry/{self.potential_id}/{self.potential_LAMMPS_id}'

    @property
    def url(self) -> str:
        """str : URL for the potential properties web page"""
        return f'{self.webdir}.html'

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs: any):
        """
        Sets multiple object values.

        Parameters
        ----------
        name : str, optional
            The name to use for saving the record.  Either name or id should
            be given as they are treated as aliases for this record style.
        potential : BaseLAMMPSPotential, optional
            A record entry for a LAMMPS-compatible potential that the computed
            properties being compiled here are for.  Cannot be given with model
            or the other potential_ parameters as they provide the same
            information.
        potential_key : str, optional
            The UUID key of the potential that the computed properties being
            compiled here are for.  Cannot be given with model or potential as
            they provide the same information.
        potential_id : str, optional
            The id of the potential that the computed properties being compiled
            here are for.  Cannot be given with model or potential as they
            provide the same information.
        potential_LAMMPS_key : str, optional
            The UUID key of the potential implementation that the computed
            properties being compiled here are for.  Cannot be given with model
            or potential as they provide the same information.
        potential_LAMMPS_id : str, optional
            The id of the potential implementation that the computed properties
            being compiled here are for.  Cannot be given with model or
            potential as they provide the same information.
        """

        if 'potential' in kwargs:
            assert 'potential_key' not in kwargs
            assert 'potential_id' not in kwargs
            assert 'potential_LAMMPS_key' not in kwargs
            assert 'potential_LAMMPS_id' not in kwargs
            self.potential_key = kwargs['potential'].potkey
            self.potential_id = kwargs['potential'].potid
            self.potential_LAMMPS_key = kwargs['potential'].key
            self.potential_LAMMPS_id = kwargs['potential'].id
        else:
            if 'potential_key' in kwargs:
                self.potential_key = kwargs['potential_key']
            if 'potential_id' in kwargs:
                self.potential_id = kwargs['potential_id']
            if 'potential_LAMMPS_key' in kwargs:
                self.potential_LAMMPS_key = kwargs['potential_LAMMPS_key']
            if 'potential_LAMMPS_id' in kwargs:
                self.potential_LAMMPS_id = kwargs['potential_LAMMPS_id']

        if name is None:
            if self.potential_LAMMPS_id is not None:
                self.name = f'props.{self.potential_LAMMPS_id}.{self.potential_key[:8]}'

    def load_model(self,
                   model,
                   name: Optional[str] = None,):
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
        super().load_model(model, name=name)
        content = self.model[self.modelroot]

        self.potential_key = content['potential']['key']
        self.potential_id = content['potential']['id']
        self.potential_LAMMPS_key = content['implementation']['key']
        self.potential_LAMMPS_id = content['implementation']['id']

        for subset in self.subsets:
            subset.load_model(content)

        if name is None:
            if self.potential_LAMMPS_id is not None:
                self.name = f'props.{self.potential_LAMMPS_id}.{self.potential_key[:8]}'

    def build_model(self) -> DM:
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict
            The data model content.
        """
        model = DM()
        model[self.modelroot] = content = DM()

        content['potential'] = DM()
        content['potential']['key'] = self.potential_key
        content['potential']['id'] = self.potential_id
        content['implementation'] = DM()
        content['implementation']['key'] = self.potential_LAMMPS_key
        content['implementation']['id'] = self.potential_LAMMPS_id

        for subset in self.subsets:
            subset.build_model(content)

        self._set_model(model)
        return model

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'per-potential-properties'

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """

        meta = {}
        meta['name'] = self.name
        meta['potential_key'] = self.potential_key
        meta['potential_id'] = self.potential_id
        meta['potential_LAMMPS_key'] = self.potential_LAMMPS_key
        meta['potential_LAMMPS_id'] = self.potential_LAMMPS_id

        for subset in self.subsets:
            subset.metadata(meta)

        return meta

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        queries = {
            'potential_key': load_query(
                style='str_match',
                name='potential_key',
                path=f'{self.modelroot}.potential.key',
                description="search by potential's UUID key"),
            'potential_id': load_query(
                style='str_match',
                name='potential_id',
                path=f'{self.modelroot}.potential.id',
                description="search by potential's UUID id"),
            'potential_LAMMPS_key': load_query(
                style='str_match',
                name='potential_LAMMPS_key',
                path=f'{self.modelroot}.implementation.key',
                description="search by potential implementation's UUID key"),
            'potential_LAMMPS_id': load_query(
                style='str_match',
                name='potential_LAMMPS_id',
                path=f'{self.modelroot}.implementation.id',
                description="search by potential implementation's id"),
        }

        for subset in self.subsets:
            queries.update(subset.queries)

        return queries
