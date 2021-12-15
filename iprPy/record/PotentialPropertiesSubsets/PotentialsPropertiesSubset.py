class PotentialsPropertiesSubset():
    """Generic PotentialsPropertiesSubset class"""
    
    def __init__(self, parent):
        self.__parent = parent
        
        # Set exists to False if allowed
        try:
            self.exists = False
        except:
            pass

    @property
    def parent(self):
        """The parent PotentialProperties object that is used by this calculation"""
        return self.__parent

    @property
    def exists(self):
        """bool : True if results for this property exist"""
        return self.__exists

    @exists.setter
    def exists(self, value):
        self.__exists = bool(value)

    def load_model(self, model):
        raise NotImplementedError()

    def build_model(self, model):
        raise NotImplementedError()

    def metadata(self, meta):
        raise NotImplementedError()
