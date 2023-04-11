# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from copy import deepcopy
from importlib import resources
from typing import Optional, Union

from yabadaba import load_query

from DataModelDict import DataModelDict as DM

import atomman as am
from atomman import __version__ as current_atomman_version

from .. import __version__ as current_iprPy_version
from ..input import parse
import uuid

from ..record import Record

class Calculation(Record):
    """Base class for managing calculations"""

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, Path, IOBase, DM, None]=None,
                 name: Optional[str]=None,
                 params: Union[str, Path, IOBase, dict] = None,
                 database = None,
                 subsets: Optional[tuple] = None,
                 **kwargs: any):
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
        database : atomman.library.Database or Database, optional
            A Database object to associate with the calculation record.  Some
            calculation styles may have options where additional data can be
            accessed from other records in a database.  Specifying a database
            ensures that those calculations are retrieving that reference
            information from the correct location.  If not given, then will
            use the settings for the local potentials/atomman database.
        subsets : tuple, optional
            The calculation subsets associated with the calculation style.
            This should be set by the child class __init__ function.
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

        # Set default values (just in case)
        self.__iprPy_version = current_iprPy_version
        self.__atomman_version = current_atomman_version
        self.__key = str(uuid.uuid4())
        self.__branch = 'main'
        self.__status = 'not calculated'
        self.__error = None

        # Link to database
        self.database = database

        # Initialize subsets list
        if subsets is not None:
            self.__subsets = tuple(subsets)
        else:
            self.__subsets = ()

        # Call Record's init
        super().__init__(model=model, name=name, **kwargs)

        # Load parameters if given
        if params is not None:
            self.load_parameters(params, key=kwargs.get('key', None))

    @property
    def maindoc(self) -> str:
        """str: the overview documentation for the calculation"""
        try:
            return resources.read_text(self.parent_module, 'README.md')
        except:
            return ""

    @property
    def theorydoc(self) -> str:
        """str: the methods and theory documentation for the calculation"""
        try:
            return resources.read_text(self.parent_module, 'theory.md')
        except:
            return ""

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""        
        return []

    @property
    def files(self) -> dict:
        """dict: the names and contents of all required files."""
        files = {}
        for filename in self.filenames:
            files[filename] = resources.read_text(self.parent_module, filename)
        
        return files

