# coding: utf-8
def read_calc_file(filename, filedict):
    """
    Utility function for reading the contents of required calculation files, whether
    the calculation was called using the script or through an iprPy Calculation
    object.

    Parameters
    ----------
    filename : str
        The name of the file to read/get content for.
    filedict : dict
        Should be empty if calculation is called by script, and should have all
        file names and contents if calculation is called through iprPy.

    Returns
    -------
    str
        The file's contents, either by reading the file or from filedict 
    """
    
    if filename in filedict:
        return filedict[filename]
    else:
        with open(filename) as f:
            return f.read()