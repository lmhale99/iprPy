# coding: utf-8

# https://github.com/usnistgov/yabadaba
from yabadaba.tools import ModuleManager
databasemanager = ModuleManager('Database')
#from yabadaba import databasemanager as coredatabasemanager

# Local imports
from .reset_orphans import reset_orphans
from .prepare import prepare
from .master_prepare import master_prepare
from .runner import runner, RunManager
from .IprPyDatabase import IprPyDatabase
from .load_database import load_database

__all__ = sorted(['Database', 'databasemanager', 'load_database', 'runner',
                  'RunManager', 'reset_orphans', 'prepare', 'master_prepare'])

databasemanager.import_style('local', '.LocalDatabase', __name__)
databasemanager.import_style('mongo', '.MongoDatabase', __name__)
databasemanager.import_style('cdcs', '.CDCSDatabase', __name__)

# Upgrade LocalDatabase to an IprPyDatabase
#if 'local' in coredatabasemanager.loaded_styles:
#    class LocalDatabase(coredatabasemanager.loaded_styles['local'], IprPyDatabase):
#        pass
#    databasemanager.loaded_styles['local'] = LocalDatabase
#else:
#    databasemanager.failed_styles['local'] = coredatabasemanager.failed_styles['local']

# Upgrade MongoDatabase to an IprPyDatabase
#if 'mongo' in coredatabasemanager.loaded_styles:
#    class MongoDatabase(coredatabasemanager.loaded_styles['mongo'], IprPyDatabase):
#        pass
#    databasemanager.loaded_styles['mongo'] = MongoDatabase
#else:
#    databasemanager.failed_styles['mongo'] = coredatabasemanager.failed_styles['mongo']

# Upgrade CDCSDatabase to an IprPyDatabase
#if 'cdcs' in coredatabasemanager.loaded_styles:
#    class CDCSDatabase(coredatabasemanager.loaded_styles['cdcs'], IprPyDatabase):
#        pass
#    databasemanager.loaded_styles['cdcs'] = CDCSDatabase
#else:
#    databasemanager.failed_styles['cdcs'] = coredatabasemanager.failed_styles['cdcs']