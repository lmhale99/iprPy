# coding: utf-8
# Standard Python libraries
from pathlib import Path
from copy import deepcopy

from datamodelbase import query

from DataModelDict import DataModelDict as DM

from atomman import __version__ as atomman_version

from .. import __version__ as iprPy_version
from ..input import parse
import uuid

from ..record import Record

class Calculation(Record):
    """Base class for managing calculations"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """
        Initializes a Calculation object for a given style.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Record content in data model format to read in.  Cannot be given
            with params.
        name : str, optional
            The name to use for saving the record.  By default, this should be
            the calculation's key.
        params : str, file-like object or dict, optional
            Calculation input parameters or input parameter file.  Cannot be
            given with model.
        **kwargs : any
            Any other core Calculation record attributes to set.  Cannot be
            given with model.
        """
        # Throw error for default class
        if self.__module__ == __name__:
            raise TypeError("Don't use Calculation itself, only use derived classes")
        
        # Check for params
        if params is not None and model is not None:
                raise ValueError('model and params cannot both be given')

        # Set style and parent_module
        module_terms = self.__module__.split('.')
        self.__parent_module = '.'.join(module_terms[:-1])
        self.__calc_style = module_terms[-2]

        # Call Record's init
        super().__init__(model=model, name=name, **kwargs)

        # Load parameters if given
        if params is not None:
            self.load_parameters(params, key=kwargs.get('key', None))

############################### Class attributes ##############################

    @property
    def style(self):
        """str: The record style"""
        return f'calculation_{self.calc_style}'

    @property
    def calc_style(self):
        """str : The calculation style"""
        return self.__calc_style

    @property
    def key(self):
        return self.__key
    
    @property
    def iprPy_version(self):
        return self.__iprPy_version

    @property
    def atomman_version(self):
        return self.__atomman_version

    @property
    def script(self):
        return self.__script

    @property
    def branch(self):
        return self.__branch
    
    @property
    def status(self):
        return self.__status

    @property
    def error(self):
        return self.__error

    @property
    def parent_module(self):
        return self.__parent_module

    def set_values(self, name=None, **kwargs):
        """
        Used to set initial common values for the calculation.
        """
        self.__iprPy_version = kwargs.get('iprPy_version', iprPy_version)
        self.__atomman_version = kwargs.get('atomman_version', atomman_version)
        self.__key = kwargs.get('key', str(uuid.uuid4()))
        self.__script = f'calc_{self.calc_style}' # Obsolete....
        self.__branch = kwargs.get('branch', 'main')
        self.__status = kwargs.get('status', 'not calculated')
        self.__error = kwargs.get('error', None)

        if name is None:
            self.name = self.key
        else:
            self.name = name

    def isvalid(self):
        """
        Looks at the set atttributes to determine if the associated calculation
        would be a valid one to run.
        
        Returns
        -------
        bool
            True if element combinations are valid, False if not.
        """
        # Default Record.isvalid() returns True
        return True

##################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Parse params to input_dict if needed
        if isinstance(params, dict):
            input_dict = params
        else:
            try:
                assert Path(params).is_file()
            except:
                input_dict = parse(params, allsingular=True)
            else:
                with open(params) as f:
                    input_dict = parse(f, allsingular=True)
        
        self.__branch = input_dict.get('branch', 'main')
        
        # Set calculation UUID
        if key is not None:
            self.__key = self.name = key
        else:
            self.__key = self.name = input_dict.get('calc_key', self.key)

        return input_dict

    def master_prepare_inputs(self, branch='main', **kwargs):
        """
        Utility method that build input parameters for prepare according to the
        workflows used by the NIST Interatomic Potentials Repository.  In other
        words, transforms inputs from master_prepare into inputs for prepare.

        Parameters
        ----------
        branch : str, optional
            Indicates the workflow branch to prepare calculations for.  Default
            value is 'main'.
        **kwargs : any
            Any parameter modifications to make to the standard workflow
            prepare scripts.

        Returns
        -------
        params : dict
            The full set of prepare parameters based on the workflow branch
        """
        raise NotImplementedError('Not implemented for the calculation style')

    @property
    def singularkeys(self):
        """list: Calculation keys that can have single values during prepare."""
        return  ['branch']
    
    @property
    def multikeys(self):
        """list: Calculation key sets that can have multiple values during prepare."""
        return []
    
    @property
    def allkeys(self):
        """
        list: All keys used by the calculation.
        """
        # Build list of all keys
        allkeys = deepcopy(self.singularkeys)
        for keyset in self.multikeys:
            allkeys.extend(keyset)
        
        return allkeys

    @property
    def template(self):
        """str: The template to use for generating calc.in files."""
        # Start template
        template = f'# Input script for calc_{self.style}.py\n'
        
        # Build common content
        header = 'Calculation metadata'
        keys = ['branch']
        template += '\n' +self._template_builder(header, keys) + '\n'

        return template

    def _template_builder(self, header, keys):
        """Builds a section of the template for a set of parameter keys"""
        if len(keys) > 0:
            template = f'# {header}\n'
            for key in keys:
                spacelen = 32 - len(key)
                if spacelen < 1:
                    spacelen = 1
                space = ' ' * spacelen
                template += f'{key}{space}<{key}>\n'
        return template

########################### Data model interactions ###########################

    @property
    def xsd_filename(self):
        return (self.parent_module, f'{self.style}.xsd')

    def load_model(self, model, name=None):

        super().load_model(model, name=name)
        calc = self.model[self.modelroot]
        
        # Extract information
        self.__key = calc['key']
        self.__iprPy_version = calc['calculation']['iprPy-version']
        self.__atomman_version = calc['calculation']['atomman-version']
        self.__script = calc['calculation']['script']
        self.__branch = calc['calculation'].get('branch', 'main')
        self.__status = calc.get('status', 'finished')
        self.__error = calc.get('error', None)

        try:
            self.name
        except:
            self.name = self.key

    def build_model(self):
        
        # Create the root of the DataModelDict
        model = DM()
        model[self.modelroot] = calc = DM()
        
        # Assign uuid
        calc['key'] = self.key
        
        # Save calculation parameters
        calc['calculation'] = DM()
        calc['calculation']['iprPy-version'] = self.iprPy_version
        calc['calculation']['atomman-version'] = self.atomman_version        
        calc['calculation']['script'] = self.script
        calc['calculation']['branch'] = self.branch

        if self.status != 'finished':
            calc['status'] = self.status

            if self.status == 'error':
                calc['error'] = self.error

        return model

########################## Metadata interactions ##############################

    def metadata(self):
        """
        Converts the structured content to a simpler dictionary.

        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        meta = {}
        meta['name'] = self.name
        
        # Set universal calculation record params
        meta['key'] = self.key
        meta['iprPy_version'] = self.iprPy_version
        meta['atomman_version'] = self.atomman_version
        meta['script'] = self.script
        meta['branch'] = self.branch

        # Fetch calculation status
        meta['status'] = self.status
        if self.status == 'error':
            meta['error'] = self.error
        
        return meta

    @property
    def compare_terms(self):
        """list: The terms to compare metadata values absolutely."""
        return []
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, iprPy_version=None,
                     atomman_version=None, script=None, branch=None,
                     status=None):

        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.str_match.pandas(dataframe, 'key', key)
            &query.str_match.pandas(dataframe, 'iprPy_version', iprPy_version)
            &query.str_match.pandas(dataframe, 'atomman_version', atomman_version)
            &query.str_match.pandas(dataframe, 'script', script)
            &query.str_match.pandas(dataframe, 'branch', branch)
            &query.str_match.pandas(dataframe, 'status', status)
        )
        return matches

    @staticmethod
    def mongoquery(modelroot, name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None):
        mquery = {}
        query.str_match.mongo(mquery, f'name', name)
        
        root = f'content.{modelroot}'
        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.calculation.iprPy-version', iprPy_version)
        query.str_match.mongo(mquery, f'{root}.calculation.atomman-version', atomman_version)
        query.str_match.mongo(mquery, f'{root}.calculation.script', script)
        query.str_match.mongo(mquery, f'{root}.calculation.branch', branch)
        if status is not None:            
            assert isinstance(status, str), 'lists of status not yet supported'
            if status == 'finished':
                mquery[f'{root}.status'] = {'$exists': False}
            else:
                mquery[f'{root}.status'] = status
        
        return mquery

    @staticmethod
    def cdcsquery(modelroot, key=None, iprPy_version=None,
                  atomman_version=None, script=None, branch=None,
                  status=None):
        mquery = {}
        root = modelroot
        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.calculation.iprPy-version', iprPy_version)
        query.str_match.mongo(mquery, f'{root}.calculation.atomman-version', atomman_version)
        query.str_match.mongo(mquery, f'{root}.calculation.script', script)
        query.str_match.mongo(mquery, f'{root}.calculation.branch', branch)
        if status is not None:            
            assert isinstance(status, str), 'lists of status not yet supported'
            if status == 'finished':
                mquery[f'{root}.status'] = {'$exists': False}
            else:
                mquery[f'{root}.status'] = status

        return mquery


