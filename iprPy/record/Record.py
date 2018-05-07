# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import sys

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

class Record(object):
    """
    Class for handling different record styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.records submodule.
    """
    
    def __init__(self, name=None, content=None):
        """
        Initializes a Record object for a given style.
        
        Parameters
        ----------
        name : str, optional
            The unique name to assign to the record.
        content : str, file-like object, DataModelDict
            The content of the record as an XML formatted str.
        """
        # Get module information for current class
        self_module = sys.modules[self.__module__]
        self.__mod_file = self_module.__file__
        self.__mod_name = self_module.__name__
        if self.__mod_name == 'iprPy.record.Record':
            raise TypeError("Don't use Record itself, only use derived classes")
        
        self.name = name
        self.content = content
    
    def __str__(self):
        """
        Returns
        -------
        str
            The string representation of the record.
        """
        return 'record style ' + self.style + ' named ' + self.name
    
    @property
    def style(self):
        """str: The record style"""
        pkgname = self.__mod_name.split('.')
        return pkgname[2]
    
    @property
    def directory(self):
        """str: The path to the record's directory"""
        return os.path.dirname(os.path.abspath(self.__mod_file))
    
    @property
    def name(self):
        """str: The record's name."""
        if self.__name is not None:
            return self.__name
        else:
            raise AttributeError('name not set')
    
    @name.setter
    def name(self, value):
        if value is not None:
            self.__name = str(value)
        else:
            self.__name = None
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        raise AttributeError('contentroot not defined for Record style')
        
    @property
    def content(self):
        """
        DataModelDict: The record's content.
        """
        if self.__content is not None:
            return self.__content
        else:
            raise AttributeError('content not set')
    
    @content.setter
    def content(self, value):
        if value is not None:
            value = DM(value)
            if len(value.keys()) == 1 and self.contentroot in value:
                self.__content = DM(value)
            else:
                raise ValueError('Invalid root element for content')
        else:
            self.__content = None
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        raise AttributeError('schema not defined for Record style')
    
    @property
    def compare_terms(self):
        """
        list of str: The default terms used by isnew() for comparisons.
        """
        raise AttributeError('compare_terms not defined for Record style')
    
    @property
    def compare_fterms(self):
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        raise AttributeError('compare_fterms not defined for Record style')
    
    def buildcontent(self, script, input_dict, results_dict=None):
        """
        Builds a data model of the specified record style based on input (and
        results) parameters.
        
        Parameters
        ----------
        script : str
            The name of the calculation script used.
        input_dict : dict
            Dictionary of all input parameter terms.
        results_dict : dict, optional
            Dictionary containing any results produced by the calculation.
            
        Returns
        -------
        DataModelDict
            Data model consistent with the record's schema format.
        
        Raises
        ------
        AttributeError
            If buildcontent is not defined for record style.
        """
        raise AttributeError('buildcontent not defined for Record style')
    
    def todict(self, full=True, flat=False):
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
        
        Raises
        ------
        AttributeError
            If todict is not defined for record style.
        """
        raise AttributeError('todict not defined for Record style')
    
    def isvalid(self):
        """
        Looks at the values of elements in the record to determine if the
        associated calculation would be a valid one to run.
        
        Returns
        -------
        bool
            True if element combinations are valid, False if not.
        """
        # Default Record.isvalid() returns True
        return True
    
    def isnew(self, record_df=None, record_list=None, database=None,
              terms=None, fterms=None, atol=0.0, rtol=1e-8):
        """
        Checks the record versus a database, list of records, or DataFrame of
        records to see if any records exists with matching terms and fterms.
        
        Parameters
        ----------
        record_df : pandas.DataFrame, optional
            DataFrame to compare record againts.  record_df must be built by
            converting records to dictionaries using Record.todict(full=False,
            flat=True), then converting the list of dictionaries to a
            DataFrame.  Either record_df, record_list or database must be given.
        record_list : list of iprPy.Records, optional
            List of Records to compare against.  Either record_df, record_list
            or database must be given.
        database : iprPy.Database, optional
            Database containing records of record.style to compare against.
            All records of record.style contained in the database will be
            checked.  Either record_df, record_list or database must be given.
        terms : list of str, optional
            The keys of the dictionary produced by Record.todict(full=False,
            flat=True) to check for equivalency, i.e. use == comparisons for
            terms with str and int values. If not given, will use the record
            style's compare_terms.
        fterms : list of str, optional
            The keys of the dictionary produced by Record.todict(full=False,
            flat=True) to check for approximately equal values, i.e. use
            numpy.isclose() for terms with float values. If not given, will
            use the record style's compare_fterms.
        atol : float, optional
            The absolute tolerance to use in numpy.isclose() for comparing
            fterms (Default value is 0.0).
        rtol : float, optional
            The relative tolerance to use in numpy.isclose() for comparing
            fterms (Default value is 1e-8).
        
        Returns
        -------
        bool
        
        Raises
        ------
        ValueError
            If more than one of record_df, record_list, and database are 
            given.
        """
        
        # Convert database to record_list
        if database is not None:
            if record_df is not None:
                raise ValueError('record_df and database cannot both be provided')
            if record_list is not None:
                raise ValueError('record_list and database cannot both be provided')
            
            record_list = database.get_records(style=self.style)
        
        # Convert record_list to record_df
        if record_list is not None:
            if record_df is not None:
                raise ValueError('record_df and record_list cannot both be provided')
            
            record_df = []
            for r in record_list:
                record_df.append(r.todict(full=False, flat=True))
            record_df = pd.DataFrame(record_df)
        
        # Return True if no records in record_df
        if len(record_df) == 0:
            return True
        
        # Get default terms and fterms lists
        if terms is None:
            terms = self.compare_terms
        if fterms is None:
            fterms = self.compare_fterms
        
        # Convert record to dictionary
        record_dict = self.todict(full=False, flat=True)
        
        # Define slice for comparison testing
        test_df = record_df
        
        # Compare string and int terms
        for term in terms:
            # Compare total size multipliers (high-low)
            if   term == 'a_mult':
                test_df = test_df[test_df['a_mult2']-test_df['a_mult1'] == record_dict['a_mult2']-record_dict['a_mult1']]
            elif term == 'b_mult':
                test_df = test_df[test_df['b_mult2']-test_df['b_mult1'] == record_dict['b_mult2']-record_dict['b_mult1']]
            elif term == 'c_mult':
                test_df = test_df[test_df['c_mult2']-test_df['c_mult1'] == record_dict['c_mult2']-record_dict['c_mult1']]
            
            # Compare non-NaN terms
            elif term in record_dict and pd.notnull(record_dict[term]):
                test_df = test_df[test_df[term] == record_dict[term]]
            
            # Return True if no matching records remain
            if len(test_df) == 0:
                return True
        
        # Compare float terms
        for fterm in fterms:
            # Compare non-NaN terms
            if fterm in record_dict and pd.notnull(record_dict[fterm]):
                test_df = test_df[np.isclose(test_df[fterm],
                                  record_dict[fterm])]
       
            # Return True if no matching records remain
            if len(test_df) == 0:
                return True
        
        # Return False indicating that there are matches
        return False
    
    def match_df(self, record_df=None, record_list=None, database=None,
              terms=None, fterms=None, atol=0.0, rtol=1e-8):
        """
        Checks the record versus a database, list of records, or DataFrame of
        records to see if any records exists with matching terms and fterms.
        
        Parameters
        ----------
        record_df : pandas.DataFrame, optional
            DataFrame to compare record againts.  record_df must be built by
            converting records to dictionaries using Record.todict(full=False,
            flat=True), then converting the list of dictionaries to a
            DataFrame.  Either record_df, record_list or database must be given.
        record_list : list of iprPy.Records, optional
            List of Records to compare against.  Either record_df, record_list
            or database must be given.
        database : iprPy.Database, optional
            Database containing records of record.style to compare against.
            All records of record.style contained in the database will be
            checked.  Either record_df, record_list or database must be given.
        terms : list of str, optional
            The keys of the dictionary produced by Record.todict(full=False,
            flat=True) to check for equivalency, i.e. use == comparisons for
            terms with str and int values. If not given, will use the record
            style's compare_terms.
        fterms : list of str, optional
            The keys of the dictionary produced by Record.todict(full=False,
            flat=True) to check for approximately equal values, i.e. use
            numpy.isclose() for terms with float values. If not given, will
            use the record style's compare_fterms.
        atol : float, optional
            The absolute tolerance to use in numpy.isclose() for comparing
            fterms (Default value is 0.0).
        rtol : float, optional
            The relative tolerance to use in numpy.isclose() for comparing
            fterms (Default value is 1e-8).
        
        Returns
        -------
        bool
        
        Raises
        ------
        ValueError
            If more than one of record_df, record_list, and database are 
            given.
        """
        
        # Convert database to record_list
        if database is not None:
            if record_df is not None:
                raise ValueError('record_df and database cannot both be provided')
            if record_list is not None:
                raise ValueError('record_list and database cannot both be provided')
            
            record_list = database.get_records(style=self.style)
        
        # Convert record_list to record_df
        if record_list is not None:
            if record_df is not None:
                raise ValueError('record_df and record_list cannot both be provided')
            
            record_df = []
            for r in record_list:
                record_df.append(r.todict(full=False, flat=True))
            record_df = pd.DataFrame(record_df)
            
        # Return True if no records in record_df
        if len(record_df) == 0:
            return True
        
        # Get default terms and fterms lists
        if terms is None:
            terms = self.compare_terms
        if fterms is None:
            fterms = self.compare_fterms
        
        # Convert record to dictionary
        record_dict = self.todict(full=False, flat=True)

        # Define slice for comparison testing
        test_df = record_df
        
        # Compare string and int terms
        for term in terms:
            # Compare total size multipliers (high-low)
            if   term == 'a_mult':
                test_df = test_df[test_df['a_mult2']-test_df['a_mult1'] == record_dict['a_mult2']-record_dict['a_mult1']]
            elif term == 'b_mult':
                test_df = test_df[test_df['b_mult2']-test_df['b_mult1'] == record_dict['b_mult2']-record_dict['b_mult1']]
            elif term == 'c_mult':
                test_df = test_df[test_df['c_mult2']-test_df['c_mult1'] == record_dict['c_mult2']-record_dict['c_mult1']]
            
            # Compare non-NaN terms
            elif term in record_dict and pd.notnull(record_dict[term]):
                test_df = test_df[test_df[term] == record_dict[term]]
            
            # Return True if no matching records remain
            if len(test_df) == 0:
                return test_df
        
        # Compare float terms
        for fterm in fterms:
            # Compare non-NaN terms
            if fterm in record_dict and pd.notnull(record_dict[fterm]):
                test_df = test_df[np.isclose(test_df[fterm],
                                  record_dict[fterm])]
            
            # Return True if no matching records remain
            if len(test_df) == 0:
                return test_df
        
        # Return False indicating that there are matches
        return test_df