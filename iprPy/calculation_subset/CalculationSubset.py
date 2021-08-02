class CalculationSubset():
    """
    A CalcRecordSubset helps define common sets of calculation record fields
    that are shared across multiple calculation record styles.
    """

############################# Core properties #################################

    def __init__(self, parent, prefix='', templateheader=None,
                 templatedescription=None):
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
            a single record.
        templateheader : str, optional
            An alternate header to use in the template file for the subset.
        templatedescription : str, optional
            An alternate description of the subset for the templatedoc.
        """
        # Get module information for current class
        if self.__module__ == __name__:
            raise TypeError("Don't use Subset itself, only use derived classes")
        
        self.__parent = parent
        self.__prefix = prefix
        self._template_init(templateheader=templateheader,
                            templatedescription=templatedescription)

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

    def _template_init(self, templateheader=None, templatedescription=None):
        """
        Sets the template header and description values.

        Parameters
        ----------
        templateheader : str, optional
            An alternate header to use in the template file for the subset.
        templatedescription : str, optional
            An alternate description of the subset for the templatedoc.
        """
        self.__templateheader = templateheader
        self.__templatedescription = templatedescription

    @property
    def templatekeys(self):
        """dict : The subset-specific input keys and their descriptions."""
        return {}

    @property
    def templateheader(self):
        """str : The header to use in the template file for the subset"""
        return self.__templateheader
    
    @property
    def templatedescription(self):
        """str : Provides a description of the subset for the templatedoc."""
        return self.__templatedescription

    @property
    def template(self):
        """str : The input file template lines for the subset."""

        # Specify keys to include
        keys = self._pre(list(self.templatekeys.keys()))
        
        # Define lines and specify content header
        lines = [f'# {self.templateheader}']

        # Build input template lines
        for key in keys:
            spacelen = 32 - len(key)
            if spacelen < 1:
                spacelen = 1
            space = ' ' * spacelen
            lines.append(f'{key}{space}<{key}>')
        
        # Join and return lines
        return '\n'.join(lines) + '\n'

    @property
    def templatedoc(self):
        """str : The documentation for the template lines for this subset."""

        # Define lines and specify content header and description
        lines = [f'## {self.templateheader}', '', self.templatedescription, '']

        # Build lines for each template key
        for key, doc in self.templatekeys.items():
            lines.append(f'- __{self._pre(key)}__: {doc}')

        # Join and return lines
        return '\n'.join(lines) + '\n'

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