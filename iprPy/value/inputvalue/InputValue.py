from typing import Any, Optional, Union

from yabadaba.value import Value


class InputValue(Value):
    """Base input value class"""

    def __init__(self,
                 name: str,
                 record,
                 defaultvalue: Optional[Any] = None,
                 valuerequired: bool = True,
                 allowedvalues: Optional[tuple] = None,
                 metadatakey: Union[str, bool, None] = None,
                 metadataparent: Optional[str] = None,
                 modelpath: Optional[str] = None,
                 calcname: Union[str, bool, None] = None,
                 templatekey: Optional[str] = None,
                 templatedoc: str = '',
                 is_compare_term: bool = False,
                 compare_fterm_tol: Optional[float] = None):
        """
        Initialize an InputValue object for calculation inputs.

        Parameters
        ----------
        name : str
            The name of the parameter.  This should correspond to the name of
            the associated class attribute.
        record : Record, optional
            The Record object that the Parameter is used with.
        defaultvalue : any or None, optional
            The default value to use for the property.  The default value of
            None indicates that there is no default value.
        valuerequired: bool, optional
            Indicates if a value must be given for the property.  If True, then
            checks will be performed that a value is assigned to the property.
            Should be True for input values.
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
        modelpath: str or None, optional
            The period-delimited path after the record root element for
            where the parameter will be found in the built data model.  If set
            to None (default) then name will be used for modelpath.
        calcname: str or None, optional
            The name of the input parameter for the calculation function
            that corresponds to this value.  If set to None
            (default) then name will be used for calcname.
        templatekey: str or None, optional
            The name of the input file/template key that corresponds to this
            value.  If set to None (default) then name will be used for
            templatekey.
        templatedoc: str, optional
            The description of the template parameter to include in the
            calculation's templatedoc documentation.  Default value is '',
            i.e. no information.
        is_compare_term: bool, optional
            Indicates if the corresponding metadata value is included in
            the compare_terms list for direct comparison of values for
            determining the uniqueness of the calculation.  Default value
            is False (not included in compare_terms).
        compare_fterm_tol: float or None, optional
            An absolute tolerance to associate with the metadata value for use
            in the compare_fterms dict of the calculation to determine
            uniqueness.  If None (default) then the value will not be included
            in compare_fterms.  If a float value is given then the term will
            be included in compare_fterms with the given tolerance.
        """
        # Call parent super
        super().__init__(name, record,
                         defaultvalue=defaultvalue,
                         valuerequired=valuerequired,
                         allowedvalues=allowedvalues,
                         metadatakey=metadatakey,
                         metadataparent=metadataparent,
                         modelpath=modelpath)
        
        # Set default values of calcname and templatekey
        if calcname is None:
            calcname = self.name
        elif isinstance(calcname, bool):
            if calcname is True:
                raise TypeError('calcname can be None, False, or str')
        else:
            calcname = str(calcname)
        if templatekey is None:
            templatekey = self.name
        
        # Check compare term/fterm settings
        if is_compare_term is True and compare_fterm_tol is not None:
            raise ValueError('value cannot be added to both compare_terms and compare_fterms')
        if compare_fterm_tol is not None:
            compare_fterm_tol = float(compare_fterm_tol)

        # Save values to class attributes
        self.__is_compare_term = bool(is_compare_term)
        self.__compare_fterm_tol = compare_fterm_tol
        self.__calcname =  calcname
        self.__templatekey =  templatekey
        self.__templatedoc =  templatedoc

    def load_parameters_value(self, val):
        """
        Function to modify values when reading them in from an input parameter
        file.
        """
        return val

    def load_parameters(self, input_dict: dict):
        """
        Reads in the templatekey value from the input parameter file and
        saves it to the class attribute value.
        """
        if self.templatekey is None:
            return None
        
        if self.defaultvalue is None:
            val = input_dict[self.templatekey]
        else:
            val = input_dict.get(self.templatekey, self.defaultvalue)
        
        self.value = self.load_parameters_value(val)

    @property
    def is_compare_term(self) -> bool:
        """bool: Indicates if the value should be in compare_terms"""
        return self.__is_compare_term
    
    @property
    def compare_fterm_tol(self) -> Optional[float]:
        """float or None: tolerance to use for the value in compare_fterms"""
        return self.__compare_fterm_tol
    
    @property
    def calcname(self) -> Union[str, bool]:
        """str or bool: The calculation function parameter name to use"""
        return self.__calcname
    
    @property
    def templatekey(self) -> str:
        """str: the name to use for the parameter in the input file template"""
        return self.__templatekey
    
    @property
    def templatedoc(self) -> str:
        """str: The parameter description to use in templatedoc"""
        return self.__templatedoc
    
    def calc_inputs_value(self):
        """Function to modify values when passing them to the calculation function"""
        return self.value

    def calc_inputs(self, kwargs: dict):
        """
        Adds the value to the kwargs dict for the calculation function
        """
        if self.calcname is not False:
            kwargs[self.calcname] = self.calc_inputs_value()

