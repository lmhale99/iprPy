# coding: utf-8

# Standard Python libraries

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

from ...calculation import Calculation

class AnalyzeQHA():
    """
    Supporting class for analyzing thermodynamic data from a phonon calculation
    record that includes QHA results.
    """
    def __init__(self,
                 phonon,
                 natoms=1):
        """
        Parameters
        ----------
        phonon : iprPy.calculation.phonon.CalculationPhonon object
            Results from a phonon and QHA calculation.
        natoms : int, optional
            The number of atoms in the unit cell used with the phonon
            calculation.  Can be set/changed directly after init.
        """
        
        self.__phonon = phonon
        self.__natoms = natoms

    @property
    def phonon(self) -> Calculation:
        """The CalculationPhonon object"""
        return self.__phonon

    @property
    def natoms(self) -> int:
        """int: The number of atoms used in the unit cell for the phonon calculation"""
        return self.__natoms
    
    @natoms.setter
    def natoms(self, value: int):
        value = int(value)
        assert len(value) > 0
        self.__natoms = int(value)
        
    @property
    def U0(self) -> float:
        """float: The internal energy per atom estimated at 0K"""
        return self.phonon.E0 / self.natoms
    
    @property
    def V0(self) -> float:
        """float: The volume per atom estimated at 0K"""
        return self.phonon.V0 / self.natoms
    
    @property
    def G0(self) -> float:
        """float: The Gibbs free energy per atom estimated at 0K"""
        return self.G[0]
    
    @property
    def einstein_temperature(self) -> float:
        """float: The Einstein temperature evaluated by comparing G0 and U0"""
        return 2 * (self.G0 - self.U0) / (3 * uc.unit['kB'])
    
    @property
    def T(self) -> np.ndarray:
        """np.ndarray: The temperatures at which the phonon/QHA thermo results are evaluated at"""
        return self.phonon.thermal['temperature']
        
    @property
    def F(self) -> np.ndarray:
        """np.ndarray: Values of Helmholtz free energy per atom"""
        return self.phonon.thermal['Helmholtz'] / self.natoms
        
    @property
    def S(self) -> np.ndarray:
        """np.ndarray: Values of entropy per atom"""
        return self.phonon.thermal['entropy'] / self.natoms
        
    @property
    def Cv(self) -> np.ndarray:
        """np.ndarray: Values of constant volume heat capacity per atom"""
        return self.phonon.thermal['heat_capacity_v'] / self.natoms
        
    @property
    def V(self) -> np.ndarray:
        """np.ndarray: Values of volume per atom"""
        return self.phonon.thermal['volume'] / self.natoms
        
    @property
    def alpha(self) -> np.ndarray:
        """np.ndarray: Values of thermal expansion"""
        return self.phonon.thermal['thermal_expansion']

    @property
    def G(self) -> np.ndarray:
        """np.ndarray: Values of Gibbs free energy per atom"""
        return self.phonon.thermal['Gibbs'] / self.natoms

    @property
    def Cp_num(self) -> np.ndarray:
        """np.ndarray: Values of constant pressure heat capacity evaulated numerically"""
        return self.phonon.thermal['heat_capacity_p_numerical'] / self.natoms
        
    @property
    def Cp_poly(self) -> np.ndarray:
        """np.ndarray: Values of constant pressure heat capacity evaulated with a polynomial fit"""
        return self.phonon.thermal['heat_capacity_p_polyfit'] / self.natoms
        
    @property
    def B(self) -> np.ndarray:
        """np.ndarray: Values of bulk modulus"""
        return self.phonon.thermal['bulk_modulus']