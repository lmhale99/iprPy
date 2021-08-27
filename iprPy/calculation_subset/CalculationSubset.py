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
        """Adds prefix to a key or list of keys"""
        if isinstance(keys, str):
            return f'{self.prefix}{keys}'
        else:
            return [f'{self.prefix}{key}' for key in keys]

    @property
    def keyset(self):
        """list : The input keyset for preparing."""
        return self._pre(self.preparekeys)

    @property
    def keymap(self):
        """dict : Maps the keys to the basekeys"""
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

    def set_values(self, **kwargs):
        pass

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        """str : The root element name for the subset terms."""
        baseroot = ''
        return f'{self.modelprefix}{baseroot}'

    @property
    def modelprefix(self):
        """str: The prefix added to the model root for the subset."""
        return self.prefix.replace('_', '-')

    def load_model(self, model):
        """Loads subset attributes from an existing model."""
        pass

    def build_model(self, model, **kwargs):
        """
        Adds the subset model to the parent model.
        
        Parameters
        ----------
        model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        kwargs : any
            Any options to pass on to dict_insert that specify where the subset
            content gets added to in the parent model.
        """
        pass

    def mongoquery(self, **kwargs):
        """
        Generate a query to parse records with the subset from a Mongo-style
        database.
        
        Parameters
        ----------
        kwargs : any
            The parent query terms and values ignored by the subset.

        Returns
        -------
        dict
            The Mongo-style find query terms.
        """
        # Init query and set root paths
        mquery = {}
        parentroot = f'content.{self.parent.modelroot}'
        root = f'{parentroot}.{self.modelroot}'
        
        # Build query terms

        # Return query dict
        return mquery

    def cdcsquery(self, **kwargs):
        """
        Generate a query to parse records with the subset from a CDCS-style
        database.
        
        Parameters
        ----------
        kwargs : any
            The parent query terms and values ignored by the subset.
        
        Returns
        -------
        dict
            The CDCS-style find query terms.
        """
        # Init query and set root paths
        mquery = {}
        parentroot = {self.parent.modelroot}
        root = f'{parentroot}.{self.modelroot}'
        
        # Build query terms

        # Return query dict
        return mquery

########################## Metadata interactions ##############################

    def metadata(self, meta):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        meta : dict
            The dictionary to add the subset content to
        """
        pass

    def pandasfilter(self, dataframe, **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
        kwargs : any
            The parent query terms and values ignored by the subset.

        Returns
        -------
        pandas.Series of bool
            True for each entry where all filter terms+values match, False for
            all other entries.
        """
        return dataframe.apply(lambda series:True, axis=1)

########################### Calculation interactions ##########################
    
    def calc_inputs(self, input_dict):
        """
        Generates calculation function input parameters based on the values
        assigned to attributes of the subset.

        Parameters
        ----------
        input_dict : dict
            The dictionary of input parameters to add subset terms to.
        """
        pass