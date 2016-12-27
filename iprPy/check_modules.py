from __future__ import print_function

from .calculations import failed_calculations
from .records import failed_records
from .databases import failed_databases

from . import calculation_styles
from . import record_styles
from . import database_styles

def check_modules():
    """Prints lists of sucessful and failed importing of modular components of iprPy."""
    
    print('calculations that passed import:')
    for calculation in calculation_styles():
        print(' ' + calculation)
    print('calculations that failed import:')
    for calculation in failed_calculations:
        print(' ' + calculation)
    print()
    
    print('records that passed import:')
    for record in record_styles():
        print(' ' + record)
    print('records that failed import:')
    for record in failed_records:
        print(' ' + record)
    print()

    print('databases that passed import:')
    for database in database_styles():
        print(' ' + database)
    print('databases that failed import:')
    for database in failed_databases:
        print(' ' + database)
    print()    