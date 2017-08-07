from __future__ import division, absolute_import, print_function

from .calculations import calculations_dict

__all__ = ['calculation_styles', 'Calculation']

def calculation_styles():
    """
    Returns
    -------
    list of str
        All calculation styles successfully loaded.
    """
    return calculations_dict.keys()
        
class Calculation(object):
    """
    Class for handling different calculation styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.calculations submodule.
    """
    
    def __init__(self, style):
        """
        Initializes a Calculation object for a given style.
        
        Parameters
        ----------
        style : str
            The calculation style.
        
        Raises
        ------
        KeyError
            If the calculation style is not available.
        """
        
        # Check if calculation style exists
        try:
            self.__calc_module = calculations_dict[style]
        except KeyError:
            raise KeyError('No calculation style ' + style + ' imported')
        
        self.__style = style
    
    def __str__(self):
        """
        Returns
        -------
        str
            The string representation of the calculation:
            iprPy.Calculation (<style>).
        """
        return 'iprPy.Calculation (' + self.style + ')'
    
    @property
    def style(self):
        """str: The calculation's style."""
        return self.__style
    
    def process_input(self, input_dict, UUID=None, build=True):
        """
        Processes str input parameters, assigns default values if needed, and
        generates new, more complex terms as used by the calculation.
        
        Parameters
        ----------
        input_dict :  dict
            Dictionary containing the calculation input parameters with string
            values.  The allowed keys depends on the calculation style.
        UUID : str, optional
            Unique identifier to use for the calculation instance.  If not 
            given and a 'UUID' key is not in input_dict, then a random UUID4 
            hash tag will be assigned.
        build : bool, optional
            Indicates if all complex terms are to be built.  A value of False
            allows for default values to be assigned even if some inputs 
            required by the calculation are incomplete. (Default is True.)
        
        Raises
        ------
        AttributeError
            If process_input is not defined for calculation style.
        """
        
        try: 
            process_input = self.__calc_module.process_input
        except AttributeError:
            raise AttributeError('Calculation (' + self.style
                                 + ') has no attribute process_input')
        else:
            process_input(input_dict, UUID=UUID, build=build)
    
    @property
    def template(self):
        """str: The template to use for generating calc.in files."""
        
        try: 
            template = self.__calc_module.template  
        except AttributeError:
            raise AttributeError('Calculation (' + self.style 
                                 + ') has no attribute template')
        else:
            return template()

    @property
    def files(self):
        """
        iter of str: Path to each file required by the calculation.
        """
        
        try: 
            files = self.__calc_module.files
        except AttributeError:
            raise AttributeError('Calculation (' + self.style 
                                 + ') has no attribute files')
        else:
            return files()
            
    @property
    def prepare_keys(self):
        """dict: lists 'singular' and 'multi' keys used by prepare."""
        try: 
            prepare_keys = self.__calc_module.prepare_keys
        except AttributeError:
            raise AttributeError('Calculation (' + self.style 
                                 + ') has no attribute prepare_keys')
        else:
            return prepare_keys
        
    def prepare(self, dbase, run_directory, *args, **kwargs):
        """
        Calls the calculation's prepare function.
        
        Parameters
        ----------
        dbase : iprPy.Database
            The database to use with preparing instances of the calculation.
        run_directory : str
            The directory path where all calculation instances being prepared
            are to be placed.
        *args
            Any calculation-specific arguments.
        **kwargs
            Any calculation-specific keyword arguments.
        
        Raises
        ------
        AttributeError
            If prepare is not defined for calculation style.
        """
        try: 
            prepare = self.__calc_module.prepare
        except AttributeError:
            raise AttributeError('Calculation (' + self.style + ') has no attribute prepare') 
        else:
            return prepare(dbase, run_directory, *args, **kwargs) 