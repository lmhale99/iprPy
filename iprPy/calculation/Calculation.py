from yabadabado.calculation import Calculation as yaba_Calculation

class Calculation(yaba_Calculation):

    def _init_values(self):

        super()._init_values()

        self._add_value('calculation_subset', 'calculation',
                        recordclass = 'subset_iprpycalc',
                        loadorder = 0,
                        description = 'Core iprPy calculation info')

        self.calculation.script = f'calc_{self.calc_style}'