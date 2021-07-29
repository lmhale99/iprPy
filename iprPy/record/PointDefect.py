from DataModelDict import DataModelDict as DM

from datamodelbase import query

# iprPy imports
from . import Record

modelroot = 'point-defect'

class PointDefect(Record):
    
    @property
    def style(self):
        """str: The record style"""
        return 'point_defect'

    @property
    def xsd_filename(self):
        return ('iprPy.record.xsd', f'{self.style}.xsd')

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return modelroot
    
    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        self.__key = str(value)
    
    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = str(value)

    @property
    def family(self):
        return self.__family

    @family.setter
    def family(self, value):
        self.__family = str(value)

    @property
    def parameters(self):
        return self.__parameters

    def load_model(self, model, name=None):

        super().load_model(model, name=name)
        content = self.model[self.modelroot]

        self.key = content['key']
        self.id = content['id']
        self.family = content['system-family']
        self.__parameters = []
        for cp in content.aslist('calculation-parameter'):
            self.__parameters.append(dict(cp))

    def build_model(self):
        model = DM()
        model[self.modelroot] = content = DM()

        content['key'] = self.key
        content['id'] = self.id
        content['system-family'] = self.family
        for cp in self.parameters:
            content.append('calculation-parameter', DM(cp))

        self._set_model(model)
        return model

    def metadata(self):
        """
        Converts the structured content to a simpler dictionary.
            
        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        meta = {}
        meta['name'] = self.name
        meta['id'] = self.id
        meta['family'] = self.family
        
        meta['ptd_type'] = []
        meta['pos'] = []
        meta['atype'] = []
        meta['db_vect'] = []
        meta['scale'] = []
        for cp in self.parameters:
            meta['ptd_type'].append(cp.get('ptd_type', None))
            meta['pos'].append(cp.get('pos', None))
            meta['atype'].append(cp.get('atype', None))
            meta['db_vect'].append(cp.get('db_vect', None))
            meta['scale'].append(cp.get('scale', None))
        
        return meta

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, id=None,
                     family=None, ptd_type=None):
        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.str_match.pandas(dataframe, 'key', key)
            &query.str_match.pandas(dataframe, 'id', id)
            &query.str_match.pandas(dataframe, 'family', family)
            &query.in_list.pandas(dataframe, 'ptd_type', ptd_type)
        )
        return matches

    @staticmethod
    def mongoquery(name=None, key=None, id=None,
                   family=None, ptd_type=None):
        mquery = {}
        root = f'content.{modelroot}'

        query.str_match.mongo(mquery, f'name', name)

        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_match.mongo(mquery, f'{root}.system-family', family)
        query.in_list.mongo(mquery, f'{root}.calculation-parameter.ptd_type', ptd_type)
        
        return mquery

    @staticmethod
    def cdcsquery(key=None, id=None, family=None, ptd_type=None):
        mquery = {}
        root = modelroot

        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_match.mongo(mquery, f'{root}.system-family', family)
        query.in_list.mongo(mquery, f'{root}.calculation-parameter.ptd_type', ptd_type)

        return mquery