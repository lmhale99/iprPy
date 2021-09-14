import sys

from .reset_orphans import reset_orphans
from .prepare import prepare
from .master_prepare import master_prepare
from .runner import runner
from .IprPyDatabase import IprPyDatabase

from datamodelbase.tools import ModuleManager
databasemanager = ModuleManager('Database')
from .load_database import load_database

__all__ = ['Database', 'databasemanager', 'load_database']

# Import LocalDatabase
try:
    from datamodelbase.database import LocalDatabase as LocalParent
except Exception as e:
    databasemanager.failed_styles['local'] = '%s: %s' % sys.exc_info()[:2]
else:
    class LocalDatabase(LocalParent, IprPyDatabase):
        pass
    databasemanager.loaded_styles['local'] = LocalDatabase
    __all__.append('LocalDatabase')

# Import MongoDatabase
try:
    from datamodelbase.database import MongoDatabase as MongoParent
except Exception as e:
    databasemanager.failed_styles['mongo'] = '%s: %s' % sys.exc_info()[:2]
else:
    class MongoDatabase(MongoParent, IprPyDatabase):
        pass
    databasemanager.loaded_styles['mongo'] = MongoDatabase
    __all__.append('MongoDatabase')

# Import CDCSDatabase
try:
    from datamodelbase.database import CDCSDatabase as CDCSParent
except Exception as e:
    databasemanager.failed_styles['cdcs'] = '%s: %s' % sys.exc_info()[:2]
else:
    class CDCSDatabase(CDCSParent, IprPyDatabase):
        pass
    databasemanager.loaded_styles['cdcs'] = CDCSDatabase
    __all__.append('CDCSDatabase')

__all__.sort()