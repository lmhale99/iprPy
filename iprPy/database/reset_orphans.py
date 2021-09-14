# coding: utf-8
# Standard Python libraries
from pathlib import Path
import tarfile

from .. import load_run_directory

def reset_orphans(run_directory, orphan_directory=None):
    """
    Resets calculations that were moved to an orphan directory back to a
    run directory and removes any bid files that they contain.  Can be useful
    if connection is lost to a remote database or a runner was accidentally
    started with the wrong database.

    Parameters
    ----------
    run_directory : str
        The directory to move the orphaned calculations to.
    orphan_directory : str, optional
        The orphan directory containing archived calculation folders.  The
        default value assumes that the orphan directory is a directory named
        "orphan" that is in the same parent directory as run_directory, i.e.
        is at "../orphan" relative to run_directory.
    """
    # Check for run_directory first by name then by path
    try:
        run_directory = load_run_directory(run_directory)
    except:
        run_directory = Path(run_directory).resolve()
        if not run_directory.is_dir():
            raise ValueError('run_directory not found/set')

    # Set default orphan directory
    if orphan_directory is None:
        orphan_directory = Path(run_directory.parent, 'orphan')
        
    # Loop over tar.gz files 
    for archive in Path(orphan_directory).glob('*.tar.gz'):
        
        # Extract calc to run_directory
        tar = tarfile.open(archive)
        tar.extractall(run_directory)
        tar.close()
        archive.unlink()
        
        # Remove any bids in the calc
        calc_dir = Path(run_directory, archive.name.split('.')[0])
        for bidfile in calc_dir.glob('*.bid'):
            bidfile.unlink()