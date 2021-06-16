# Standard Python libraries
import uuid

# https://github.com/usnistgov/atomman
import atomman as am

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Record

class ReferenceCrystal(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'reference-crystal'
    
    def buildcontent(self, input_dict):
        """
        Builds a data model of the specified record style based on input (and
        results) parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary of all input parameter terms.
        
        Returns
        -------
        DataModelDict
            Data model consistent with the record's schema format.
        
        Raises
        ------
        AttributeError
            If buildcontent is not defined for record style.
        """
        # Create the root of the DataModelDict
        output = DM()
        output[self.contentroot] = crystal = DM()
        
        # Assign key and id
        crystal['key'] = input_dict.get('key', str(uuid.uuid4()))
        crystal['id'] = input_dict['id']
        
        # Specify source info
        crystal['source'] = DM()
        crystal['source']['name'] = input_dict['sourcename']
        crystal['source']['link'] = input_dict['sourcelink']
        
        system_model = input_dict['ucell'].dump('system_model',
                                                box_unit=input_dict.get('length_unit', None))
        crystal['atomic-system'] = system_model['atomic-system']
        
        self.content = output

    def todict(self, full=True, flat=False):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
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
            
        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        # Fetch universal record params
        params = super().todict(full=full, flat=flat)
        
        crystal = self.content[self.contentroot]
        params['sourcename'] = crystal['source']['name']
        params['sourcelink'] = crystal['source']['link']
        
        ucell = am.load('system_model', self.content, key='atomic-system')
        params['composition'] = ucell.composition
        params['natypes'] = ucell.natypes
        
        if flat is True:
            params['symbols'] = list(ucell.symbols)
            params['a'] = ucell.box.a
            params['b'] = ucell.box.b
            params['c'] = ucell.box.c
            params['alpha'] = ucell.box.alpha
            params['beta'] = ucell.box.beta
            params['gamma'] = ucell.box.gamma
            params['natoms'] = ucell.natoms
        else:
            params['ucell'] = ucell
        
        return params