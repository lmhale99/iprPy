class CalculationSubset():
    """
    A CalcRecordSubset helps define common sets of calculation record fields
    that are shared across multiple calculation record styles.
    """

############################# Core properties #################################

    def __init__(self, parent, prefix=''):
        """
        Initializes a calculation record subset object.

        Parameters
        ----------
        parent : iprPy.calculation.Calculation
            The parent calculation object that the subset object is part of.
            This allows for the subset methods to access parameters set to the
            calculation itself or other subsets.
        prefix : str, optional
            An optional prefix to add to metadata field names to allow for
            differentiating between multiple subsets of the same style within
            a single record
        """
        # Get module information for current class
        if self.__module__ == __name__:
            raise TypeError("Don't use Subset itself, only use derived classes")
        
        self.__parent = parent
        self.__prefix = prefix

    @property
    def parent(self):
        """str: The parent calculation object for the subset."""
        return self.__parent

    @property
    def prefix(self):
        """str: The prefix added before metadata field names."""
        return self.__prefix

    def _pre(self, keys):
        """
        Adds prefix to a key or list of keys
        """
        if isinstance(keys, str):
            return f'{self.prefix}{keys}'
        else:
            return [f'{self.prefix}{key}' for key in keys]

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

####################### Parameter file interactions ###########################

    @property
    def templateheader(self):
        """str : The default header to use in the template file for the subset"""
        return ''
    
    @property
    def templatekeys(self):
        """list : The default input keys used by the calculation."""
        return []

    def template(self, header=None):
        """str : The input file template lines for the subset."""
        # Specify default header
        if header is None:
            header = self.templateheader
        
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
        return '\n'.join(lines) + '\n\n'

    def set_values(self, input_dict, results_dict=None):
        raise NotImplementedError()

########################### Data model interactions ###########################

    @property
    def modelprefix(self):
        """str: The prefix added to the model root for the subset."""
        return self.prefix.replace('_', '-')

    def load_model(self, model):
        raise NotImplementedError()

    def build_model(self):
        raise NotImplementedError()

########################## Metadata interactions ##############################

    def metadata(self):
        raise NotImplementedError()

########################### Calculation interactions ##########################
    
    def calc_inputs(self, input_dict):
        raise NotImplementedError()