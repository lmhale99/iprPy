from pathlib import Path
from typing import Optional, Union
import json

import potentials
import atomman as am
import atomman.unitconvert as uc

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

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

    @classmethod
    def run_from_input(cls, input_dict: Union[str, dict, Path]):
        """
        Sets up and performs a quick check based on dict/JSON input settings.
        """
        if isinstance(input_dict, str):
            try:
                # Check if input_dict is a filename
                if Path(input_dict).exists():
                    input_dict = Path(input_dict)
                else:
                    raise OSError('Not a file')
            except OSError as e:
                # Read json string
                input_dict = json.loads(input_dict)
        
        # Load JSON from file path
        if isinstance(input_dict, Path):
            with open(input_dict) as f:
                input_dict = json.load(fp=f)

        # Throw error if not dict
        if not isinstance(input_dict, dict):
            raise TypeError('input_dict neither a dict or JSON content')

        # Extract lammps_command
        lammps_command = input_dict.pop('lammps_command')

        # Extract or build potential
        pot_dict = input_dict.pop('potential')
        if 'file' in pot_dict:
            model = pot_dict.pop('file')
            potential = am.lammps.Potential(model, **pot_dict)
        elif 'pair_style' in pot_dict:
            pair_style = pot_dict.pop('pair_style')
            builder = am.build_lammps_potential(pair_style, **pot_dict)
            potential = builder.potential()
        else:
            raise ValueError('potential must be loaded from a "file" or defined for a "pair_style"')

        # Extract and build crystal unit cells

        ucells = {}
        for crystal_dict in input_dict['crystal']:
            name = crystal_dict['name']
            if 'symbols' in crystal_dict and not isinstance(crystal_dict['symbols'], str):
                crystal_dict['symbols'] = ' '.join(crystal_dict['symbols'])
            calc = load_calculation('relax_static')
            calc.system.load_parameters(crystal_dict)
            d = {}
            calc.system.calc_inputs(d)
            ucell = d['ucell']
            ucells[name] = ucell
        
        self = cls(lammps_command, potential, ucells)

        self.run(**input_dict)

        if 'html_results' in input_dict:
            htmlfilename = input_dict['html_results'].pop('filename', None)
            display = htmlfilename is None
            html = self.html_results(display=display, **input_dict['html_results'])

            if htmlfilename is not None:
                with open(htmlfilename, 'w') as f:
                    f.write(html)

        return self

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
            for crystal_kwargs in kwargs['crystal']:
                if crystal_kwargs['name'] == name:
                    crystal.run(**crystal_kwargs)
                    continue


    def run_isolated_atom(self):

        calc = load_calculation('isolated_atom')
        results = calc.calc(self.lammps_command, self.potential)
        calc.clean_files()

        self.results['isolated_atom'] = results

    def run_diatom_scan(self,
                        symbols: Optional[list] = None,
                        rmin: float = 2.0,
                        rmax: float = 6.0,
                        rsteps: int = 50):

        calc = load_calculation('diatom_scan')

        if symbols is None:
            # Generate all unique symbol pairs
            symbols = []
            potsymbols = self.potential.symbols
            for i in range(len(potsymbols)):
                for j in range(i, len(potsymbols)):
                    symbols.append([potsymbols[i], potsymbols[j]])

        self.results['diatom_scan'] = []
        for symbolpair in symbols:
            results = calc.calc(self.lammps_command, self.potential, symbolpair,
                                rmin=rmin, rmax=rmax, rsteps=rsteps)
            results['symbols'] = symbolpair
            calc.clean_files()
            self.results['diatom_scan'].append(results)

    def run_relax_static_diatom(self,
                                symbols: Optional[list] = None,
                                etol: float = 0.0,
                                ftol: float = 1e-8,
                                maxiter: int = 100000,
                                maxeval: int = 1000000,
                                dmax: float = 0.01,
                                maxcycles: int = 20,
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

    def plot_diatom_scan(self,
                         symbols: Optional[list] = None,
                         filename: Optional[str] = None,
                         xlim=(None, None),
                         ylim=(None, None)):
        if symbols is None:
            symbols = [s['symbols'] for s in self.results['diatom_scan']]

        if not isinstance(symbols, (list, tuple)):
            raise ValueError('symbols must be a list of lists')
            
        for i, syms in enumerate(symbols):
            if not isinstance(syms, (list, tuple)):
                raise ValueError('symbols must be a list of lists')
            if len(syms) == 1 and isinstance(syms[0], str):
                symbols[i] = [syms[0], syms[0]]
            elif len(syms) == 2 and isinstance(syms[0], str) and isinstance(syms[0], str):
                pass
            else:
                raise ValueError('Each symbols list must have one or two symbol values')

        for syms in symbols:
            symbolstr1 = '-'.join(sorted(syms))

            for scan in self.results['diatom_scan']:
                symbolstr2 = '-'.join(sorted(scan['symbols']))
                if symbolstr1 == symbolstr2:
                    plt.plot(scan['r_values'], scan['energy_values'], label=symbolstr1)

        plt.title('Diatom interactions')
        plt.xlabel('r')
        plt.ylabel('Energy')
        plt.legend()
        plt.xlim(*xlim)
        plt.ylim(*ylim)
        
        if filename is None:
            plt.show()
        else:
            plt.savefig(filename)
            plt.close()

    def plot_E_vs_r_scan(self,
                         crystals=None,
                         xaxis='r',
                         filename=None,
                         xlim=(None, None),
                         ylim=(None, None)):
                        
    
        if crystals is None:
            crystals = list(self.crystals.keys())
        
        for crystalname in crystals:
            crystal = self.crystals[crystalname]
            scan = crystal.results['E_vs_r_scan']
        
            if xaxis == 'r':
                plt.plot(scan['r_values'], scan['Ecoh_values'], label=crystalname)
            else:
                plt.plot(scan['a_values'], scan['Ecoh_values'], label=crystalname)
        
        plt.title('Volumetric crystal scan')
        plt.legend()
        
        if xaxis == 'r':
            plt.xlabel('r')
        else:
            plt.xlabel('a')
        plt.ylabel('Potential energy per atom')
        
        plt.xlim(*xlim)
        plt.ylim(*ylim)

        if filename is None:
            plt.show()
        else:
            plt.savefig(filename)
            plt.close()

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
                     plot_diatom_scan: Union[dict, list, None] = None,
                     plot_E_vs_r_scan: Union[dict, list, None] = None,
                     plot_width = '500px',
                     display: bool = False):
        
        # Generate table of basic properties
        html = self.data(length_unit=length_unit,
                         energy_unit=energy_unit).to_html()
        
        # Generate diatom scan plots
        if plot_diatom_scan is not None:
            if isinstance(plot_diatom_scan, dict):
                plot_diatom_scan = [plot_diatom_scan]
            for plot_kwargs in plot_diatom_scan:
                self.plot_diatom_scan(**plot_kwargs)
                html += self.html_img(plot_kwargs['filename'], 'diatom_scan', plot_width)

        # Generate E vs r scan plots
        if plot_E_vs_r_scan is not None:
            if isinstance(plot_E_vs_r_scan, dict):
                plot_E_vs_r_scan = [plot_E_vs_r_scan]
            for plot_kwargs in plot_E_vs_r_scan:
                self.plot_E_vs_r_scan(**plot_kwargs)
                html += self.html_img(plot_kwargs['filename'], 'E_vs_r_scan', plot_width)

        for name, crystal in self.crystals.items():
            html += f'<h4>{name}</h4>'

            # Generate crystal specific properties
            html += crystal.data(length_unit=length_unit,
                                 energy_unit=energy_unit,
                                 pressure_unit=pressure_unit, 
                                 energy_per_area_unit=energy_per_area_unit).to_html()
            
            # Insert any figures for crystal specific properties
            for filename in Path('.').glob(f'{name}--*--band.png'):
                html += self.html_img(filename, 'band_structure', plot_width)
            
        if display:
            import IPython.display
            IPython.display.display(IPython.display.HTML(html))
        else:
            return html
        
    def html_img(self, filename, alt, width):
        return f'<img src="{filename}" alt="{alt}" style="width:{width}">'