from DataModelDict import DataModelDict as DM

from datamodelbase import query

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

        # Build list of all available subsets
        self.subsets = [
            self.diatom,
            self.evsr,
            self.crystals,
            self.cijs,
            self.freesurfaces,
            self.stackingfaults,
            self.pointdefects,
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
                self.name = f'properties.{self.potential_LAMMPS_id}'

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
                self.name = f'properties.{self.potential_LAMMPS_id}'

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