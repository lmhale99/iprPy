from __future__ import print_function
from io import BytesIO

from DataModelDict import DataModelDict as DM

import numpy as np

import pandas as pd

from .records import records_dict

def record_styles():
    """Returns a list of the styles of the loaded calculations."""
    return records_dict.keys()
    
def buildmodel(style, script, input_dict, results_dict=None):
    """Generates a DataModelDict instance of the record style"""
    
    try:
        r_module = records_dict[style]
    except KeyError:
            raise KeyError('No record style ' + style + ' imported')
    try:        
        buildmodel = r_module.buildmodel
    except:
        raise AttributeError('buildmodel not defined for record style ' + style)
    else:
        return buildmodel(script, input_dict, results_dict=results_dict)
    
class Record(object):
    """Class for handling different record styles in the same fashion"""
    
    def __init__(self, style, name, content):
        #Check if calculation style exists
        try:
            self.__r_module = records_dict[style]
        except KeyError:
            raise KeyError('No record style ' + style + ' imported')
        
        self.__style = style
        self.__name = name
        self.__content = content
    
    def __str__(self):
        return self.name + ' (' + self.style + ')'
    
    @property
    def style(self):
        return self.__style
        
    @property
    def name(self):
        return self.__name
    
    @property
    def content(self):
        return self.__content
        
    @content.setter
    def content(self, value):
        self.__content = value
          
    def todict(self, **kwargs):
        """Converts an xml record to a flat dictionary"""
        
        try: 
            todict = self.__r_module.todict
        except:
            raise AttributeError('Record (' + self.style + ') has no attribute todict')
        else:
            return todict(self.content, **kwargs)    
    
    @property
    def schema(self):
        """Returns the path to the .xsd file for the named record."""
        
        try: 
            schema = self.__r_module.schema
        except AttributeError:
            raise AttributeError('Record (' + self.style + ') has no attribute schema') 
        else:
            return schema()
            
    @property
    def compare_terms(self):
        """Returns the list of default string and int terms used for comparisons."""
        
        try: 
            compare_terms = self.__r_module.compare_terms
        except AttributeError:
            raise AttributeError('Record (' + self.style + ') has no attribute compare_terms') 
        else:
            return compare_terms()
            
    @property
    def compare_fterms(self):
        """Returns the list of default float terms used for comparisons."""
        
        try: 
            compare_fterms = self.__r_module.compare_fterms
        except AttributeError:
            raise AttributeError('Record (' + self.style + ') has no attribute compare_fterms') 
        else:
            return compare_fterms()
            
    def isnew(self, record_df=None, record_list=None, database=None, terms=None, fterms=None, atol=0.0, rtol=1e-8):
        """
        Determine if a matching record already exists in a database, list, or 
        DataFrame of records.
        
        Keyword Arguments:
        record_df -- pandas.DataFrame of records of the record's style. This should 
                     be built by using the Record.todict(full=False, flat=True) 
                     method on every record contained within.
        record_list -- list of records of the record's style.
        database -- iprPy.Database containing records of record's style.
        terms -- list of integer and string terms to include in comparison. If not 
                 given, will use default compare_terms list for the record style.
        fterms -- list of float terms to include in comparison. If not given, will 
                  use default compare_fterms list for the record style.
        atol -- absolute tolerance to use in comparing fterms. Default value is 0.0.
        rtol -- relative tolerance to use in comparing fterms. Default value is 1e-8.
        """
        
        # Convert database to record_list
        if database is not None:
            assert record_df is None, 'record_df and database cannot both be provided'
            assert record_list is None, 'record_list and database cannot both be provided'
            
            record_list = database.get_records(style=self.style)
        
        # Convert record_list to record_df
        if record_list is not None:
            assert record_df is None, 'record_df and record_list cannot both be provided'
            
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
                test_df = test_df[np.isclose(test_df[fterm], record_dict[fterm])]
       
            # Return True if no matching records remain
            if len(test_df) == 0:
                return True
        
        # Return False indicating that there are matches
        return False