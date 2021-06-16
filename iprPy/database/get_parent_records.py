from pathlib import Path

def get_parent_records(database, record=None, name=None, style=None,
                       ancestors=False):
    """
    Returns all records that are parents to the given one.

    Parameters
    ----------
    database : iprPy.Database
        The database to search for parent records.
    record : iprPy.Record, optional
        The record whose parents are to be found.
    name : str, optional
        Record name for identifying a record to load and check for parents.
        Cannot be given with record. 
    style : str, optional
        Record style associated with the record identified by name.
        Cannot be given with record. 
    ancestors : bool, optional
        If True, then the identified parents will be recursively searched to
        identify all ancestors of the current record.  Default value is False,
        meaning that only direct parents are returned.

    Returns
    -------
    list of iprPy.Record
        All the parent records 
    """
    # Get child record if needed
    if record is None:
        record = database.get_record(name=name, style=style) 
    elif name is not None or style is not None:
        raise ValueError('record cannot be given with name/style')
    
    parents = []
    try:
        # Check if record has system-info
        model = record.build_model().find('system-info')
    except:
        pass
    else:
        # Loop over all file values in system-info
        for load_file in model.finds('file'):
            
            # See if load file is in a directory
            directory = Path(load_file).parent.stem
            if directory != '':
                # Set parentname as load_file's directory
                parentname = directory
            else:
                # Set parentname as loadfile's name
                parentname = Path(load_file).stem

            try:
                # Get parent record
                parent = database.get_record(name=parentname) 
            except:
                pass
            else:
                parents.append(parent)

                # Recursively check for ancestors
                if ancestors is True:
                    grandparents = database.get_parent_records(record=parent)
                    parents.extend(grandparents)
    
    return parents