############################### Class attributes ##############################

    @property
    def subsets(self) -> tuple:
        """tuple: The calculation's subsets"""
        return self.__subsets

    @property
    def style(self) -> str:
        """str: The record style"""
        return f'calculation_{self.calc_style}'

    @property
    def calc_style(self) -> str:
        """str : The calculation style"""
        return self.__calc_style

    @property
    def key(self) -> str:
        """str : The UUID4 key used to identify the calculation run"""
        return self.__key

    @property
    def iprPy_version(self) -> str:
        """str : The version of iprPy used"""
        return self.__iprPy_version

    @property
    def atomman_version(self) -> str:
        """str : The version of atomman used"""
        return self.__atomman_version

    @property
    def script(self) -> str:
        """str : The name of the calculation script used"""
        return self.__script

    @property
    def branch(self) -> str:
        """str : The calculation branch name"""
        return self.__branch

    @property
    def status(self) -> str:
        """str : The current status of the calculation"""
        return self.__status

    @property
    def error(self) -> Optional[str]:
        """str or None : Any error message generated by the calculation"""
        return self.__error

    @property
    def parent_module(self) -> str:
        """str : Name of the module where the calculation's code is located"""
        return self.__parent_module

    @property
    def database(self):
        """iprPy.Database : The Database associated with the calculation record"""
        return self.__database

    @database.setter
    def database(self, value):

        # Set None or atomman.library.Database values
        if value is None or isinstance(value, am.library.Database):
            self.__database = value

        # Otherwise assume that it is a yabadaba/iprPy database
        else:
            self.__database = am.library.Database(local_database=value,
                                                  remote=False)

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs: any):
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameters
        ----------
        name : str, optional
            The name to assign to the calculation.  By default, this is set as
            the calculation's key.
        iprPy_version : str, optional
            Identifies the version of iprPy used.  If not given, will be set to
            the currently loaded iprPy version.
        atomman_version : str, optional
            Identifies the version of atomman used.  If not given, will be set
            to the currently loaded atomman version.
        key : str, optional
            A UUID4 key to uniquely identify the calculation run.
        branch : str, optional
            A branch name to differentiate sets of calculation runs based on
            input parameters.  Default value is 'main'.
        status : str, optional
            The calculation's status: 'not calculated', 'finished' or 'error'.
            Default value is 'not calculated'.
        error : str or None, optional
            An error message for the calculation, if one was raised.
        **kwargs : any, optional
            All extra keywords are passed on to the set_values() methods of
            the calculation's subsets.
        """
        # Set universal content
        self.__iprPy_version = kwargs.get('iprPy_version', current_iprPy_version)
        self.__atomman_version = kwargs.get('atomman_version', current_atomman_version)
        self.__key = kwargs.get('key', str(uuid.uuid4()))
        self.__script = f'calc_{self.calc_style}' # Obsolete....
        self.__branch = kwargs.get('branch', 'main')
        self.__status = kwargs.get('status', 'not calculated')
        self.__error = kwargs.get('error', None)

        # Set name
        if name is None:
            self.name = self.key
        else:
            self.name = name

        # Set subset content
        for subset in self.subsets:
            subset.set_values(**kwargs)

##################### Parameter file interactions ########################### 

    def load_parameters(self,
                        params: Union[dict, str, IOBase],
                        key: Optional[str] = None):
        """
        Reads in and sets calculation parameters.

        Parameters
        ----------
        params : dict, str or file-like object
            The parameters or parameter file to read in.
        key : str, optional
            A new key value to assign to the object.  If not given, will use
            calc_key field in params if it exists, or leave the key value
            unchanged.
        """
        # Parse params to input_dict if needed
        if isinstance(params, dict):
            input_dict = params
        else:
            input_dict = parse(params, allsingular=True)

        self.__branch = input_dict.get('branch', 'main')

        # Set calculation UUID
        if key is not None:
            self.__key = self.name = key
        else:
            self.__key = self.name = input_dict.get('calc_key', self.key)

        return input_dict

    def master_prepare_inputs(self,
                              branch: str = 'main',
                              **kwargs: any) -> dict:
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
    def commontemplatekeys(self) -> dict:
        """dict : The input keys and their descriptions shared by all calculations."""
        return {
            'branch': ' '.join([
                "A metadata group name that the calculation can be parsed by.",
                "Primarily meant for differentiating runs with different",
                "settings parameters."
            ])
        }

    @property
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""
        return {}

    @property
    def template(self) -> str:
        """str: The template to use for generating calc.in files."""
        # Start template
        lines = [f'# Input script for iprPy calculation {self.calc_style}', '']

        # Build common content
        lines += ['# Calculation Metadata']
        for key in self.commontemplatekeys.keys():
            spacelen = 32 - len(key)
            if spacelen < 1:
                spacelen = 1
            space = ' ' * spacelen
            lines.append(f'{key}{space}<{key}>')
        lines.append('')

        # Add subset content
        for subset in self.subsets:
            lines.append(subset.template)

        # Build calculation-specific run parameters
        if len(self.templatekeys) > 0:
            lines += ['# Run Parameters']
            for key in self.templatekeys.keys():
                spacelen = 32 - len(key)
                if spacelen < 1:
                    spacelen = 1
                space = ' ' * spacelen
                lines.append(f'{key}{space}<{key}>')

        # Join and return lines
        return '\n'.join(lines)

    @property
    def templatedoc(self) -> str:
        """str: The documentation for the template lines for this calculation."""

        lines = [f'# {self.calc_style} Input Terms', '']

        # Specify common content
        lines += ['## Calculation Metadata',
                  '',
                  "Specifies metadata descriptors common to all calculation styles.",
                  '']

        # Build lines for each common template key
        for key, doc in self.commontemplatekeys.items():
            lines.append(f'- __{key}__: {doc}')
        lines.append('')

        # Add subset content
        for subset in self.subsets:
            lines.append(subset.templatedoc)

        # Build lines for each calculation-specific template key
        if len(self.templatekeys) > 0:
            lines.append('## Run Parameters\n')
            for key, doc in self.templatekeys.items():
                lines.append(f'- __{key}__: {doc}')

        # Join and return lines
        return '\n'.join(lines)

    def _template_builder(self,
                          header: str,
                          keys: list) -> str:
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

    @property
    def singularkeys(self) -> list:
        """list: Calculation keys that can have single values during prepare."""
        return  ['branch']

    @property
    def multikeys(self) -> list:
        """list: Calculation key sets that can have multiple values during prepare."""
        return []

    @property
    def allkeys(self) -> list:
        """
        list: All keys used by the calculation.
        """
        # Build list of all keys
        allkeys = deepcopy(self.singularkeys)
        for keyset in self.multikeys:
            allkeys.extend(keyset)

        return allkeys

########################### Data model interactions ###########################

    @property
    def xsd_filename(self):
        """tuple: The module path and file name of the record's xsd schema"""
        return (self.parent_module, f'{self.style}.xsd')

    @property
    def xsl_filename(self):
        """tuple: The module path and file name of the record's xsl transform"""
        return (self.parent_module, f'{self.style}.xsl')

    def build_model(self) -> DM:
        """
        Generates and returns model content based on the values set to object.
        """
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

    def load_model(self,
                   model: Union[str, DM],
                   name: Optional[str] = None):
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
        super().load_model(model, name=name)
        calc = self.model[self.modelroot]

        # Load universal content
        self.__key = calc['key']
        self.__iprPy_version = calc['calculation']['iprPy-version']
        self.__atomman_version = calc['calculation']['atomman-version']
        self.__script = calc['calculation']['script']
        self.__branch = calc['calculation'].get('branch', 'main')
        self.__status = calc.get('status', 'finished')
        self.__error = calc.get('error', None)

        # Set name
        try:
            self.name
        except:
            self.name = self.key

        # Load subset content
        for subset in self.subsets:
            subset.load_model(calc)

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        queries = {
            'key': load_query(
                style='str_match',
                name='key',
                path=f'{self.modelroot}.key',
                description="search by calculation's UUID key"),
            'iprPy_version': load_query(
                style='str_match',
                name='iprPy_version',
                path=f'{self.modelroot}.calculation.iprPy-version',
                description="search by iprPy version used"),
            'atomman_version': load_query(
                style='str_match',
                name='atomman_version',
                path=f'{self.modelroot}.calculation.atomman-version',
                description="search by atomman version used"),
            'script': load_query(
                style='str_match',
                name='script',
                path=f'{self.modelroot}.calculation.script',
                description="search by script name used"),
            'branch': load_query(
                style='str_match',
                name='branch',
                path=f'{self.modelroot}.calculation.branch',
                description="search by calculation branch name"),
            'status': load_query(
                style='str_match',
                name='status',
                path=None,
                description="search by calculation status"),
        }

        # Add subset queries
        for subset in self.subsets:
            queries.update(subset.queries)

        return queries

    def mongoquery(self,
                   name: Union[str, list, None] = None,
                   key: Union[str, list, None] = None,
                   iprPy_version: Union[str, list, None] = None,
                   atomman_version: Union[str, list, None] = None,
                   script: Union[str, list, None] = None,
                   branch: Union[str, list, None] = None,
                   status: Union[str, list, None] = None,
                   **kwargs: any) -> dict:
        """
        Builds a Mongo-style query based on kwargs values for the record style.

        Parameters
        ----------
        name : str or list, optional
            The record name(s) to parse by.
        key : str or list, optional
            The unique record UUID4 keys to parse by.
        iprPy_version : str or list, optional
            The version(s) of iprPy to parse by.
        atomman_version : str or list, optional
            The version(s) of atomman to parse by.
        script : str or list, optional
            The name(s) of the calculation script to parse by.
        branch : str or list, optional
            The calculation branch name(s) to parse by.
        status : str or list, optional
            The status(es) of the calculations to parse by.
        **kwargs : any
            Any extra query terms associated with one of the calculation's
            subsets.
        
        Returns
        -------
        dict
            The Mongo-style query.
        """

        # Pass all known and unknown kwargs except status
        mquery = super().mongoquery(name=name, key=key, iprPy_version=iprPy_version,
                                    atomman_version=atomman_version, script=script,
                                    branch=branch, **kwargs)

        # Add status
        if status is not None:
            assert isinstance(status, str), 'lists of status not yet supported'

            root = f'content.{self.modelroot}'
            querylist = mquery['$and']

            if status == 'finished':
                querylist.append( {f'{root}.status': {'$exists': False} } )
            else:
                querylist.append( {f'{root}.status': status} )

        return mquery

    def cdcsquery(self,
                  key: Union[str, list, None] = None,
                  iprPy_version: Union[str, list, None] = None,
                  atomman_version: Union[str, list, None] = None,
                  script: Union[str, list, None] = None,
                  branch: Union[str, list, None] = None,
                  status: Union[str, list, None] = None,
                  **kwargs: any) -> dict:
        """
        Builds a CDCS-style query based on kwargs values for the record style.

        Parameters
        ----------
        key : str or list, optional
            The unique record UUID4 keys to parse by.
        iprPy_version : str or list
            The version(s) of iprPy to parse by.
        atomman_version : str or list, optional
            The version(s) of atomman to parse by.
        script : str or list, optional
            The name(s) of the calculation script to parse by.
        branch : str or list, optional
            The calculation branch name(s) to parse by.
        status : str or list, optional
            The status(es) of the calculations to parse by.
        **kwargs : any
            Any extra query terms associated with one of the calculation's
            subsets.
        
        Returns
        -------
        dict
            The CDCS-style query.
        """
        # Pass all known and unknown kwargs except status
        mquery = super().cdcsquery(key=key, iprPy_version=iprPy_version,
                                   atomman_version=atomman_version, script=script,
                                   branch=branch, **kwargs)

        # Add status
        if status is not None:
            assert isinstance(status, str), 'lists of status not yet supported'

            root = self.modelroot
            querylist = mquery['$and']

            if status == 'finished':
                querylist.append( {f'{root}.status': {'$exists': False} } )
            else:
                querylist.append( {f'{root}.status': status} )

        return mquery

