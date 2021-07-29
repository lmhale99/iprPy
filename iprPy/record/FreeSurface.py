
from DataModelDict import DataModelDict as DM

from datamodelbase import query

# iprPy imports
from . import Record

modelroot = 'free-surface'

class FreeSurface(Record):
    
    @property
    def style(self):
        """str: The record style"""
        return 'free_surface'

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
        self.__parameters = dict(content['calculation-parameter'])

    def build_model(self):
        model = DM()
        model[self.modelroot] = content = DM()

        content['key'] = self.key
        content['id'] = self.id
        content['system-family'] = self.family
        content['calculation-parameter'] = DM(self.parameters)

        self._set_model(model)
        return model

    def metadata(self):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        full : bool, optional
            Flag used by the calculation records.  A True value will include
            terms for both the calculation's input and results, while a value
            of False will only include input terms (Default is True).
        flat : bool, optional
            Flag affecting the format of the dictionary terms.  If True, the
            dictionary terms are limited to having only str, int, and float
            values, which is useful for comparisons.  If False, the term
            values can be of any data type, which is convenient for analysis.
            (Default is False).
            
        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        meta = {}
        meta['name'] = self.name
        meta['id'] = self.id
        meta['family'] = self.family
        meta['hkl'] = self.parameters['hkl']
        if 'shiftindex' in self.parameters:
            meta['shiftindex'] = self.parameters['shiftindex']
        meta['cutboxvector'] = self.parameters['cutboxvector']
        
        return meta

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, id=None,
                     family=None, hkl=None, shiftindex=None,
                     cutboxvector=None):
        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.str_match.pandas(dataframe, 'key', key)
            &query.str_match.pandas(dataframe, 'id', id)
            &query.str_match.pandas(dataframe, 'family', family)
            &query.str_match.pandas(dataframe, 'hkl', hkl)
            &query.str_match.pandas(dataframe, 'shiftindex', shiftindex)
            &query.str_match.pandas(dataframe, 'cutboxvector', cutboxvector)
        )
        return matches

    @staticmethod
    def mongoquery(name=None, key=None, id=None,
                   family=None, hkl=None, shiftindex=None,
                     cutboxvector=None):
        mquery = {}
        root = f'content.{modelroot}'

        query.str_match.mongo(mquery, f'name', name)

        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_match.mongo(mquery, f'{root}.system-family', family)
        query.str_match.mongo(mquery, f'{root}.calculation-parameter.hkl', hkl)
        query.str_match.mongo(mquery, f'{root}.calculation-parameter.shiftindex', shiftindex)
        query.str_match.mongo(mquery, f'{root}.calculation-parameter.cutboxvector', cutboxvector)
        
        return mquery

    @staticmethod
    def cdcsquery(key=None, id=None, family=None, hkl=None, shiftindex=None,
                  cutboxvector=None):
        mquery = {}
        root = modelroot

        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_match.mongo(mquery, f'{root}.system-family', family)
        query.str_match.mongo(mquery, f'{root}.calculation-parameter.hkl', hkl)
        query.str_match.mongo(mquery, f'{root}.calculation-parameter.shiftindex', shiftindex)
        query.str_match.mongo(mquery, f'{root}.calculation-parameter.cutboxvector', cutboxvector)

        return mquery