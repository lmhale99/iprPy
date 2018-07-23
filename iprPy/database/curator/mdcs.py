# Standard Python libraries
from __future__ import (print_function, unicode_literals, division,
                        absolute_import)
import os
import sys
import json
import getpass
from copy import deepcopy
from collections import OrderedDict
import warnings

# https://pandas.pydata.org
import pandas as pd

# http://docs.python-requests.org
import requests

from DataModelDict import DataModelDict as DM

def screen_input(prompt=''):
    """
    Replacement input function that is compatible with Python versions 2 and
    3, as well as the mingw terminal.
    
    Parameters
    ----------
    prompt : str, optional
        The screen prompt to use for asking for the input.
        
    Returns
    -------
    str
        The user input.
    """
    ispython2 = sys.version_info[0] == 2
    ispython3 = sys.version_info[0] == 3
    
    # Flush prompt to work interactively with mingw
    print(prompt, end=' ')
    sys.stdout.flush()
    
    # Call version dependent function
    if ispython3: 
        return input()
    elif ispython2:
        return raw_input()
    else:
        raise ValueError('Unsupported Python version')

def database_list():
    """
    Lists names of all stored access informations.
    
    Returns 
    -------
    list
        The names assigned to all access information.
    """
    accessfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mdcs')
    if os.path.isfile(accessfile):
        with open(accessfile) as fp:
            access_info = json.load(fp)
    else:
        return []
    return list(access_info.keys())

def database_info(name):
    """
    Shows info for stored access information.  If pswd is stored, will replace
    value with True.
    
    Returns
    -------
    dict
        Contains the keys 'host', 'user', 'cert', and 'pswd'.
    """
    accessfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mdcs')
    if os.path.isfile(accessfile):
        with open(accessfile) as fp:
            access_info = json.load(fp)
    else:
        raise ValueError('No access info stored as ' + name)
    
    if name in access_info:
        access_dict = access_info[name]
        if access_dict['pswd'] is not None:
            access_dict['pswd'] = True
        return access_dict
    else:
        raise ValueError('No access info stored as ' + name)

def database_load(name):
    """
    Retrieve stored access information.
    
    Parameters
    ----------
    name : str
        The name assigned to stored access information.
    
    Returns
    -------
    MDCS
        A database interface object with the stored login information.
    """
    accessfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mdcs')
    if os.path.isfile(accessfile):
        with open(accessfile) as fp:
            access_info = json.load(fp)
    else:
        raise ValueError('No access info stored as ' + name)
    
    if name in access_info:
        host = access_info[name]['host']
        user = access_info[name]['user']
        pswd = access_info[name]['pswd']
        cert = access_info[name]['cert']
        return MDCS(host, user, pswd=pswd, cert=cert)
    else:
        raise ValueError('No access info stored as ' + name)

def database_forget(name):
    """
    Deletes stored access information.
    
    Parameters
    ----------
    name : str
        The name assigned to stored access information.
    """
    accessfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mdcs')
    if os.path.isfile(accessfile):
        with open(accessfile) as fp:
            access_info = json.load(fp)
    else:
        raise ValueError('No access info stored as ' + name)
    
    if name in access_info:
        del(access_info[name])
        with open(accessfile, 'w') as fp:
            json.dump(access_info, fp)
    else:
        raise ValueError('No access info stored as ' + name)

