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
    
    def __str__(self):
        return 'iprPy.Calculation (' + self.style + ')' 
    
    @property
    def style(self):
        return self.__style
    
    def data_model(self, input_dict, results_dict=None):
        """Generates a data model for the named calculation."""
        
        try: 
            data_model = self.__calc_module.data_model
        except AttributeError:
            raise AttributeError('Calculation (' + self.style + ') has no attribute data_model') 
        else:
            return data_model(input_dict, results_dict)
        
    def read_input(self, fp, *args):
        """Reads the calc_*.in input commands for the named calculation."""
        
        try: 
            read_input = self.__calc_module.read_input
        except AttributeError:
            raise AttributeError('Calculation (' + self.style + ') has no attribute read_input') 
        else:
            return read_input(fp, *args)   
            
    @property
    def template(self):
        """Reads the calc_*.in input commands for the named calculation."""
        
        try: 
            template = self.__calc_module.template  
        except AttributeError:
            raise AttributeError('Calculation (' + self.style + ') has no attribute template')
        else:
            return template()

    @property
    def files(self):
        """Yields the list of files necessary for a calculation to run"""
        
        try: 
            files = self.__calc_module.files
        except AttributeError:
            raise AttributeError('Calculation (' + self.style + ') has no attribute files')
        else:
            return files()
            
    @property
    def prepare_keys(self):
        """Yields the list of keys recognized by the prepare script"""
        try: 
            prepare_keys = self.__calc_module.prepare_keys
        except AttributeError:
            raise AttributeError('Calculation (' + self.style + ') has no attribute prepare_keys')
        else:
            return prepare_keys
        
    def prepare(self, dbase, run_directory, *args, **kwargs):
        """Calls the calculation's prepare function"""
        try: 
            prepare = self.__calc_module.prepare
        except AttributeError:
            raise AttributeError('Calculation (' + self.style + ') has no attribute prepare') 
        else:
            return prepare(dbase, run_directory, *args, **kwargs) 