########################## Metadata interactions ##############################

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
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

        # Extract subset content
        for subset in self.subsets:
            subset.metadata(meta)

        return meta

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return []

    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

    def isvalid(self) -> bool:
        """
        Looks at the set attributes to determine if the associated calculation
        would be a valid one to run.
        
        Returns
        -------
        bool
            True if element combinations are valid, False if not.
        """
        # Default Record.isvalid() returns True
        return True

########################### Calculation interactions ##########################

    def clean(self):
        """Resets the calculation state for running again."""
        self.__status = 'not calculated'
        self.__error = None

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""
        raise AttributeError('calc_inputs not defined for Calculation style')

    def calc(self, *args, **kwargs) -> dict:
        """Calls the calculation's primary function(s)"""
        raise AttributeError('calc not defined for Calculation style')

    def process_results(self, results_dict: dict):
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
        raise AttributeError('process_results not defined for Calculation style')

    def run(self,
            params: Union[str, dict, IOBase, None] = None,
            newkey: bool = False,
            results_json: bool = False,
            raise_error: bool = False,
            verbose: bool = False):
        """
        Runs the calculation using the current object attribute values or
        supplied parameters. Status after running will be either "finished"
        or "error".

        Parameters
        ----------
        params : dict, str or file-like object, optional
            The parameters or parameter file to read in.  If not given, will
            run based on the current object attribute values.
        newkey : bool, optional
            If True, then the calculation's key and name will be replaced with
            a new UUID4.  This allows for iterations on previous runs to be
            uniquely labeled.  Default value is False.
        results_json : bool, optional
            If True, then a "results.json" file will be generated following
            the run.
        raise_error : bool, optional
            The default behavior of run is to take any error messages from the
            calculation and set them to class attributes and save to
            results.json. This allows for calculations to successfully fail.
            Setting this to True will instead raise the errors, which can
            provide more details for debugging.
        verbose : bool, optional
            If True, a message relating to the calculation's status will be
            printed upon completion.  Default value is False.
        """
        # Clean record back to not calculated state
        self.clean()

        # Update iprPy and atomman version info
        self.__iprPy_version = current_iprPy_version
        self.__atomman_version = current_atomman_version

        # Change the calculation's key if requested
        if newkey:
            self.__key = self.name = str(uuid.uuid4())

        # Load params if given
        if params is not None:
            self.load_parameters(params)

        # Build calculation inputs
        input_dict = self.calc_inputs()

        try:
            # Pass inputs to calc function
            results_dict = self.calc(**input_dict)

        except Exception as e:
            if raise_error:
                raise e
            # Catch any error messages
            self.__status = 'error'
            self.__error = str(e)
            results_dict = None

        else:
            self.__status = 'finished'
            self.process_results(results_dict)

        if verbose:
            if self.status == 'finished':
                print('Calculation finished successfully')
            else:
                print('Error:', self.error)

        # Save results to json
        if results_json is True:
            with open('results.json', 'w', encoding='UTF-8') as f:
                self.build_model().json(fp=f, indent=4, ensure_ascii=False)
