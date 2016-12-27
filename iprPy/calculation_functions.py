from .calculations import calculations_dict

def calculation_styles():
    """Returns a list of the styles of the loaded calculations."""
    return calculations_dict.keys()
        
class Calculation(object):
    """Class for handling different calculations in the same fashion"""        
    
    def __init__(self, style):
        
        #Check if calculation style exists
        try:
            self.__calc_module = calculations_dict[style]
        except KeyError:
            raise KeyError('No calculation style ' + style + ' imported')
        
        self.__style = style
    
    @property
    def style(self):
        return self.__style
    
    def data_model(self, input_dict, results_dict=None):
        """Generates a data model for the named calculation."""
        
        try: 
            return self.__calc_module.data_model(input_dict, results_dict)
        except AttributeError:
            raise AttributeError('Calculation ' + self.__style + ' has no attribute data_model') 
        
    def read_input(self, fp, *args):
        """Reads the calc_*.in input commands for the named calculation."""
        
        try: 
            return self.__calc_module.read_input(fp, *args)   
        except AttributeError:
            raise AttributeError('Calculation ' + self.__style + ' has no attribute read_input') 

    @property
    def template(self):
        """Reads the calc_*.in input commands for the named calculation."""
        
        try: 
            return self.__calc_module.template()  
        except AttributeError:
            raise AttributeError('Calculation ' + self.__style + ' has no attribute template')

    @property
    def files(self):
        """Yields the list of files necessary for a calculation to run"""
        
        try: 
            return self.__calc_module.files()  
        except AttributeError:
            raise AttributeError('Calculation ' + self.__style + ' has no attribute files')