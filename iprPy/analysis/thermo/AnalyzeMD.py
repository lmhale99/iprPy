# coding: utf-8

# Standard Python libraries
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# Local imports
from ...tools import num_deriv_3_point

class AnalyzeMD():
    """
    Supporting class for analyzing thermodynamic data from relax_dynamic
    calculations performed at different temperatures.
    """

    def __init__(self,
                 df: pd.DataFrame,
                 natoms: int = 1,
                 U0: Optional[float] = None,
                 V0: Optional[float] = None,
                 Tmax: Optional[float] = None):

        # Solid relaxes list pressures separately
        if 'pressure_xx' in df:
            # Check that all results are for the same pressure
            pressures = np.hstack([df.pressure_xx.values,
                                df.pressure_yy.values,
                                df.pressure_zz.values])
            pressure = pressures.mean()
            assert np.allclose(pressure, pressures), 'All results must be for the same pressure!'
        elif 'pressure' in df:
            pressure = df.pressure.values
        self.__p = pressure

        # Save values to df
        self.__df = df.sort_values('temperature')

        self.natoms = natoms
        self.U0 = U0
        self.V0 = V0
        self.Tmax = Tmax

    @property
    def df(self) -> pd.DataFrame:
        """pandas.DataFrame: The raw calculation results"""
        return self.__df

    @property
    def Tmax(self) -> Optional[float]:
        """float or None: The max temperature to include in the results"""
        return self.__Tmax

    @Tmax.setter
    def Tmax(self, value: Optional[float]):
        if value is not None:
            value = float(value)
            count = np.sum(self.df.temperature <= value)
            assert count > 0, 'No temperatures found less than Tmax!'
        self.__Tmax = value

    @property
    def U0(self) -> Optional[float]:
        """float or None: The internal energy per atom at 0K"""
        return self.__U0

    @U0.setter
    def U0(self, value: Optional[float]):
        if value is not None:
            value = float(value)
        self.__U0 = value

    @property
    def V0(self) -> Optional[float]:
        """float or None: The volume  per atom at 0K"""
        return self.__V0

    @V0.setter
    def V0(self, value: Optional[float]):
        if value is not None:
            value = float(value)
        self.__V0 = value

    @property
    def p(self) -> float:
        """float: The pressure used for all results"""
        return self.__p

    def has_0_values(self) -> bool:
        """
        Checks if U0 and V0 values are set.
        
        Returns
        -------
        bool
            True if both U0 and V0 are set.  False if both are unset.
        
        Raises
        ------
        ValueError
            If U0 or V0 is set and the other is not.
        
        """
        if self.U0 is None and self.V0 is None:
            return False
        elif self.U0 is not None and self.V0 is not None:
            return True
        else:
            raise ValueError('Both or neither U0, V0 must be set')

    @property
    def T(self) -> np.ndarray:
        """np.ndarray: Values of temperature"""
        T = self.df.temperature.values

        if self.has_0_values():
            T = np.array([0.0] + T.tolist())

        if self.Tmax is not None:
            T = T[T <= self.Tmax]

        return T

    @property
    def V(self) -> np.ndarray:
        """np.ndarray: Values of volume per atom"""
        if 'lx' in self.df:
            V = self.df.lx.values * self.df.ly.values * self.df.lz.values / self.natoms
        else:
            V = self.df.volume

        if self.has_0_values():
            V = np.array([self.V0] + V.tolist())

        return V[:len(self.T)]

    @property
    def U(self) -> np.ndarray:
        """np.ndarray: Values of internal eneregy per atom"""
        U = self.df.E_total.values

        if self.has_0_values():
            U = np.array([self.U0] + U.tolist())

        return U[:len(self.T)]

    @property
    def H(self) -> np.ndarray:
        """np.ndarray: Values of enthalpy per atom"""
        return self.U + self.V * self.p

    @property
    def Cp(self) -> np.ndarray:
        """np.ndarray: Values of constant pressure heat capacity per atom"""
        return num_deriv_3_point(self.T, self.H)
