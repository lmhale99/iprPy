# coding: utf-8
# Standard library imports
from copy import deepcopy

import numpy as np

import matplotlib.pyplot as plt

import atomman as am

class Bain():
    
    def __init__(self, a_bcc, a_fcc, symbol):
        
        # Define prototype bcc ucell
        self.__proto = am.System(atoms=am.Atoms(pos=[[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]), symbols=symbol)
        
        self.a_bcc = a_bcc
        self.a_fcc = a_fcc

    @property
    def proto(self):
        return self.__proto
        
    @property
    def a_bcc(self):
        return self.__a_bcc
    
    @a_bcc.setter
    def a_bcc(self, value):
        self.__a_bcc = float(value)
    
    @property
    def a_fcc(self):
        return self.__a_fcc
    
    @a_fcc.setter
    def a_fcc(self, value):
        self.__a_fcc = float(value)
    
    def ucell(self, a_scale, c_scale):
        
        # Get the ideal deformation points
        a_0 = self.a_fcc * 2**0.5 / 2
        c_0 = self.a_fcc
        a_1 = c_1 = self.a_bcc
        
        a = a_0 * (1 - a_scale) + a_1 * a_scale
        c = c_0 * (1 - c_scale) + c_1 * c_scale
        
        ucell = deepcopy(self.proto)
        ucell.box_set(a=a, b=a, c=c, scale=True)
        
        return ucell
    
    def itercellmap(self, num_a=23, num_c=23, min_a=-0.05, max_a=1.05, min_c=-0.05, max_c=1.05):
        
        
        # Construct mesh of regular points
        avals, cvals = np.meshgrid(np.linspace(min_a, max_a, num_a),
                                   np.linspace(min_c, max_c, num_c))
        
        for a, c in zip(avals.flat, cvals.flat):
            yield a, c, self.ucell(a, c)
            
    def set_results(self, a_scale, c_scale, E_coh):
        
        self.a_scale = np.array(a_scale)
        self.c_scale = np.array(c_scale)
        self.E_coh = np.array(E_coh)
        
    def plot_1d_path(self):
        
        fig = plt.figure(figsize=(8,5))
        
        matches = (self.a_scale == self.c_scale)
        plt.plot(self.a_scale[matches], self.E_coh[matches])
        plt.xlabel('linear deformation coefficient: 0=fcc, 1=bcc')
        plt.ylabel('Cohesive energy (eV/atom)')
        
        return fig
    
    def plot_2d(self):
        
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