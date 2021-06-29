from copy import deepcopy

# https://github.com/usnistgov/atomman
from atomman import System

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from datamodelbase.record import Record
from datamodelbase import query

modelroot = 'reference-crystal'

class ReferenceCrystal(Record):
    
    @property
    def style(self):
        """str: The record style"""
        return 'reference_crystal'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return modelroot

    @property
    def xsd_filename(self):
        return ('iprPy.record.xsd', f'{self.style}.xsd')
    
    @property
    def id(self):
        return self.__id

    @property
    def key(self):
        return self.__key

    @property
    def sourcename(self):
        return self.__sourcename

    @property
    def sourcelink(self):
        return self.__sourcelink    

    @property
    def composition(self):
        return self.__composition

    @property
    def symbols(self):
        return self.__symbols

    @property
    def natoms(self):
        return self.__natoms

    @property
    def natypes(self):
        return self.__natypes

    @property
    def crystalfamily(self):
        return self.__crystalfamily

    @property
    def a(self):
        return self.__a

    @property
    def b(self):
        return self.__b

    @property
    def c(self):
        return self.__c

    @property
    def alpha(self):
        return self.__alpha

    @property
    def beta(self):
        return self.__beta

    @property
    def gamma(self):
        return self.__gamma

    @property
    def ucell(self):
        if self.__ucell is None:
            self.__ucell = System(model=self.model)
        return self.__ucell

    def build_model(self):
        return deepcopy(self.model)

    def load_model(self, model, name=None):
        super().load_model(model, name=name)        
        crystal = self.model[modelroot]
        
        self.__key = crystal['key']
        self.__id = crystal['id']
        self.__sourcename = crystal['source']['name']
        self.__sourcelink = crystal['source']['link']
        
        self.__symbols = crystal['system-info'].aslist('symbol')
        self.__composition = crystal['system-info']['composition']
        self.__crystalfamily = crystal['system-info']['cell']['crystal-family']
        self.__natypes = crystal['system-info']['cell']['natypes']
        self.__a = crystal['system-info']['cell']['a']
        self.__b = crystal['system-info']['cell']['b']
        self.__c = crystal['system-info']['cell']['c']
        self.__alpha = crystal['system-info']['cell']['alpha']
        self.__beta = crystal['system-info']['cell']['beta']
        self.__gamma = crystal['system-info']['cell']['gamma']

        self.__natoms = crystal['atomic-system']['atoms']['natoms']

        self.__ucell = None

        # Set name as id if no name given
        try:
            self.name
        except:
            self.name = self.id

    def metadata(self):
        """
        Converts the structured content to a simpler dictionary.
        
        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        params = {}
        params['name'] = self.name
        params['key'] = self.key
        params['id'] = self.id
        params['sourcename'] = self.sourcename
        params['sourcelink'] = self.sourcelink

        params['crystalfamily'] = self.crystalfamily
        params['natypes'] = self.natypes
        params['symbols'] = self.symbols
        params['composition'] = self.composition

        params['a'] = self.a
        params['b'] = self.b
        params['c'] = self.c
        params['alpha'] = self.alpha
        params['beta'] = self.beta
        params['gamma'] = self.gamma
        params['natoms'] = self.natoms

        return params

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None,
                     id=None, sourcename=None,
                     sourcelink=None, crystalfamily=None, composition=None,
                     symbols=None, natoms=None, natypes=None):

        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.str_match.pandas(dataframe, 'key', key)
            &query.str_match.pandas(dataframe, 'id', id)
            &query.str_match.pandas(dataframe, 'sourcename', sourcename)
            &query.str_match.pandas(dataframe, 'sourcelink', sourcelink)
            &query.str_match.pandas(dataframe, 'crystalfamily', crystalfamily)
            &query.str_match.pandas(dataframe, 'composition', composition)
            &query.in_list.pandas(dataframe, 'symbols', symbols)
            &query.str_match.pandas(dataframe, 'natoms', natoms)
            &query.str_match.pandas(dataframe, 'natypes', natypes)
        )
        return matches

    @staticmethod
    def mongoquery(name=None, key=None,
                   id=None, sourcename=None,
                   sourcelink=None, crystalfamily=None, composition=None,
                   symbols=None, natoms=None, natypes=None):

        mquery = {}
        query.str_match.mongo(mquery, f'name', name)
        root = f'content.{modelroot}'

        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_match.mongo(mquery, f'{root}.source.name', sourcename)
        query.str_match.mongo(mquery, f'{root}.sourcelink', sourcelink)
        query.str_match.mongo(mquery, f'{root}.system-info.cell.crystal-family', crystalfamily)
        query.str_match.mongo(mquery, f'{root}.system-info.cell.composition', composition)
        query.in_list.mongo(mquery, f'{root}.system-info.symbol', symbols)
        query.str_match.mongo(mquery, f'{root}.atomic-system.atoms.natoms', natoms)
        query.str_match.mongo(mquery, f'{root}.system-info.cell.natypes', natypes)

        return mquery

    @staticmethod
    def cdcsquery(key=None, id=None, sourcename=None,
                  sourcelink=None, crystalfamily=None, composition=None,
                  symbols=None, natoms=None, natypes=None):

        mquery = {}
        root = modelroot
        
        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_match.mongo(mquery, f'{root}.source.name', sourcename)
        query.str_match.mongo(mquery, f'{root}.sourcelink', sourcelink)
        query.str_match.mongo(mquery, f'{root}.system-info.cell.crystal-family', crystalfamily)
        query.str_match.mongo(mquery, f'{root}.system-info.cell.composition', composition)
        query.in_list.mongo(mquery, f'{root}.system-info.symbol', symbols)
        query.str_match.mongo(mquery, f'{root}.atomic-system.atoms.natoms', natoms)
        query.str_match.mongo(mquery, f'{root}.system-info.cell.natypes', natypes)

        return mquery