import os
import glob
from DataModelDict import DataModelDict as DM

def yield_records(lib_directory, potential='*', elements='*', system_family='*', calculation='*', record_id='*'):
    """
    Search library directory for calculation results satisfying the limiters.
    Returns record file name, and DataModelDict of the record
    
    Arguments
    lib_directory -- path to the library directory
    
    Keyword Arguments (all optional, can be singular or list/tuple)
    potential -- if given will only include records for that potential name
    elements -- if given will only include records for the specified element(s)                
    system_family -- if given will only include records for that system_family
    calculation -- if given will only include records for that calculation
    record_id -- if given will only include the record with the matching uuid
    
    Note: the searches are only operating on the library subdirectory names, but the * wildcard can be used. 
    This could cause issues with elements for single letter element names, i.e. 'H*' will return results for H and He... 
    """
    for p in iteritem(potential):
        for e in iteritem(elements):
            for s in iteritem(system_family):
                for c in iteritem(calculation):
                    for r in iteritem(record_id):
                        for record_file in glob.iglob(os.path.join(lib_directory, p, e, s, c, r)):
                            if os.path.splitext(record_file)[1].lower() in ['.xml', '.json']:
                                with open(record_file) as f:
                                    yield record_file, DM(f)
                
def iteritem(term):
    """simple function for iterating over single or multi-valued values"""
    if isinstance(term, (str, unicode)):
        yield term
    else:
        try:
            for t in term:
                yield t
        except:
            yield term