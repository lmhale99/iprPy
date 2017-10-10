from __future__ import division, absolute_import, print_function

from io import BytesIO

from DataModelDict import DataModelDict as DM

import numpy as np

import pandas as pd

from .records import records_dict

__all__ = ['record_styles', 'buildmodel', 'Record']

def record_styles():
    """
    Returns
    -------
    list of str
        All record styles successfully loaded.
    """
    return records_dict.keys()
    
def buildmodel(style, script, input_dict, results_dict=None):
    """
    Builds a data model of the specified record style based on input (and
    results) parameters.
    
    Parameters
    ----------
    style : str
        The record style to use.
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
    KeyError
        If the record style is not available.
    AttributeError
        If buildmodel is not defined for record style.
    """
    
    try:
        r_module = records_dict[style]
    except KeyError:
            raise KeyError('No record style ' + style + ' imported')
    try:        
        buildmodel = r_module.buildmodel
    except:
        raise AttributeError('buildmodel not defined for record style '
                             + style)
    else:
        return buildmodel(script, input_dict, results_dict=results_dict)
    
class Record(object):
    """
    Class for handling different record styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.records submodule.
    """
    
    def __init__(self, style, name, content):
        """
        Initializes a Record object for a given style.
        
        Parameters
        ----------
        style : str
            The record style.
        name : str
            The unique name to assign to the record.
        content : str
            The content of the record as an XML formatted str.
        
        Raises
        ------
        KeyError
            If the record style is not available.
        """
        
        
        # Check if record style exists
        try:
            self.__r_module = records_dict[style]
        except KeyError:
            raise KeyError('No record style ' + style + ' imported')
        
        self.__style = style
        self.__name = name
        self.__content = content
    
    def __str__(self):
        """
        Returns
        -------
        str
            The string representation of the record: <name> (<style>).
        """
        return self.name + ' (' + self.style + ')'
    
    @property
    def style(self):
        """str: The records's style."""
        return self.__style
        
    @property
    def name(self):
        """str: The records's name."""
        return self.__name
    
    @property
    def content(self):
        """
        str: The record's XML-formatted content. Can be set directly.
        """
        return self.__content
        
    @content.setter
    def content(self, value):
        self.__content = value
          
    def todict(self, full=True, flat=False):
        """
        Converts the XML content to a dictionary.
        
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
        
        try: 
            todict = self.__r_module.todict
        except:
            raise AttributeError('Record (' + self.style 
                                 + ') has no attribute todict')
        else:
            return todict(self.content, full=full, flat=flat)
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        
        try: 
            schema = self.__r_module.schema
        except AttributeError:
            raise AttributeError('Record (' + self.style 
                                 + ') has no attribute schema')
        else:
            return schema()

    @property
    def compare_terms(self):
        """
        list of str: The default terms used by isnew() for comparisons.
        """
        
        try: 
            compare_terms = self.__r_module.compare_terms
        except AttributeError:
            raise AttributeError('Record (' + self.style
                                 + ') has no attribute compare_terms')
        else:
            return compare_terms()
            
    @property
    def compare_fterms(self):
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        
        try: 
            compare_fterms = self.__r_module.compare_fterms
        except AttributeError:
            raise AttributeError('Record (' + self.style
                                 + ') has no attribute compare_fterms')
        else:
            return compare_fterms()
            
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