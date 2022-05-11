from yabadaba import databasemanager

from .IprPyDatabase import IprPyDatabase

# Extend the yabadaba LocalDatabase to include IprPyDatabase operations
class LocalDatabase(databasemanager.get_class('local'), IprPyDatabase):
    pass