from typing import Any, Optional, Union

from yabadaba.value import Value


class ResultValue(Value):
    """Base result value class"""

    def __init__(self,
                 name: str,
                 record,
                 defaultvalue: Optional[Any] = None,
                 valuerequired: bool = False,
                 allowedvalues: Optional[tuple] = None,
                 metadatakey: Union[str, bool, None] = None,
                 metadataparent: Optional[str] = None,
                 modelpath: Optional[str] = None,
                 calcname: Union[str, bool, None] = None):
        """
        Initialize a ResultValue object for calculation results.

        Parameters
        ----------
        name : str
            The name of the parameter.  This should correspond to the name of
            the associated class attribute.
        record : Record, optional
            The Record object that the Parameter is used with.
        defaultvalue : any or None, optional
            The default value to use for the property.  The default value of
            None indicates that there is no default value.  Should be None for
            results values. 
        valuerequired: bool, optional
            Indicates if a value must be given for the property.  If True, then
            checks will be performed that a value is assigned to the property.
            Should be False for results values.
        allowedvalues : tuple or None, optional
            A list/tuple of values that the parameter is restricted to have.
            Setting this to None (default) indicates any value is allowed.
        metadatakey: str, bool or None, optional
            The key name to use for the property when constructing the record
            metadata dict.  If set to None (default) then name will be used for
            metadatakey.  If set to False then the parameter will not be
            included in the metadata dict.
        metadataparent: str or None, optional
            If given, then this indicates that the metadatakey is actually an
            element of a dict in metadata with this name.  This allows for limited
            support for metadata having embedded dicts.
        modelpath: str, optional
            The period-delimited path after the record root element for
            where the parameter will be found in the built data model.  If set
            to None (default) then name will be used for modelpath.
        calcname: str, optional
            The key/name of the term in the calculation function's returned
            results_dict that corresponds to this value.  If set to None
            (default) then name will be used for calcname.
        """
        # Call parent super
        super().__init__(name, record,
                         defaultvalue=defaultvalue,
                         valuerequired=valuerequired,
                         allowedvalues=allowedvalues,
                         metadatakey=metadatakey,
                         metadataparent=metadataparent,
                         modelpath=modelpath)
        
        # Set default values of calcname
        if calcname is None:
            calcname = self.name
        elif isinstance(calcname, bool):
            if calcname is True:
                raise TypeError('calcname can be None, False, or str')
        else:
            calcname = str(calcname)
                
        # Save values to class attributes
        self.__calcname =  calcname
    
    @property
    def calcname(self) -> Union[str, bool]:
        """str or bool: The calculation function parameter name to use"""
        return self.__calcname
    
    def process_results_value(self, val):
        return val

    def process_results(self, dict):
        if self.calcname is not False:
            self.value = self.process_results_value(dict[self.calcname])