########################### Calculation interactions ##########################

    def clean(self):
        self.__status = 'not calculated'
        self.__error = None

    def calc_inputs(self):
        """Builds calculation inputs from the class's attributes"""
        raise AttributeError('calc not defined for Calculation style')

    def calc(self, *args, **kwargs):
        """Calls the calculation's primary function(s)"""
        raise AttributeError('calc not defined for Calculation style')

    def run(self, newkey=False, results_json=False, verbose=False):
        """
        Runs the calculation using the current class attribute values. Status
        after running will be either "finished" or "error".

        Parameters
        ----------
        newkey : bool, optional
            If True, then the calculation's key and name will be replaced with
            a new UUID4.  This allows for iterations on previous runs to be
            uniquely labeled.  Default value is False.
        results_json : bool, optional
            If True, then a "results.json" file will be generated following
            the run.
        verbose : bool, optional
            If True, a message relating to the calculation's status will be
            printed upon completion.  Default value is False.
        """
        # Clean record back to not calculated state
        self.clean()        
        
        # Update iprPy and atomman version info
        self.__iprPy_version = iprPy_version
        self.__atomman_version = atomman_version

        # Change the calculation's key if requested
        if newkey:
            self.__key = self.name = str(uuid.uuid4())

        # Build calculation inputs
        input_dict = self.calc_inputs()
        
        try:
            # Pass inputs to calc function
            results_dict = self.calc(**input_dict)
        
        except Exception as e:
            # Catch any error messages
            self.__status = 'error'
            self.__error = str(e)
            results_dict = None
        
        else:
            self.__status = 'finished'
        
        if results_json is True:
            with open('results.json', 'w', encoding='UTF-8') as f:
                self.build_model().json(fp=f, indent=4, ensure_ascii=False)

        if verbose:
            if self.status == 'finished':
                print('Calculation finished successfully')
            else:
                print('Error:', self.error)

        return results_dict