# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# iprPy imports
from ...compatibility import range

__all__ = ['defect']

def defect(database, keys, record=None, query=None, **kwargs):

    defects, defect_df = database.get_records(style=record, return_df=True,
                                           query=query, **kwargs)
    
    file_key = None
    content_key = None
    family_key = None
    inputs = {}
    for key in keys:
        inputs[key] = []
        if key[-5:] == '_file':
            if file_key is None:
                file_key = key
            else:
                raise KeyError('Multiple <defect>_file keys found')
        elif key[-8:] == '_content':
            if content_key is None:
                content_key = key
            else:
                raise KeyError('Multiple <defect>_content keys found')
        elif key[-7:] == '_family':
            if family_key is None:
                family_key = key
            else:
                raise KeyError('Multiple <defect>_family keys found')
    
    if file_key is None:
        raise KeyError('No <defect>_file key found')
    if content_key is None:
        raise KeyError('No <defect>_content key found')
    if family_key is None:
        raise KeyError('No <defect>_family key found')
    
    for i, defect_series in defect_df.iterrows():
        defect = defects[i]
        for key in keys:
            if key == file_key:
                inputs[key].append(defect.name + '.json')
            elif key == content_key:
                inputs[key].append(defect.content)
            elif key == family_key:
                inputs[key].append(defect_series.family)
            else:
                inputs[key].append('')
    
    return inputs