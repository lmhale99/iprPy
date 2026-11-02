from yabadabado.calculation import CalculationSubset

import atomman as am

from .. import __version__ as iprPy_version

__all__ = ['IprPyCalc']

class IprPyCalc(CalculationSubset):
    """Handles calculation terms for LAMMPS executable commands"""

############################# Core properties #################################

    def _init_values(self):

        self._add_value('str', 'iprPy_version',
                        modelpath = 'iprPy-version',
                        defaultvalue = iprPy_version,
                        description = 'The iprPy version used')

        self._add_value('str', 'atomman_version',
                        modelpath = 'atomman-version',
                        defaultvalue=am.__version__,
                        description = 'The atomman version used')

        self._add_value('str', 'script',
                        description = "Field retained for compatibility: is the calculation style with a 'calc_' prefix")

########################### Calculation interactions ##########################

    @property
    def modelroot(self):
        return 'calculation'

    @property
    def modelsortkeys(self) -> list | None:
        return [
            'iprPy-version',
            'atomman-version',
            'script',
            'branch',
        ]