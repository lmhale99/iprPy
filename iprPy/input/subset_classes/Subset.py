# Standard Python libraries
from pathlib import Path
import sys

class Subset():
    """
    Defines interactions between subsets of calculation input keys allowing
    for common handling across multiple calculation styles
    """
    def __init__(self, prefix=''):
        """
        Initializes a Calculation object for a given style.

        Parameters
        ----------
        prefix : str, optional
            An optional prefix to add to the keywords.
        """
        # Get module information for current class
        self_module = sys.modules[self.__module__]
        self._mod_file = self_module.__file__
        self._mod_name = self_module.__name__
        if self._mod_name == 'iprPy.input.subset_classes.Subset':
            raise TypeError("Don't use Subset itself, only use derived classes")
        self.__prefix = prefix

    @property
    def style(self):
        """
        str: The calculation style
        """
        pkgname = self._mod_name.split('.')
        return pkgname[3]

    @property
    def directory(self):
        """str: The path to the subset's directory"""
        return Path(self._mod_file).resolve().parent

    @property
    def prefix(self):
        """
        str: The calculation style
        """
        return self.__prefix

    @property
    def templatekeys(self):
        """
        list : The default input keys used by the calculation.
        """
        return []
    
    @property
    def templatedoc(self):
        """str: The markdown doc describing the associated input parameters"""
        with open(Path(self.directory, 'parameters.md')) as f:
            return f.read()

    @property
    def preparekeys(self):
        """
        list : The default input keys used by prepare.
        """
        return self.templatekeys + []

    @property
    def interpretkeys(self):
        """
        list : The default input keys accessed when interpreting input files.
        """
        return self.preparekeys + []

    @property
    def keyset(self):
        """
        list : The input keyset for preparing.
        """
        return self._pre(self.preparekeys)

    @property
    def keymap(self):
        """
        dict : Maps the keys to the basekeys 
        """
        km = {}
        for key in self.interpretkeys:
            km[key] = self._pre(key)
        return km

    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = ''
        
        # Specify keys to include
        keys = self._pre(self.templatekeys)
        
        # Define lines and specify content header
        lines = [header]

        # Build input template lines
        for key in keys:
            spacelen = 32 - len(key)
            if spacelen < 1:
                spacelen = 1
            space = ' ' * spacelen
            lines.append(f'{key}{space}<{key}>')
        
        # Join and return lines
        return '\n'.join(lines)

    def _pre(self, keys):
        """
        Adds prefix to a key or list of keys
        """
        if isinstance(keys, str):
            return f'{self.prefix}{keys}'
        else:
            return [f'{self.prefix}{key}' for key in keys]

    def interpret(self, input_dict):
        """
        Interprets calculation parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary containing input parameter key-value pairs.
        """
        pass

    def buildcontent(self, record_model, input_dict, results_dict=None):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        record_model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        input_dict : dict
            Dictionary of all input parameter terms.
        results_dict : dict, optional
            Dictionary containing any results produced by the calculation.
        """
        pass

    def todict(self, record_model, params, full=True, flat=False):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        record_model : DataModelDict.DataModelDict
            The record content (after root element) to interpret.
        params : dict
            The dictionary to add the interpreted content to
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
        """
        pass
