# coding: utf-8

# iprPy imports
from . import recordmanager, calculationmanager, databasemanager

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
