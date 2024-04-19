from pathlib import Path
from typing import Optional, Union

import atomman as am
import atomman.unitconvert as uc

import numpy as np
import pandas as pd

from .. import load_calculation
from .QuickCheckCrystal import QuickCheckCrystal

class QuickCheck():

    def __init__(self,
                 lammps_command: str,
                 potential: am.lammps.Potential,
                 ucells: dict):

        self.__lammps_command = lammps_command
        self.__potential = potential
        
        self.__crystals = {}
        for name, ucell in ucells.items():
            self.crystals[name] = QuickCheckCrystal(name, lammps_command,
                                                    potential, ucell)
        self.__results = {}

    @property
    def lammps_command(self) -> str:
        """str: The LAMMPS executable to use"""
        return self.__lammps_command
    
    @property
    def potential(self) -> am.lammps.Potential:
        """atomman.lammps.Potential: The LAMMPS potential to use"""
        return self.__potential

    @property
    def crystals(self) -> str:
        """list: QuickCheckCrystal objects"""
        return self.__crystals

    @property
    def results(self) -> dict:
        """dict: Collection of calculation results"""
        return self.__results

###############################################################################

    def run(self,
            isolated_atom: Union[dict, bool] = True,
            diatom_scan: Union[dict, bool] = True,
            relax_static_diatom: Union[dict, bool] = False,
            **kwargs):
        
        if isolated_atom is not False:
            if isolated_atom is True:
                isolated_atom = {}
            self.run_isolated_atom(**isolated_atom)

        if diatom_scan is not False:
            if diatom_scan is True:
                diatom_scan = {}
            self.run_diatom_scan(**diatom_scan)

        if relax_static_diatom is not False:
            if relax_static_diatom is True:
                relax_static_diatom = {}
            self.run_relax_static_diatom(**relax_static_diatom)

        for name, crystal in self.crystals.items():
            crystal_kwargs = kwargs.get(name, {})
            crystal.run(**crystal_kwargs)


    def run_isolated_atom(self):

        calc = load_calculation('isolated_atom')
        results = calc.calc(self.lammps_command, self.potential)
        calc.clean_files()

        self.results['isolated_atom'] = results

    def run_diatom_scan(self,
                        rmin: float = 2.0,
                        rmax: float = 6.0,
                        rsteps: int = 50):

        calc = load_calculation('diatom_scan')

        self.results['diatom_scan'] = []
        potsymbols = self.potential.symbols
        for i in range(len(potsymbols)):
            for j in range(i, len(potsymbols)):
                symbols = [potsymbols[i], potsymbols[j]]
                results = calc.calc(self.lammps_command, self.potential, symbols,
                                    rmin=rmin, rmax=rmax, rsteps=rsteps)
                results['symbols'] = symbols
                calc.clean_files()
                self.results['diatom_scan'].append(results)

    def run_relax_static_diatom(self,
                                symbols: Optional[list] = None,
                                etol: float = 0.0,
                                ftol: float = 1e-8,
                                maxiter: int = 100000,
                                maxeval: int = 1000000,
                                dmax: float = 0.01,
                                maxcycles: int = 100,
                                ctol: float = 1e-10,
                                raise_at_maxcycles: bool = False):
        
        self.results['relax_static_diatom'] = []
        calc = load_calculation('relax_static')

        for diatom_scan in self.results['diatom_scan']:
            
            # Skip unmatched symbols (if symbols are given)
            symbolset = diatom_scan['symbols']
            if symbols is not None:
                match = False
                for syms in symbols:
                    if syms[0] == symbolset[0] and syms[1] == symbolset[1]:
                        match = True
                        break
                    if syms[0] == symbolset[1] and syms[1] == symbolset[0]:
                        match = True
                        break
                if match is False:
                    continue

            # Find the minimum energy from the diatom scan run
            r = diatom_scan['r_values']
            energy = diatom_scan['energy_values']
            r_min = r[energy == energy.min()][0]
        
            # Build a diatom configuration
            box = am.Box.cubic(a=1000)
            atoms = am.Atoms(atype=[1,2], pos = [[500, 500, 500], [500+r_min, 500, 500]])
            diatom = am.System(box=box, atoms=atoms, scale=False, symbols=symbolset)
        
            results = calc.calc(self.lammps_command, diatom, self.potential,
                                etol=etol, ftol=ftol, maxiter=maxiter,
                                maxeval=maxeval, dmax=dmax, maxcycles=maxcycles,
                                ctol=ctol, raise_at_maxcycles=raise_at_maxcycles)
            results['relaxed_diatom'] = am.load('atom_dump', results['dumpfile_final'],
                                                symbols=results['symbols_final'])
            calc.clean_files()

            self.results['relax_static_diatom'].append(results)

###############################################################################

    def data(self,
             length_unit: str = 'angstrom',
             energy_unit: str = 'eV',):
        data = [
            self.data_isolated_atom(energy_unit=energy_unit),
            self.data_relax_static_diatom(length_unit=length_unit,
                                          energy_unit=energy_unit)
        ]

        return pd.concat(data, axis=0)
    
    def data_isolated_atom(self,
                           energy_unit: str = 'eV'):
        data = {}
        for symbol, energy in self.results['isolated_atom']['energy'].items():
            data[symbol] = {}
            data[symbol]['E_isolated'] = uc.get_in_units(energy, energy_unit)

        data = pd.DataFrame(data)
        return data

    def data_relax_static_diatom(self,
                                 length_unit: str = 'angstrom',
                                 energy_unit: str = 'eV'):
        data = {}
        for i in range(len(self.results['relax_static_diatom'])):
            relax = self.results['relax_static_diatom'][i]
            diatom = relax['relaxed_diatom']
            if diatom.symbols[0] == diatom.symbols[1]:
                symbol = diatom.symbols[0]
            else:
                symbol = '-'.join(diatom.symbols)
            
            r0 = np.linalg.norm(diatom.atoms.pos[0] - diatom.atoms.pos[1])

            data[symbol] = d = {}
            d['E_diatom'] = uc.get_in_units(relax['E_pot'], energy_unit)
            d['r_diatom'] = uc.get_in_units(r0, length_unit)
        
        data = pd.DataFrame(data)
        return data
    
###############################################################################

    def print_results(self,
                      length_unit: str = 'angstrom',
                      energy_unit: str = 'eV',
                      pressure_unit: str = 'GPa',
                      energy_per_area_unit: str = 'mJ/m^2',):
        
        print(self.data(length_unit=length_unit, energy_unit=energy_unit))

        for name, crystal in self.crystals.items():
            print(name)
            print(crystal.data(length_unit=length_unit,
                               energy_unit=energy_unit,
                               pressure_unit=pressure_unit, 
                               energy_per_area_unit=energy_per_area_unit))
            print()

    def html_results(self,
                     length_unit: str = 'angstrom',
                     energy_unit: str = 'eV',
                     pressure_unit: str = 'GPa',
                     energy_per_area_unit: str = 'mJ/m^2',
                     display: bool = False):
        html = self.data(length_unit=length_unit,
                         energy_unit=energy_unit).to_html()
        
        for name, crystal in self.crystals.items():
            html += f'<h4>{name}</h4>'
            html += crystal.data(length_unit=length_unit,
                                 energy_unit=energy_unit,
                                 pressure_unit=pressure_unit, 
                                 energy_per_area_unit=energy_per_area_unit).to_html()
            
        if display:
            import IPython.display
            IPython.display.display(IPython.display.HTML(html))
        else:
            return html