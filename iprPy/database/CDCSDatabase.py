from yabadaba import databasemanager

from .IprPyDatabase import IprPyDatabase

# Extend the yabadaba CDCSDatabase to include IprPyDatabase operations
class CDCSDatabase(databasemanager.get_class('cdcs'), IprPyDatabase):
    pass