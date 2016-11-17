from . import get_files_in_library

from DataModelDict import DataModelDict as DM

def read_records(lib_directory, potential=['*'], symbols=['*'], prototype=['*'], calc_type=['*'], calc_id=['*']):
    """Finds and reads records in lib_directory matching the given conditions"""

    records = []
    for fname in get_files_in_library(lib_directory, potential=potential, symbols=symbols, prototype=prototype, calc_type=calc_type, calc_id=calc_id, ext=['.json', '.xml']):

        with open(fname) as f:
            model = DM(f)
        records.append({'file':fname, 'model':model})
    return records