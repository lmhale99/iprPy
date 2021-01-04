# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

__all__ = ['defect']

def defect(database, keys, content_dict=None, record=None, query=None, **kwargs):

    # Initialize inputs and content dict
    if content_dict is None:
        content_dict = {}

    # Initialize input and search for defect keys
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
    
    # Check that all necessary defect keys are found
    if file_key is None:
        raise KeyError('No <defect>_file key found')
    if content_key is None:
        raise KeyError('No <defect>_content key found')
    if family_key is None:
        raise KeyError('No <defect>_family key found')

    defects, defect_df = database.get_records(style=record, return_df=True,
                                              query=query, **kwargs)
    print(len(defect_df), 'matching defects')
    if len(defect_df) == 0:
        return inputs, content_dict
 
    # Generate 
    for i in defect_df.index:
        defect_series = defect_df.loc[i]
        defect = defects[i]
        content_dict[defect.name] = defect.content

        for key in keys:
            if key == file_key:
                inputs[key].append(f'{defect.name}.json')
            elif key == content_key:
                inputs[key].append(f'record {defect.name}')
            elif key == family_key:
                inputs[key].append(defect_series.family)
            else:
                inputs[key].append('')
    
    return inputs, content_dict