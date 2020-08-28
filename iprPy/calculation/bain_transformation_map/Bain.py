# coding: utf-8
# Standard library imports
from copy import deepcopy

import numpy as np

import matplotlib.pyplot as plt

import atomman as am

class Bain():
    """
    Atomic structure generator and results plotter for exploring the
    generalized Bain transformation energy map through the generation of
    intermediate tetragonal systems from ideal bcc to fcc.
    """
    def __init__(self, a_bcc=None, a_fcc=None, symbol=None):
        """
        Initializes the Bain structure generator.

        Parameters
        ----------
        a_bcc : float, optional
            The bcc lattice constant. If not given, will use the ideal value
            of a_fcc * sqrt(2/3).  At least one of a_bcc and a_fcc is required.
        a_fcc : float, optional
            The fcc lattice constant. If not given, will use the ideal value
            of a_bcc * sqrt(3/2).  At least one of a_bcc and a_fcc is required.
        symbol : str, optional
            The element model symbol to assign to the atoms in the generated
            atomic configurations.
        """

        # Set symbol information
        self.symbol = symbol
        
        # Set a_bcc and a_fcc
        if a_bcc is None:
            if a_fcc is not None:
                a_bcc = a_fcc * (2/3)**0.5
            else:
                raise ValueError('At least one of a_bcc and a_fcc is required')
        elif a_fcc is None:
            a_fcc = a_bcc * (3/2)**0.5

        self.a_bcc = a_bcc
        self.a_fcc = a_fcc

    @property
    def symbol(self):
        """
        str : The element model symbol to assign to the atoms in the generated
        atomic configurations.
        """
        return self.__symbol

    @symbol.setter
    def symbol(self, value):
        self.__symbol = str(value)

    @property
    def a_bcc(self):
        """float : The bcc lattice constant."""
        return self.__a_bcc
    
    @a_bcc.setter
    def a_bcc(self, value):
        self.__a_bcc = float(value)
    
    @property
    def a_fcc(self):
        """float : The fcc lattice constant."""
        return self.__a_fcc
    
    @a_fcc.setter
    def a_fcc(self, value):
        self.__a_fcc = float(value)
    
    def ucell(self, a_scale, c_scale):
        """
        Generates a bct unit cell for intermediate structures based on the 
        given bcc and fcc lattice constants.

        For the scaling parameters, values of a_scale = c_scale = 0 corresponds
        to the given fcc lattice, and values of a_scale = c_scale = 1
        corresponds to the given bcc lattice.

        Parameters
        ----------
        a_scale : float
            Scaling parameter for the bct structure's a lattice parameter.
        c_scale : float
            Scaling parameter for the bct structure's c lattice parameter.

        Returns
        -------
        ucell : atomman.System
            The corresponding bct unit cell.
        """
        # Set the ideal constants based on a_fcc and a_bcc
        a_0 = self.a_fcc * 2**0.5 / 2
        c_0 = self.a_fcc
        a_1 = c_1 = self.a_bcc
        
        # Compute the bct lattice constants using the scale parameters
        a = a_0 * (1 - a_scale) + a_1 * a_scale
        c = c_0 * (1 - c_scale) + c_1 * c_scale
        
        # Generate box, atoms and system for the bct unit cell
        box = am.Box().tetragonal(a=a, c=c)
        atoms = am.Atoms(pos=[[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]])
        ucell = am.System(atoms=atoms, box=box, symbols=self.symbol, scale=True)
        
        return ucell
    
    def itercellmap(self, num_a=23, num_c=23, min_a_scale=-0.05,
                    max_a_scale=1.05, min_c_scale=-0.05, max_c_scale=1.05):
        """
        Generates bct unit cells that explore a range of lattice constants
        corresponding to the Bain transformation map area.

        Parameters
        ----------
        num_a : int
            The number of unique a_scale values to iterate over.
        num_c : int
            The number of unique c_scale values to iterate over.
        min_a_scale : float
            The minimum a_scale value to include.  Typically, this should be
            slightly less than 0.
        max_a_scale : float
            The maximum a_scale value to include.  Typically, this should be
            slightly greater than 1.
        min_c_scale : float
            The minimum c_scale value to include.  Typically, this should be
            slightly less than 0.
        max_c_scale : float
            The maximum c_scale value to include.  Typically, this should be
            slightly greater than 1.

        Yields
        ------
        a_scale : float
            The a_scale parameter corresponding to the generated unit cell.
        c_scale : float
            The c_scale parameter corresponding to the generated unit cell.
        ucell : atomman.System
            The generated bct unit cell.
        """
        
        # Construct mesh of regular points
        avals, cvals = np.meshgrid(np.linspace(min_a_scale, max_a_scale, num_a),
                                   np.linspace(min_c_scale, max_c_scale, num_c))
        
        # Iterate over grid and yield unit cells
        for a_scale, c_scale in zip(avals.flat, cvals.flat):
            yield a_scale, c_scale, self.ucell(a_scale, c_scale)
            
    def set_results(self, a_scale, c_scale, E_coh):
        """
        Allows for calculated energies to be set in order to generate plots.

        Parameters
        ----------
        a_scale : array-like object
            The list of a_scale values corresponding to each measurement.
        c_scale : array-like object
            The list of c_scale values corresponding to each measurement.
        E_coh : array-like object
            The list of cohesive energy measurements.
        """
        self.a_scale = np.array(a_scale)
        self.c_scale = np.array(c_scale)
        self.E_coh = np.array(E_coh)
        
    def plot_1d_path(self):
        """
        Generates a 1D transformation plot between fcc and bct.  Currently
        limited to the linear path between fcc and bct.
        """

        fig = plt.figure(figsize=(8,5))
        
        matches = (self.a_scale == self.c_scale)
        plt.plot(self.a_scale[matches], self.E_coh[matches])
        plt.xlabel('linear deformation coefficient: 0=fcc, 1=bcc')
        plt.ylabel('Cohesive energy (eV/atom)')
        
        return fig
    
    def plot_2d(self):
        """
        Generates a 2D color map over the full range of evaluated a_scale and
        c_scale values.
        """
        fig = plt.figure(figsize=(10,8))
        
        d = int(len(self.a_scale.flat)**0.5)
        a_scale = self.a_scale.reshape(d,d)
        c_scale = self.c_scale.reshape(d,d)
        E_coh = self.E_coh.reshape(d,d)
        plt.pcolormesh(a_scale, c_scale, E_coh)
        plt.xlabel('xy linear deformation coefficient')
        plt.xlabel('z linear deformation coefficient')
        cbar = plt.colorbar()
        cbar.ax.set_ylabel('cohesive energy (eV/atom)',
                           fontsize='x-large')
        plt.show()
        
        return fig