class MDCS(object):
    """
    Class for accessing instances the Materials Database Curation System (MDCS).
    """
    
    def __init__(self, host, user=None, pswd=None, cert=None):
        """
        Class initializer. Tests and stores MDCS access information and builds
        local DataFrames of types and templates.
        
        Parameters
        ----------
        host : str
            URL for the MDCS server.
        user : str
            User name of desired account on the MDCS server.
        pswd : str, optional
            Password of desired account on the MDCS server.  A prompt will
            ask for the password if not given.
        cert : str, optional
            Path to an authentication certificate, if needed, to access the MDCS
            server.
        """
        # Set access information
        self.login(host, user=user, pswd=pswd, cert=cert)
    
    def __str__(self):
        """
        String representation.
        """
        return 'MDCS @ ' + self.host + ' (' + self.user + ')'
        
    @property
    def host(self):
        """str: The host url for the MDCS server."""
        return self.__host
    
    @property
    def user(self):
        """str: The username to use for the MDCS server."""
        return self.__user
    
    @property
    def cert(self):
        """str or None: The path to the certification file."""
        return self.__cert
    
    def login(self, host, user=None, pswd=None, cert=None):
        """
        Defines access information for an MDCS instance.
        
        Parameters
        ----------
        host : str
            URL for the MDCS server.
        user : str, optional
            User name of desired account on the MDCS server.  A prompt will
            ask for the user name if not given.
        pswd : str, optional
            Password of desired account on the MDCS server.  A prompt will
            ask for the password if not given.
        cert : str, optional
            Path to an authentication certificate, if needed, to access the MDCS
            server.
        
        Raises
        ------
        ValueError
            If access information not correct.
        """
        # Handle host
        host = host.strip("/")
        
        # Handle cert
        if cert is not None:
            if os.path.isfile(cert):
                cert = os.path.abspath(cert)
            else:
                raise ValueError('Certification file not found!')
        
        # Handle username
        if user is None:
            user = screen_input(prompt='username:')
        
        # Handle password
        if pswd is None:
            pswd = getpass.getpass(prompt='password:')
        
        # Test values
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = requests.get(host + "/rest/explore/select",
                                 auth=(user, pswd), verify=cert)
        except requests.exceptions.SSLError:
            raise ValueError('Invalid cert')
        except requests.exceptions.ConnectionError:
            raise ValueError('Invalid host')
        else:
            if r.status_code == 401:
                raise ValueError('Invalid user/pswd')
            elif r.status_code != 400:
                r.raise_for_status()
        
        # Set values
        self.__host = host
        self.__user = user
        self.__pswd = pswd
        self.__cert = cert
    
    def database_remember(self, name, include_pswd=False):
        """
        Save access information using an assigned name.
        
        Parameters
        ----------
        name : str
            Name to assign to stored access information
        include_pswd : bool
            Indicates if password is to be saved.  Note: the information is
            stored in a text file, so it can be viewed by anyone with access
            to your computer.
        """
        accessfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mdcs')
        access_dict = {}
        access_dict['host'] = self.host
        access_dict['user'] = self.user
        access_dict['cert'] = self.cert
        if include_pswd:
            access_dict['pswd'] = self.__pswd
        else:
            access_dict['pswd'] = None
        
        if os.path.isfile(accessfile):
            with open(accessfile) as fp:
                access_info = json.load(fp)
        else:
            access_info = {}
        
        if name in access_info:
            raise ValueError('Access info ' + name + ' already exists')
        
        access_info[name] = access_dict
        with open(accessfile, 'w') as fp:
            json.dump(access_info, fp)
    
    def select_all(self, format=None):
        """
        Get all data from the MDCS server.
        
        Parameters
        ----------
        format : str, optional
            Format to return record content as, can be either 'xml', or 'json'.
        
        Returns
        -------
        pandas.DataFrame
            All stored records.
        """
        # Build requests parameters
        params = {}
        if format:
            params['dataformat'] = format
        
        # Get and return response
        url = self.host + "/rest/explore/select/all"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = requests.get(url, params=params, auth=(self.user, self.__pswd), verify=self.cert)
        r.raise_for_status()
        return pd.DataFrame(r.json(object_pairs_hook=OrderedDict))
    
    def select(self, *args, **kwargs):
        """
        Gets a list of all records matching the given parameters.  One
        positional parameter is allowed, which will be tested against title,
        and id, if they are not given separately.
        
        Parameters
        ----------
        title : str, optional
            The title assigned to the record.
        id : str, optional
            The records's unique id.
        template : pandas.Series, str or dict, optional
            The template associated with the record.  If str, will be searched
            against the template's id, title, and filename.  If dict, allows
            multiple template parameters to be specified in matching correct
            template.
        format : str, optional
            Format to return record content as, can be either 'xml', or 'json'.
        
        Returns
        -------
        pandas.DataFrame
            All matching records.
        """
        # Check parameters
        if len(args) > 1:
            raise TypeError('Only one positional argument allowed')
        for key in kwargs:
            if key not in ['id', 'title', 'template', 'format']:
                raise KeyError('Unknown keyword argument ' + key)
        for key in ['id', 'title', 'template', 'format']:
            kwargs[key] = kwargs.get(key, None)
        
        # Handle template
        if kwargs['template'] is not None:
            template = kwargs['template']
            if isinstance(template, pd.Series):
                pass
            elif isinstance(template, dict):
                template = self.template_select_one(**template)
            else:
                template = self.template_select_one(template)
            kwargs['template'] = template
        
        if len(args) == 0:
            url = self.host + "/rest/explore/select"
            params = {}
            if kwargs['format'] is not None:
                params['dataformat'] = kwargs['format']
            if kwargs['id'] is not None:
                params['id'] = kwargs['id']
            if kwargs['template'] is not None:
                params['schema'] = kwargs['template'].id
            if kwargs['title'] is not None:
                params['title'] = kwargs['title']
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = requests.get(url, params=params, auth=(self.user, self.__pswd), verify=self.cert)
            try:
                r.raise_for_status()
            except:
                return pd.DataFrame()
            else:
                return pd.DataFrame(r.json(object_pairs_hook=OrderedDict))
        else:
            if kwargs['id'] is not None and kwargs['title'] is not None:
                raise KeyError('Positional argument not allowed if if id, and title are both given')
            records = pd.DataFrame()
            for key in ['id', 'title']:
                if kwargs[key] is None:
                    newkwargs = deepcopy(kwargs)
                    newkwargs[key] = args[0]
                    try:
                        newrecords = self.select(**newkwargs)
                    except:
                        pass
                    else:
                        records = pd.concat([records, newrecords], ignore_index=True)
            if len(records) > 0:
                records = records.drop_duplicates()
            return records
    
    def select_one(self, *args, **kwargs):
        """
        Get a single record matching the given parameters.  One
        positional parameter is allowed, which will be tested against title,
        id, and filename if they are not given separately.  Will issue an error
        if no or multiple matching records are found.
        
        Parameters
        ----------
        title : str, optional
            The title assigned to the record.
        id : str, optional
            The records's unique id.
        template : pandas.Series, str or dict, optional
            The template associated with the record.  If str, will be searched
            against the template's id, title, and filename.  If dict, allows
            multiple template parameters to be specified in matching correct
            template.
        format : str, optional
            Format to return record content as, can be either 'xml', or 'json'.
        
        Returns
        -------
        pandas.Series
            The matching record.
        """
        
        # Pass args and kwargs to select
        records = self.select(*args, **kwargs)
        
        if len(records) == 1:
            return records.iloc[0]
        elif len(records) == 0:
            raise ValueError('No matching records found')
        else:
            raise ValueError('Multiple matching records found')
    
    def query(self, query, format=None, repositories=None):
        """
        Select records based on MongoDB-style query string.
        
        Parameters
        ----------
        
        """
        # Build requests data
        data = {}
        data['query'] = query
        if format:
            data['dataformat'] = format
        if format:
            data['repositories'] = repositories
        
        # Post and return response
        url = self.host + "/rest/explore/query-by-example"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = requests.post(url, data=data, auth=(self.user, self.__pswd), verify=self.cert)
        r.raise_for_status()
        return pd.DataFrame(r.json(object_pairs_hook=OrderedDict))
    
    def curate(self, content, title, template):
        """
        Curates (uploads) a record to the MDCS instance.
        
        Parameters
        ----------
        content : str
            The xml content or path to a file containing the content of the
            record to curate.
        title : str
            The name to assign to the record as it will be stored in the database.
        template : pandas.Series, str or dict, optional
            The template associated with the record.  If str, will be searched
            against the template's id, title, and filename.  If dict, allows
            multiple template parameters to be specified in matching correct
            template.
        """
        
        # Handle template
        if isinstance(template, pd.Series):
            pass
        elif isinstance(template, dict):
            template = self.template_select_one(**template)
        else:
            template = self.template_select_one(template)
        
        # Check if matching record already curated
        records = self.select(title=title, template=template)
        if len(records) > 0:
            raise ValueError('Record with matching title and template already curated')
        
        # Handle content
        content = DM(content).xml()
        
        # Build requests parameters
        data = {}
        data['content'] = [content]
        data['schema'] = [template.id]
        data['title'] = [title]
        
        # Post and return response
        url = self.host + "/rest/curate"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = requests.post(url, data=data, auth=(self.user, self.__pswd), verify=self.cert)
        r.raise_for_status()
    
    def delete(self, *args, **kwargs):
        """
        Deletes a record from the MDCS instance.
        
        Parameters
        ----------
        record : pandas.Series, optional
            The record to delete.  Cannot be given with the other parameters.
        title : str, optional
            The title assigned to the record.
        id : str, optional
            The record's unique id.
        template : pandas.Series, str or dict, optional
            The template associated with the record.  If str, will be searched
            against the template's id, title, and filename.  If dict, allows
            multiple template parameters to be specified in matching correct
            template.
        """
        
        # Handle record
        if len(args) == 1 and isinstance(args[0], pd.Series):
            record = args[0]
        elif 'record' in kwargs and kwargs['record'] is not None:
            if len(args) > 0 or ken(kwargs) > 1:
                raise ValueError('record cannot be given with any other parameters')
            record = record
        else:
           record = self.select_one(*args, **kwargs)
        
        # Build requests parameters
        params ={}
        params['id'] = record._id
        
        # Delete and return response
        url = self.host + "/rest/explore/delete"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = requests.delete(url, params=params, auth=(self.user, self.__pswd), verify=self.cert)
        r.raise_for_status()
        return r.text
    
    def template_select(self, *args, **kwargs):
        """
        Gets a list of all templates matching the given parameters.  One
        positional parameter is allowed, which will be tested against title,
        id, and filename if they are not given separately.
        
        Parameters
        ----------
        title : str
            The title assigned to the template.
        id : str
            The template's unique id.
        filename : str
            The filename for the template.
        version : int
            Version number for the template.
        templateVersion : str
            Unique id for template and version.
        hash : str
            Database hash.
        
        Returns
        -------
        pandas.DataFrame
            All matching templates.
        """
        
        # Check parameters
        if len(args) > 1:
            raise TypeError('Only one positional argument allowed')
        for key in kwargs:
            if key not in ['id', 'filename', 'title', 'version',
                           'templateVersion', 'hash']:
                raise KeyError('Unknown keyword argument ' + key)
        
        if len(args) == 0:
            url = self.host + "/rest/templates/select"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r = requests.get(url, params=kwargs, auth=(self.user, self.__pswd), verify=self.cert)
            try:
                r.raise_for_status()
            except:
                df = self.template_select_all()
                for key in kwargs:
                    df = df[df[key] == kwargs[key]]
                return df
            else:
                return pd.DataFrame(r.json(object_pairs_hook=OrderedDict))
                
        else:
            if 'id' in kwargs and 'filename' in kwargs and 'title' in kwargs:
                raise KeyError('Positional argument not allowed if id, filename and title are all given')
            templates = pd.DataFrame()
            for key in ['id', 'filename', 'title']:
                if key not in kwargs:
                    newkwargs = deepcopy(kwargs)
                    newkwargs[key] = args[0]
                    try:
                        newtemplates = self.template_select(**newkwargs)
                    except:
                        pass
                    else:
                        templates = pd.concat([templates, newtemplates], ignore_index=True)
            if len(templates) > 0:
                templates = templates.drop_duplicates(subset=['title', 'filename',
                                                              'content', 'version',
                                                              'hash','id',
                                                              'templateVersion'])
            return templates
    
    def template_select_one(self, *args, **kwargs):
        """
        Get a single templates matching the given parameters.  One
        positional parameter is allowed, which will be tested against title,
        id, and filename if they are not given separately.  Will issue an error
        if no or multiple matching templates are found.
        
        Parameters
        ----------
        title : str
            The title assigned to the template.
        id : str
            The template's unique id.
        filename : str
            The filename for the template.
        version : int
            Version number for the template.
        templateVersion : str
            Unique id for template and version.
        hash : str
            Database hash.
        
        Returns
        -------
        pandas.Series
            The matching template.
        """
        # Pass args and kwargs to template_select
        templates = self.template_select(*args, **kwargs)
        
        if len(templates) == 1:
            return templates.iloc[0]
        elif len(templates) == 0:
            raise ValueError('No matching templates found')
        else:
            raise ValueError('Multiple matching templates found')
    
    def template_select_all(self):
        """
        Gets a list of all templates in the MDCS instance.
        
        Returns
        -------
        pandas.DataFrame
            All templates.
        """
        # Specify URL
        url = self.host + "/rest/templates/select/all"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = requests.get(url, auth=(self.user, self.__pswd), verify=self.cert)
        try:
            r.raise_for_status()
        except:
            return pd.DataFrame()
        else:
            return pd.DataFrame(r.json(object_pairs_hook=OrderedDict))
    
    def template_add(self, filename, title, version=None, dependencies=None):
        """
        Uploads a new template to the MDCS instance.
        
        Parameters
        ----------
        filename
        title
        version
        dependencies
        """
        assert False, 'Method not added yet'
    
    def blob_upload(self, filename):
        """
        Uploads a blob to the MDCS instance.
        
        Parameters
        ----------
        filename : str
            Path to file to upload
        
        Returns
        -------
        str
            The URL where the blob can be downloaded.
        """
        
        # Build requests parameters
        files = {'blob':open(filename, 'rb')}
        
        # Post and check response
        url = self.host + "/rest/blob"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = requests.post(url, files=files, auth=(self.user, self.__pswd), verify=self.cert)
        r.raise_for_status()
        result = r.json(object_pairs_hook=OrderedDict)
        
        # Return handle (URL)
        return result['handle']
    
    def blob_download(self, url, filename=None):
        """
        Download a blob from the MDCS instance.
        
        Parameters
        ----------
        url : : str
            The URL where the blob can be downloaded.
        filename : str, optional
            Path to file where the content can be saved.  If value is None
            (default) then the blob is returned as bytes content.
        
        Returns
        -------
        bytes
            The downloaded content (only returned if filename is None).
        """
        
        # Get and check response
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = requests.get(url, auth=(self.user, self.__pswd), verify=self.cert)
        r.raise_for_status()
        
        if filename is None:
            # Return content
            return r.content
        else:
            with open(filename, 'wb') as f:
                f.write(r.content)