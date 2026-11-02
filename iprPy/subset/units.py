
from yabadabado.calculation import CalculationSubset

__all__ = ['Units']

class Units(CalculationSubset):
    """Handles calculation terms associated with input/output units settings"""

############################# Core properties ##################################

    def _init_values(self):

        self._add_value('input_str', 'length_unit',
                        defaultvalue = 'angstrom',
                        calcname = False,
                        modelpath = None,
                        metadatakey = False,
                        description = 'The unit of length to use for input/output values')

        self._add_value('input_str', 'pressure_unit',
                        defaultvalue = 'GPa',
                        calcname = False,
                        modelpath = None,
                        metadatakey = False,
                        description = 'The unit of pressure to use for input/output values')

        self._add_value('input_str', 'energy_unit',
                        defaultvalue = 'eV',
                        calcname = False,
                        modelpath = None,
                        metadatakey = False,
                        description = 'The unit of energy to use for input/output values')

        self._add_value('input_str', 'force_unit',
                        defaultvalue = 'eV/angstrom',
                        calcname = False,
                        modelpath = None,
                        metadatakey = False,
                        description = 'The unit of force to use for input/output values')
    
    @property
    def modelroot(self):
        return 'units'

####################### Parameter file interactions ###########################

    @property
    def template_header(self) -> str:
        return '# Input/Output Units'
    
    def fillunit(self, unit):
        """
        Fills in unit definitions with the set unit values.

        Parameters
        ----------
        unit : str
            A unit definition that may contain placeholders corresponding to
            the names of the values in the Units object.  These placeholders
            will be replaced with the corresponding values. E.g. if unit is
            'length_unit^2' and length_unit='nm', then unit is updated to be
            'nm^2'.
        """
        for value_object in self.value_objects:
            if value_object.name in unit:
                unit = unit.replace(value_object.name, value_object.value)

        return unit