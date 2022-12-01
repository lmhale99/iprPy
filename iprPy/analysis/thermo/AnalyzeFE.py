# coding: utf-8

# Standard Python libraries
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# Local imports
from ...tools import num_deriv_3_point

class AnalyzeFE():
    """
    Supporting class for analyzing thermodynamic data from free_energy
    calculations performed at different temperatures.
    """
    
    def __init__(self,
                 df: pd.DataFrame,
                 G0: Optional[float] = None,
                 V0: Optional[float] = None,
                 Tmax: Optional[float] = None):
        """
        Parameters
        ----------
        df : pandas.DataFrame
            Metadata results for the iprPy free_energy calculation.
        G0 : float, optional
            Gibbs free energy per atom to use for 0K.  Default value of None
            will only use values from df.  Can also be set directly after init.
        V0 : float, optional
            Volume per atom to use for 0K.  Default value of None will only use
            values from df.  Can also be set directly after init.
        Tmax : float, optional
            The max temperature to use.  Default value of None will use all
            temperatures in df.  Can also be set directly after init.
        """

        # Check that all results are for the same pressure
        pressure = df.pressure.values.mean()
        assert np.allclose(pressure, df.pressure.values[0]), 'All results must be for the same pressure!'
        self.__p = pressure
        
        # Save values to df
        self.__df = df.sort_values('temperature')
        
        self.Tmax = Tmax
        self.G0 = G0
        self.V0 = V0
     
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
            assert count > 0, 'No temperatures found less than T_max!'
        self.__Tmax = value

    @property
    def G0(self) -> Optional[float]:
        """float or None: The Gibbs free energy per atom at 0K"""
        return self.__G0
    
    @G0.setter
    def G0(self, value: Optional[float]):
        if value is not None:
            value = float(value)
        self.__G0 = value
        
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
        Checks if G0 and V0 values are set.
        
        Returns
        -------
        bool
            True if both G0 and V0 are set.  False if both are unset.
        
        Raises
        ------
        ValueError
            If G0 or V0 is set and the other is not.
        
        """
        if self.G0 is None and self.V0 is None:
            return False
        elif self.G0 is not None and self.V0 is not None:
            return True
        else:
            raise ValueError('Both or neither G0, V0 must be set')
    
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
        V  = self.df.volume.values / self.df.natoms.values
        
        if self.has_0_values():
            V = np.array([self.V0] + V.tolist())
        
        return V[:len(self.T)]
        
    @property
    def G(self) -> np.ndarray:
        """np.ndarray: Values of Gibbs free energy per atom"""
        G = self.df.Gibbs.values
        
        if self.has_0_values():
            G = np.array([self.G0] + G.tolist())
        
        return G[:len(self.T)]
    
    @property
    def S(self) -> np.ndarray:
        """np.ndarray: Values of entropy per atom"""
        return - num_deriv_3_point(self.T, self.G)

    @property
    def Cp(self) -> np.ndarray:
        """np.ndarray: Values of constant pressure heat capacity per atom"""
        return self.T * num_deriv_3_point(self.T, self.S)

    @property
    def H(self) -> np.ndarray:
        """np.ndarray: Values of enthalpy per atom"""
        return self.G + self.T * self.S