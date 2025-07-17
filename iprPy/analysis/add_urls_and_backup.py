# Standard Python libraries
from typing import Optional
import time

from tqdm import tqdm

import requests

from .. import load_calculation, load_database
from ..tools import dict_insert

def add_urls_and_backup(database,
                        calc_style: str,
                        base_url: str = 'https://potentials.nist.gov/pid/rest/local/potentials',
                        alt_databases: Optional[list] = None,
                        copytar: bool = True,
                        dryrun: bool = False,
                        workspace: str = 'Global Public Workspace',
                        ):
    """
    Adds the URL fields (and parent key fields) to finished/error calculations
    and copies the updated records to other databases if needed.  These two
    operations are paired together as it serves a simple and quick means of
    identifying which finished calculation records are missing from the
    public potentials.nist.gov database.

    Parameters
    ----------
    database : iprPy.database.Database
        The primary database to interact with to find calculation records to
        update with the URL and parent fields.
    calc_style : str
        The iprPy calculation style to update.
    base_url : str, optional
        The base URL to use for the URL fields.  The default value is associated
        with the potentials.nist.gov CDCS database.
    alt_databases : list or None, optional
        Any other databases (given as iprPy.database.Database objects) where
        the updated records are to be copied.  This can be used to copy to a 
        backup and/or upload the finished records to a public database.
    copytar : bool, optional
        If any alt_databases are given that are of local/mongo styles, this
        flag indicates if the associated calculation tar files are to be copied
        as well. Note that the tars will not be automatically uploaded to a
        cdcs style database. Default value is True.
    dryrun : bool, optional
        Setting this to True will return the changed records rather than
        adding/updating the records to the database(s).
    workspace : str, optional
        If any alt_databases are given that are of the cdcs style, then they
        will be assigned to this workspace.
    """
    
    # Set record_style and load calc object
    record_style = f'calculation_{calc_style}'
    calc = load_calculation(calc_style)

    # Query to get finished/error records that are missing URLs 
    if database.style == 'mongo':
        query = {
        f"content.{calc.modelroot}.URL": { "$exists": False },
        "$or": [{f"content.{calc.modelroot}.status": {"$exists": False }},
                {f"content.{calc.modelroot}.status": 'error'}]
        }
        records = database.get_records(record_style, query=query)

    else:
        raise ValueError(f'database with style {database.style} not supported!')
    
    print(len(records), 'finished/error calcs missing URL found')
    
    changed_records = add_urls_to_calculations(records)
    print(len(changed_records), 'records updated with URL fields')
    
    if dryrun:
        return changed_records
    
    save_records(changed_records, database, alt_databases=alt_databases,
                 copytar=copytar, workspace=workspace)



