# coding: utf-8

# Standard Python libraries
from typing import Optional
import warnings

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

import atomman.unitconvert as uc
from atomman import Box

from scipy.optimize import curve_fit

# Local imports
from ...tools import num_deriv_3_point

class Thermo():
    """
    Base thermodynamic class for use with below
    """

    def __init__(self,
                 df: pd.DataFrame,
                 p: np.ndarray,
                 V: np.ndarray):
        """
        Initializes a Thermo object by extracting data from
        md_solid_properties records.  Values for T, U, H, G and F will be extracted
        along with potential metadata.

        
        Parameters
        ----------
        df : pandas.DataFrame
            The metadata() information obtained from the md_solid_properties or
            md_liquid_properties records.  The dataframe should already have been
            sorted by temperature and had any unwanted values parsed out.
        """

        # Set default poly fit parameters
        self.__H_poly_params = None
        self.__S0 = None
        self.__G0 = None

        # Extract common metadata
        self.__potential_LAMMPS_key = df.potential_LAMMPS_key.values[0]
        self.__potential_LAMMPS_id = df.potential_LAMMPS_id.values[0]
        self.__potential_key = df.potential_key.values[0]
        self.__potential_id = df.potential_id.values[0]
        self.__composition = df.composition.values[0]

        # Extract thermodynamic data
        self.__T = df['T (K)'].values
        self.__U = uc.set_in_units(df['U (eV/atom)'].values, 'eV')
        self.__H = uc.set_in_units(df['H (eV/atom)'].values, 'eV')
        self.__G = uc.set_in_units(df['G (eV/atom)'].values, 'eV')
        self.__F = uc.set_in_units(df['F (eV/atom)'].values, 'eV')

        # Set other thermodynamic data
        self.__p = p
        self.__V = V

    
    @property
    def potential_LAMMPS_key(self) -> str:
        """str: The UUID key for the interatomic potential implementation used"""
        return self.__potential_LAMMPS_key
    
    @property
    def potential_LAMMPS_id(self) -> str:
        """str: The ID for the interatomic potential implementation used"""
        return self.__potential_LAMMPS_id
    
    @property
    def potential_key(self) -> str:
        """str: The UUID key for the interatomic potential model used"""
        return self.__potential_key
    
    @property
    def potential_id(self) -> str:
        """str: The ID for the interatomic potential model used"""
        return self.__potential_id
    
    @property
    def composition(self) -> str:
        """str: The material composition"""
        return self.__composition

    @property
    def p(self) -> np.ndarray:
        """numpy.ndarray: The pressure values"""
        return self.__p
    
    @property
    def T(self) -> np.ndarray:
        """numpy.ndarray: The temperature values"""
        return self.__T
    
    @property
    def U(self) -> np.ndarray:
        """numpy.ndarray: The per-atom energy values"""
        return self.__U

    @property
    def H(self) -> np.ndarray:
        """numpy.ndarray: The per-atom enthalpy values"""
        return self.__H
    
    @property
    def G(self) -> np.ndarray:
        """numpy.ndarray: The per-atom Gibbs free energy values"""
        return self.__G
    
    @property
    def F(self) -> np.ndarray:
        """numpy.ndarray: The per-atom Helmholtz free energy values"""
        return self.__F
    
    @property
    def V(self) -> np.ndarray:
        """numpy.ndarray: The per-atom volume values"""
        return self.__V

    @property
    def Cp(self) -> np.ndarray:
        """np.ndarray: The per-atom constant pressure heat capacity computed numerically from dH/dT"""
        return num_deriv_3_point(self.T, self.H)

    @property
    def S(self) -> np.ndarray:
        """np.ndarray: The per-atom entropy computed numerically from (H - G) / T"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            S = (self.H - self.G) / self.T
        return S
        #return - num_deriv_3_point(self.T, self.G)
    
    @property
    def S0(self) -> float:
        """float: The per-atom entropy at 0K (estimated from a polynomial fit)"""
        if self.__S0 is None:
            raise ValueError('S0 not estimated! Call fit_poly_model first()!')
        return self.__S0
    
    @property
    def H0(self) -> float:
        """float: The per-atom enthalpy energy at 0K (estimated from a polynomial fit)"""
        if self.__H0 is None:
            raise ValueError('H0 not estimated! Call fit_poly_model first()!')
        return self.__H0
    
    @property
    def H_poly_params(self) -> list:
        """list: The fitting parameters found for the polyhedral model"""
        if self.__H_poly_params is None:
            raise ValueError('H_poly_params not estimated! Call fit_poly_model first()!')
        return self.__H_poly_params
    
    def fit_poly_model(self,
                       order: int = 4,
                       Tmax: Optional[float] = None):
        """
        Builds a polynomial model of H and finds the S0 constant allowing for
        the H_poly, G_poly, S_poly and Cp_poly methods to work.

        Parameters
        ----------
        order : int, optional
            The polynomial order to use.  Values currently limited to 2, 3, 4, 5, 6.
            Default is 4.
        Tmax : float or None, optional
            The maximum temperature for the measured H(T) and G(T) values to use
            for fitting.  If None (default), then all T, H, G values will be used.
            Ideally, the values should already be pre-filtered by the hastransformed
            flag in the md_solid_properties records so this is optional.
        """
        if order < 2 or order > 6:
            raise ValueError('order is currently limited to values 2, 3, 4, 5, or 6')

        if self.T[0] == 0.0:
            self._fit_H_model_H0(order, Tmax)
        else:
            self._fit_H_model(order, Tmax)
        self._fit_G_model(order, Tmax)

    def _fit_H_model_H0(self,
                        order: int = 4,
                        Tmax: Optional[float] = None):
        """
        Find polynomial fit for H when H0 = H(T=0) is known.
        """
        
        if order < 2 or order > 6:
            raise ValueError('order is currently limited to values 2, 3, 4, 5, or 6')

        # Extract T, H, G
        T = self.T
        H = self.H
        H0 = H[0]

        # Trim the values by Tmax
        if Tmax is not None:
            usevals = T <= Tmax
            T = T[usevals]
            H = H[usevals]

        # Define the polynomial H models to use for fitting
        def fit_H2(T, a, b):
            return H0 + a * T + b * T**2
        def fit_H3(T, a, b, c):
            return fit_H2(T, a, b) + c * T**3
        def fit_H4(T, a, b, c, d):
            return fit_H3(T, a, b, c) + d * T**4
        def fit_H5(T, a, b, c, d, e):
            return fit_H4(T, a, b, c, d) + e * T**5
        def fit_H6(T, a, b, c, d, e, f):
            return fit_H5(T, a, b, c, d, e) + f * T**6
        fit_H = {2: fit_H2, 3: fit_H3, 4: fit_H4, 5: fit_H5, 6: fit_H6}
        
        # Fit H vs T to the polynomial to get the polynomial parameters
        params = curve_fit(fit_H[order], T, H)[0]
        
        # Save the fitting parameters
        self.__H_poly_params = params
        self.__H0 = H0

    def _fit_H_model(self,
                     order: int = 4,
                     Tmax: Optional[float] = None):
        """
        Find polynomial fit for H when H0 = H(T=0) is not known.
        """
        if order < 2 or order > 6:
            raise ValueError('order is currently limited to values 2, 3, 4, 5, or 6')

        # Extract T, H, G
        T = self.T
        H = self.H

        # Trim the values by Tmax
        if Tmax is not None:
            usevals = T <= Tmax
            T = T[usevals]
            H = H[usevals]

        # Define the polynomial H models to use for fitting
        def fit_H2(T, H0, a, b):
            return H0 + a * T + b * T**2
        def fit_H3(T, H0, a, b, c):
            return fit_H2(T, H0, a, b) + c * T**3
        def fit_H4(T, H0, a, b, c, d):
            return fit_H3(T, H0, a, b, c) + d * T**4
        def fit_H5(T, H0, a, b, c, d, e):
            return fit_H4(T, H0, a, b, c, d) + e * T**5
        def fit_H6(T, H0, a, b, c, d, e, f):
            return fit_H5(T, H0, a, b, c, d, e) + f * T**6
        fit_H = {2: fit_H2, 3: fit_H3, 4: fit_H4, 5: fit_H5, 6: fit_H6}
        
        # Fit H vs T to the polynomial to get the polynomial parameters
        params = curve_fit(fit_H[order], T, H)[0]
        
        # Save the fitting parameters
        self.__H_poly_params = params[1:]
        self.__H0 = params[0]

    def _fit_G_model(self,
                     order: int = 4,
                     Tmax: Optional[float] = None):
        if order < 2 or order > 6:
            raise ValueError('order is currently limited to values 2, 3, 4, 5, or 6')

        # Extract T, G
        T = self.T
        G = self.G
        G0 = self.H0

        # extract params
        params = self.H_poly_params

        # Trim the values by Tmax
        if Tmax is not None:
            usevals = T <= Tmax
            T = T[usevals]
            G = G[usevals]

        # Trim the values that are not values
        isfinite = np.isfinite(G)
        T = T[isfinite]
        G = G[isfinite]

        # Define the polynomial G models to use for fitting
        def G_T0(T):
            return 0.0
        def G_T1(T):
            return params[0] * T * (np.log(T) - 1)
        def fit_G2(T, S0):
            return G0 - S0 * T - np.piecewise(T, (T==0), (G_T0, G_T1)) - params[1] * T**2
        def fit_G3(T, S0):
            return fit_G2(T, S0) - (1/2) * params[2] * T**3
        def fit_G4(T, S0):
            return fit_G3(T, S0) - (1/3) * params[3] * T**4
        def fit_G5(T, S0):
            return fit_G4(T, S0) - (1/4) * params[4] * T**5
        def fit_G6(T, S0):
            return fit_G5(T, S0) - (1/5) * params[5] * T**6
        fit_G = {2: fit_G2, 3: fit_G3, 4: fit_G4, 5: fit_G5, 6: fit_G6}
        
        # Fit G vs T to the polynomial to get S0
        S0 = curve_fit(fit_G[order], T, G)[0][0]

        self.__S0 = S0


    def H_poly(self, T):
        """Per-atom enthalpy estimates using the polynomial model."""
        params = self.H_poly_params
        H0 = self.H0

        H = np.full_like(T, H0)
        for i, a in enumerate(params):
            H += a * T**(i+1)
        return H
    
    def Cp_poly(self, T):
        """Per-atom constant pressure heat capacity estimates using the polynomial model."""
        params = self.H_poly_params

        Cp = np.zeros_like(T)
        for i, a in enumerate(params):
            Cp += (i+1) * a * T**(i)
        return Cp

    def S_poly(self, T):
        """Per-atom entropy estimates using the polynomial model."""
        params = self.H_poly_params
        S0 = self.S0

        S = np.full_like(T, S0)
        for i, a in enumerate(params):
            if i == 0:
                def S_T0(T):
                    return 0.0
                def S_T1(T):
                    return a * np.log(T)
                S +=  np.piecewise(T, (T==0), (S_T0, S_T1))
            else:
                S += ((i+1) / (i)) * a * T**(i)
        return S
                
    def G_poly(self, T):
        """Per-atom Gibbs free energy estimates using the polynomial model."""
        params = self.H_poly_params
        G0 = self.H0
        S0 = self.S0

        G = np.full_like(T, G0) - np.full_like(T, S0) * T
        for i, a in enumerate(params):
            if i == 0:
                def G_T0(T):
                    return 0.0
                def G_T1(T):
                    return a * T * (np.log(T) - 1)
                G -= np.piecewise(T, (T==0), (G_T0, G_T1))
            else:
                G -= (1 / i) * a * T**(i+1)
        return G


class ThermoSolid(Thermo):
    """
    Collects thermodynamic data from md_solid_properties records for plotting
    and using thermodynamic transformations to estimate other properties.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes a ThermoSolid object by extracting data from
        md_solid_properties records.

        
        Parameters
        ----------
        df : pandas.DataFrame
            The metadata() information obtained from MDSolidProperties records.
            The data should all be for the same potential and relaxed_crystal_key,
            and for simulations ran at 0 pressure.
        """

        # Check that there is only one relaxed_crystal_key in the dataframe
        if len(set(df.relaxed_crystal_key)) > 1:
            raise ValueError('Multiple relaxed_crystal_key values found in df!')

        # Filter out transformed results
        parsed_df = df[df.untransformed]

        # Sort values by temperature
        sorted_df = parsed_df.sort_values('T (K)')

        # Extract pressures
        Px = sorted_df['Pxx (GPa)'].values
        Py = sorted_df['Pyy (GPa)'].values
        Pz = sorted_df['Pzz (GPa)'].values
        p = uc.set_in_units((Px + Py + Pz) / 3, 'GPa')

        # Filter by pressure
        sorted_df = sorted_df[np.isclose(p, 0.0)]
        p = p[np.isclose(p, 0.0)]

        # Compute volumes
        def get_volume(series) -> float:
            box = Box(a=series.a, b=series.b, c=series.c, alpha=series.alpha, beta=series.beta, gamma=series.gamma)
            return box.volume / series.natoms
        V = uc.set_in_units(sorted_df.apply(get_volume, axis=1), 'angstrom^3')

        # Call base Thermo's init
        super().__init__(sorted_df, p, V)

        # Extract common metadata
        self.__relaxed_crystal_key = df.relaxed_crystal_key.values[0]
        self.__family = df.family.values[0]


    @property
    def relaxed_crystal_key(self) -> str:
        """str: The UUID key for the original relaxed_crystal record"""
        return self.__relaxed_crystal_key
    
    @property
    def family(self) -> str:
        """str: The crystal prototype/reference family name"""
        return self.__family

class ThermoLiquid(Thermo):
    """
    Collects thermodynamic data from md_liquid_properties records for plotting
    and using thermodynamic transformations to estimate other properties.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes a ThermoLiquid object by extracting data from
        md_liquid_properties records.

        
        Parameters
        ----------
        df : pandas.DataFrame
            The metadata() information obtained from MDLiquidProperties records.
            The data should all be for the same potential and relaxed_crystal_key,
            and for simulations ran at 0 pressure.
        """

        # Check that there is only one relaxed_crystal_key in the dataframe
        if len(set(df.potential_LAMMPS_key)) > 1 or len(set(df.composition)) > 1:
            raise ValueError('Multiple potential or composition values found in df!')

        # Filter out transformed results
        parsed_df = df[df.isliquid]

        # Sort values by temperature
        sorted_df = parsed_df.sort_values('T (K)')

        # Extract pressures
        p = uc.set_in_units(sorted_df['P (MPa)'].values, 'MPa')

        # Filter by pressure
        sorted_df = sorted_df[np.isclose(p, 0.0)]
        p = p[np.isclose(p, 0.0)]

        # Extract volumes
        V = uc.set_in_units(sorted_df['V (m^3)'].values, 'm^3')

        # Call base Thermo's init
        super().__init__(sorted_df, p, V)
