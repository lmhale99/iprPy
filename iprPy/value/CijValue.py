from typing import Any, Optional, Union

from yabadaba.value import Value

from DataModelDict import DataModelDict as DM

from atomman import unitconvert as uc
from atomman import ElasticConstants

class CijValue(Value):
    """
    Class for representing atomman.ElasticConstants objects as yabadaba values.
    """


    def set_value_mod(self, val: Union[ElasticConstants, DM, None]):

        if isinstance(val, ElasticConstants):
            return val
        
        if val is None:
            try:
                val = self.record.model
                assert val is not None
                DM(self.record.model).find('elastic-constants')
            except:
                return None
        
        return ElasticConstants(model=val)

    def build_model_value(self):
        """Function to modify how values are represented in the model"""
        if self.value is not None:
            return self.value.model(unit='GPa')['elastic-constants']
    
    def load_model_value(self, val):
        """Function to modify how values are interpreted from the model"""
        return DM([('elastic-constants', val)])

    def metadata(self, meta):
        """
        Adds the parameter to the record's metadata dict.

        Parameters
        ----------
        meta : dict
            The metadata dict being built for the record.
        """
        if self.value is not None:
            meta['C11 (GPa)'] = uc.get_in_units(self.value.Cij[0,0], 'GPa')
            meta['C12 (GPa)'] = uc.get_in_units(self.value.Cij[0,1], 'GPa')
            meta['C13 (GPa)'] = uc.get_in_units(self.value.Cij[0,2], 'GPa')
            meta['C14 (GPa)'] = uc.get_in_units(self.value.Cij[0,3], 'GPa')
            meta['C15 (GPa)'] = uc.get_in_units(self.value.Cij[0,4], 'GPa')
            meta['C16 (GPa)'] = uc.get_in_units(self.value.Cij[0,5], 'GPa')
            meta['C22 (GPa)'] = uc.get_in_units(self.value.Cij[1,1], 'GPa')
            meta['C23 (GPa)'] = uc.get_in_units(self.value.Cij[1,2], 'GPa')
            meta['C24 (GPa)'] = uc.get_in_units(self.value.Cij[1,3], 'GPa')
            meta['C25 (GPa)'] = uc.get_in_units(self.value.Cij[1,4], 'GPa')
            meta['C26 (GPa)'] = uc.get_in_units(self.value.Cij[1,5], 'GPa')
            meta['C33 (GPa)'] = uc.get_in_units(self.value.Cij[2,2], 'GPa')
            meta['C34 (GPa)'] = uc.get_in_units(self.value.Cij[2,3], 'GPa')
            meta['C35 (GPa)'] = uc.get_in_units(self.value.Cij[2,4], 'GPa')
            meta['C36 (GPa)'] = uc.get_in_units(self.value.Cij[2,5], 'GPa')
            meta['C44 (GPa)'] = uc.get_in_units(self.value.Cij[3,3], 'GPa')
            meta['C45 (GPa)'] = uc.get_in_units(self.value.Cij[3,4], 'GPa')
            meta['C46 (GPa)'] = uc.get_in_units(self.value.Cij[3,5], 'GPa')
            meta['C55 (GPa)'] = uc.get_in_units(self.value.Cij[4,4], 'GPa')
            meta['C56 (GPa)'] = uc.get_in_units(self.value.Cij[4,5], 'GPa')
            meta['C66 (GPa)'] = uc.get_in_units(self.value.Cij[5,5], 'GPa')

    @property
    def _default_queries(self) -> dict:
        """dict: Default query operations to associate with the Parameter style"""
        return {}