def add_urls_to_calculations(records: list,
                             base_url: str = 'https://potentials.nist.gov/pid/rest/local/potentials'):
    
    # Remove end slash if included
    base_url = base_url.strip('/')
    changed_records = []
    
    for record in tqdm(records):
        changed = False
        
        # Get model
        model = record.model
        calc = model[record.modelroot]
        
        # Get metadata
        meta = record.metadata()
        
        # Add primary url field
        if 'URL' not in calc:
            name = calc['key']
            url = '/'.join([base_url, name])
            dict_insert(calc, 'URL', url, after='key')
            changed = True
            
        # Add potentials urls
        if 'potential-LAMMPS' in calc:
            if 'URL' not in calc['potential-LAMMPS'] or calc['potential-LAMMPS']['URL'] == 'None':
                name = calc['potential-LAMMPS']['id']
                if '__MO_' in name:
                    name = name[-19:-4]
                url = '/'.join([base_url, name])
                dict_insert(calc['potential-LAMMPS'], 'URL', url, after='id')
                changed = True
            if 'potential' in calc['potential-LAMMPS'] and ('URL' not in calc['potential-LAMMPS']['potential'] or calc['potential-LAMMPS']['potential']['URL'] == 'None'):
                name = f"potential.{calc['potential-LAMMPS']['potential']['id']}"
                url = '/'.join([base_url, name])
                dict_insert(calc['potential-LAMMPS']['potential'], 'URL', url, after='id')
                changed = True
        
        # Add family url
        if 'system-info' in calc and 'family' in calc['system-info'] and 'family-URL' not in calc['system-info']:
            name = calc['system-info']['family']
            url = '/'.join([base_url, name])
            dict_insert(calc['system-info'], 'family-URL', url, after='family')
            changed = True
        
        # Add parent key and url
        if 'system-info' in calc and 'parent_key' in meta and 'parent-key' not in calc['system-info']:
            parent = meta['parent_key']
            url = '/'.join([base_url, parent])
            dict_insert(calc['system-info'], 'parent', parent, after='artifact')
            dict_insert(calc['system-info'], 'parent-URL', url, after='parent')
            changed = True
        
        # Add free surface url
        if 'free-surface' in calc and 'URL' not in calc['free-surface']:
            defect = calc['free-surface']['id']
            url = '/'.join([base_url, defect])
            dict_insert(calc['free-surface'], 'URL', url, after='id')
            changed = True
            
        # Add point defect url
        if 'point-defect' in calc and 'URL' not in calc['point-defect']:
            defect = calc['point-defect']['id']
            url = '/'.join([base_url, defect])
            dict_insert(calc['point-defect'], 'URL', url, after='id')
            changed = True
            
        # Add dislocation url
        if 'dislocation' in calc and 'URL' not in calc['dislocation']:
            defect = calc['dislocation']['id']
            url = '/'.join([base_url, defect])
            dict_insert(calc['dislocation'], 'URL', url, after='id')
            changed = True
            
        # Add stacking fault url
        if 'stacking-fault' in calc and 'URL' not in calc['stacking-fault']:
            defect = calc['stacking-fault']['id']
            url = '/'.join([base_url, defect])
            dict_insert(calc['stacking-fault'], 'URL', url, after='id')
            changed = True
        
        # Delete obsolete script element
        if 'script' in calc['calculation']:
            del calc['calculation']['script']

        if changed:
            changed_records.append(record)
        
    return changed_records


def save_records(records,
                 database,
                 alt_databases: Optional[list] = None,
                 copytar: bool = True,
                 workspace: str = 'Global Public Workspace'):
    """
    Saves the changed records to one or more databases.
    """

    if alt_databases is None:
        alt_databases = []

    # Set workspaces for cdcs databases - done here to reduce CDCS REST calls
    workspaces = []
    for alt_database in alt_databases:
        if alt_database.style == 'cdcs':
            workspaces.append(alt_database.cdcs.get_workspace(workspace))
        else:
            workspaces.append(None)

    for record in tqdm(records):
        
        # Copy to alt_databases first in case script crashes
        for alt_database, workspace in zip(alt_databases, workspaces):
            
            if alt_database.style == 'cdcs':
                copy_record_cdcs(alt_database, record, workspace)
            else:
                copy_record(database, alt_database, record, copytar)
                
        # Update in the primary database
        database.update_record(record=record)


def copy_record(database, alt_database, record, copytar):
    """
    Copies a record to a mongo-style database and optionally also copies the
    associated tar file if it exists.  This is a very stripped down version of
    Database.copy_records() for copying single records at a time, with
    parameters renamed for consistency with the rest of this script.
    """

    try:
        # Add new records
        alt_database.add_record(record=record)
    except:
        # Update existing records
        alt_database.update_record(record=record)

    # Copy archives
    if copytar:
        try:
            # Get tar if it exists
            tar = database.get_tar(record=record, raw=True) 
        except:
            pass
        else:
            try:
                # Copy tar over
                alt_database.add_tar(record=record, tar=tar)
            except:
                # Update existing tar
                alt_database.update_tar(record=record, tar=tar)

def copy_record_cdcs(alt_database, record, workspace):
    """
    Copy a record to a cdcs-style database.  This will repeatedly try to upload
    if there are connection issues with the database. Also, no tar uploading
    currently in place.
    """
    while True:
        try:
            # Update records that exist
            alt_database.update_record(record=record, workspace=workspace)
        
        except ValueError:
            try:
                # Add records that don't exist (update throws ValueError)
                alt_database.add_record(record=record, workspace=workspace)
            
            except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
                # Sleep for one minute and then try again
                time.sleep(60)
            
            else:
                # Break while loop if add was successful
                break 
                
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
            # Sleep for one minute and then try again
            time.sleep(60)
        
        else:
            # Break while loop if update was successful
            break
