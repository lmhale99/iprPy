from . import recordmanager, calculationmanager, databasemanager, querymanager, valuemanager

__all__ = ['check_modules']

def check_modules():
    """
    Prints lists of the calculation, record, and database styles that were
    successfully and unsuccessfully loaded when iprPy was initialized.
    """
    databasemanager.check_styles()
    print()
    calculationmanager.check_styles()
    print()
    recordmanager.check_styles()
    print()
    querymanager.check_styles()
    print()
    valuemanager.check_styles()
    print()