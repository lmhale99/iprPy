# coding: utf-8

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba import query

# iprPy imports
from . import Record
from .PotentialPropertiesSubsets import *

class PotentialProperties(Record):
    """
    Class for representing PotentialProperties records that contain the data
    necessary to generate the properties pages for an interatomic potential.
    """
    def __init__(self, model=None, name=None, **kwargs):

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
    def style(self):
        """str: The record style"""
        return 'PotentialProperties'

    @property
    def potential_key(self):
        """str: UUID4 key assigned to the potential model"""
        return self.__potential_key

    @potential_key.setter
    def potential_key(self, value):
        self.__potential_key = str(value)

    @property
    def potential_id(self):
        """str: Unique id assigned to the potential model"""
        return self.__potential_id

    @potential_id.setter
    def potential_id(self, value):
        self.__potential_id = str(value)

    @property
    def potential_LAMMPS_key(self):
        """str: UUID4 key assigned to the LAMMPS implementation"""
        return self.__potential_LAMMPS_key

    @potential_LAMMPS_key.setter
    def potential_LAMMPS_key(self, value):
        self.__potential_LAMMPS_key = str(value)

    @property
    def potential_LAMMPS_id(self):
        """str: Unique id assigned to the LAMMPS implementation"""
        return self.__potential_LAMMPS_id

    @potential_LAMMPS_id.setter
    def potential_LAMMPS_id(self, value):
        self.__potential_LAMMPS_id = str(value)

    @property
    def webdir(self):
        """str : Root URL for the potential properties content"""
        return f'https://www.ctcms.nist.gov/potentials/entry/{self.potential_id}/{self.potential_LAMMPS_id}'

    @property
    def url(self):
        """str : URL for the potential properties web page"""
        return f'{self.webdir}.html'

    def set_values(self, name=None, **kwargs):

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

    def load_model(self, model, name=None):
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

    def build_model(self):
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
    def modelroot(self):
        """str: The root element of the content"""
        return 'per-potential-properties'
    
    def metadata(self):
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
    
    def pandasfilter(self, dataframe, name=None, potential_key=None,
                     potential_id=None, potential_LAMMPS_key=None,
                     potential_LAMMPS_id=None):
        """
        Filters a pandas.DataFrame based on kwargs values for the record style.
        
        Parameters
        ----------
        dataframe : pandas.DataFrame
            A table of metadata for multiple records of the record style.
        name : str or list
            The record name(s) to parse by.
        id : str or list
            The record id(s) to parse by.
        key : str or list
            The record key(s) to parse by.
        family : str or list
            Parent prototype/reference id(s) to parse by.
        hkl : str or list
            Space delimited fault plane(s) to parse by.
        shiftindex : int or list
            shiftindex value(s) to parse by.
        cutboxvector : str or list
            cutboxvector value(s) to parse by.
        
        Returns
        -------
        pandas.Series, numpy.NDArray
            Boolean map of matching values
        """
        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.str_match.pandas(dataframe, 'potential_key', potential_key)
            &query.str_match.pandas(dataframe, 'potential_id', potential_id)
            &query.str_match.pandas(dataframe, 'potential_LAMMPS_key', potential_LAMMPS_key)
            &query.str_match.pandas(dataframe, 'potential_LAMMPS_id', potential_LAMMPS_id)
        )
        return matches

    def mongoquery(self, name=None, potential_key=None,
                   potential_id=None, potential_LAMMPS_key=None,
                   potential_LAMMPS_id=None):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        name : str or list
            The record name(s) to parse by.
        id : str or list
            The record id(s) to parse by.
        key : str or list
            The record key(s) to parse by.
        family : str or list
            Parent prototype/reference id(s) to parse by.
        hkl : str or list
            Space delimited fault plane(s) to parse by.
        shiftindex : int or list
            shiftindex value(s) to parse by.
        cutboxvector : str or list
            cutboxvector value(s) to parse by.
        
        Returns
        -------
        dict
            The Mongo-style query
        """   
        mquery = {}
        root = f'content.{self.modelroot}'

        query.str_match.mongo(mquery, f'name', name)

        query.str_match.mongo(mquery, f'{root}.potential.key', potential_key)
        query.str_match.mongo(mquery, f'{root}.potential.id', potential_id)
        query.str_match.mongo(mquery, f'{root}.implementation.key', potential_LAMMPS_key)
        query.str_match.mongo(mquery, f'{root}.implementation.id', potential_LAMMPS_id)
        
        return mquery

    def cdcsquery(self, potential_key=None,
                   potential_id=None, potential_LAMMPS_key=None,
                   potential_LAMMPS_id=None):
        """
        Builds a CDCS-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        id : str or list
            The record id(s) to parse by.
        key : str or list
            The record key(s) to parse by.
        family : str or list
            Parent prototype/reference id(s) to parse by.
        hkl : str or list
            Space delimited fault plane(s) to parse by.
        shiftindex : int or list
            shiftindex value(s) to parse by.
        cutboxvector : str or list
            cutboxvector value(s) to parse by.
        
        Returns
        -------
        dict
            The CDCS-style query
        """
        mquery = {}
        root = self.modelroot

        query.str_match.mongo(mquery, f'{root}.potential.key', potential_key)
        query.str_match.mongo(mquery, f'{root}.potential.id', potential_id)
        query.str_match.mongo(mquery, f'{root}.implementation.key', potential_LAMMPS_key)
        query.str_match.mongo(mquery, f'{root}.implementation.id', potential_LAMMPS_id)

        return mquery