from pathlib import Path
from typing import Optional, Union

import atomman as am
import atomman.unitconvert as uc

import numpy as np
import pandas as pd

from .. import load_calculation
from ..calculation_subset.PointDefect import PointDefectParams

class QuickCheckCrystal():
    def __init__(self,
                 name: str,
                 lammps_command: str,
                 potential: am.lammps.Potential,
                 ucell: am.System):
        
        self.__name = name
        self.__lammps_command = lammps_command
        self.__potential = potential
        self.__ucell = ucell
        self.__space_group = None
        self.__results = {}

###############################################################################

    @property
    def name(self) -> str:
        """str: Name for the crystal"""
        return self.__name

    @property
    def lammps_command(self) -> str:
        """str: The LAMMPS executable to use"""
        return self.__lammps_command
    
    @property
    def potential(self) -> am.lammps.Potential:
        """atomman.lammps.Potential: The LAMMPS potential to use"""
        return self.__potential

    @property
    def ucell(self) -> am.System:
        """atomman.System: The base unit cell to test and relax"""
        return self.__ucell

    @property
    def space_group(self) -> Optional[int]:
        return self.__space_group

    @property
    def results(self) -> dict:
        """dict: Collection of calculation results"""
        return self.__results

###############################################################################

    def run(self,
            E_vs_r_scan: Union[dict, bool] = True,
            relax_static: Union[dict, bool] = True,
            crystal_space_group: Union[dict, bool] = True,
            elastic_constants_static: Union[dict, bool] = False,
            phonon: Union[dict, bool] = False,
            point_defect_static: Union[dict, bool] = False,
            surface_energy_static: Union[dict, bool] = False):
        """
        Run the calculations in the workflow.

        All parameters are named for the associated calculation style and
        can take dict or bool values.  A value of False will skip the
        associated calculation style.  A dict value will pass the contents on
        to the corresponding run_"calc_style" method as keyword arguments.
        A value of True will run the calculation with the default settings and
        is equivalent to passing an empty dict. 
        """

        if E_vs_r_scan is not False:
            if E_vs_r_scan is True:
                E_vs_r_scan = {}
            self.run_E_vs_r_scan(**E_vs_r_scan)

        if relax_static is not False:
            if relax_static is True:
                relax_static = {}
            if E_vs_r_scan is False and 'ucells' not in relax_static:
                relax_static['ucells'] = self.ucell
            self.run_relax_static(**relax_static)

        if crystal_space_group is not False:
            if crystal_space_group is True:
                crystal_space_group = {}
            self.run_crystal_space_group(**crystal_space_group)

        if elastic_constants_static is not False:
            if elastic_constants_static is True:
                elastic_constants_static = {}
            self.run_elastic_constants_static(**elastic_constants_static)

        if phonon is not False:
            if phonon is True:
                phonon = {}
            self.run_phonon(**phonon)

        if point_defect_static is not False:
            if point_defect_static is True:
                point_defect_static = {}
            self.run_point_defect_static(**point_defect_static)

        if surface_energy_static is not False:
            if surface_energy_static is True:
                surface_energy_static = {}
            self.run_surface_energy_static(**surface_energy_static)


    def run_E_vs_r_scan(self,
                        rmin: float = 2.0,
                        rmax: float = 6.0,
                        rsteps: int = 50,
                        sizemult: int = 2):
        """
        Run the E_vs_r_scan calculation for the crystal.

        Parameters
        ----------
        rmin : float
            The minimum r spacing to evaluate.
        rmax : float
            The maximum r spacing to evaluate.
        rsteps : int
            The number of r spacings to evaluate.
        sizemult : int
            A super cell size multiplier: sizemult x sizemult x sizemult.
        """
        if self.ucell is None:
            raise ValueError('ucell not set!')

        calc = load_calculation('E_vs_r_scan')
        system = self.ucell.supersize(sizemult, sizemult, sizemult)
        results = calc.calc(self.lammps_command, system, self.potential,
                            ucell=self.ucell, rmin=rmin, rmax=rmax,
                            rsteps=rsteps)
        calc.clean_files()

        self.results['E_vs_r_scan'] = results

    def run_relax_static(self,
                         ucells: Union[am.System, list, None] = None,
                         etol: float = 0.0,
                         ftol: float = 1e-8,
                         maxiter: int = 100000,
                         maxeval: int = 1000000,
                         dmax: float = 0.01,
                         maxcycles: int = 100,
                         ctol: float = 1e-10,
                         raise_at_maxcycles: bool = False):
        """
        Run the relax_static calculation for the crystal based on .

        Parameters
        ----------
        etol : float
            The energy tolerance for the minimization.
        ftol : float
            The force tolerance for the minimization.
        maxiter : int
            The number of iterations per minimization.
        maxeval : int
            The number of evaluations per minimization.
        dmax : float
            The farthest an atom is allowed to move during an iteration.
        maxcycles : int
            The maximum number of minimization runs to perform.
        ctol : float
            The tolerance for comparing minimization runs.
        raise_at_maxcycles : bool
            Indicates if an error should be raised if maxcycles is reached.
        """
        
        if ucells is None:
            ucells = self.results['E_vs_r_scan']['min_cell']
        elif isinstance(ucells, am.System):
            ucells = [ucells]
        elif hasattr(ucells, '__iter__'):
            for ucell in ucells:
                if not isinstance(ucell, am.System):
                    raise TypeError('ucells must be None or one or more atomman.Systems')
        else:
            raise TypeError('ucells must be None or one or more atomman.Systems')
        
        self.results['relax_static'] = []
        calc = load_calculation('relax_static')
        for ucell in ucells:
            results = calc.calc(self.lammps_command, ucell, self.potential,
                                etol=etol, ftol=ftol, maxiter=maxiter,
                                maxeval=maxeval, dmax=dmax, maxcycles=maxcycles,
                                ctol=ctol, raise_at_maxcycles=raise_at_maxcycles)
            
            results['relaxed_ucell'] = am.load('atom_dump', results['dumpfile_final'],
                                                symbols=results['symbols_final'])
            calc.clean_files()

            self.results['relax_static'].append(results)

    def run_crystal_space_group(self,
                                symprec: float = 1e-5,
                                to_primitive: bool = False,
                                no_idealize: bool = False):
        """
        Run the crystal_space_group calculation
        
        Parameters
        ----------
        symprec : float
            The symmetry precision tolerance.
        to_primitive : bool
            Indicates if the resulting cell should be primitive.
        no_idealize : bool
            Indicates if the resulting cell is to not be idealized.
        """
        calc = load_calculation('crystal_space_group')

        self.results['crystal_space_group'] = []
        
        # Run on the base ucell
        base = None
        if self.ucell is not None:
            base = calc.calc(self.ucell, symprec, to_primitive, no_idealize)
            self.__space_group = base['number']
        
        # Run on the relaxed cells
        for static in self.results['relax_static']:
            ucell = static['relaxed_ucell']
            results = calc.calc(ucell, symprec, to_primitive, no_idealize)
            calc.clean_files()

            if base is not None:
                results['transformed'] = base['hall_number'] != results['hall_number']
            self.results['crystal_space_group'].append(results)

    def run_elastic_constants_static(self,
                                     strainrange: float = 1e-6,
                                     etol: float = 0.0,
                                     ftol: float = 1e-8,
                                     maxiter: int = 100000,
                                     maxeval: int = 1000000,
                                     dmax: float = 0.01):
        
        calc = load_calculation('elastic_constants_static')

        self.results['elastic_constants_static'] = []
        for static in self.results['relax_static']:
            ucell = static['relaxed_ucell']
            results = calc.calc(self.lammps_command, ucell, self.potential,
                                strainrange=strainrange, etol=etol, ftol=ftol,
                                maxiter=maxiter, maxeval=maxeval, dmax=dmax)
            calc.clean_files()
            self.results['elastic_constants_static'].append(results)

    def run_phonon(self,
                   distance: float = 0.01,
                   symprec: float = 1e-5,
                   strainrange: float = 1e-6,
                   numstrains: int = 1):
        calc = load_calculation('phonon')

        self.results['phonon'] = []
        for i, static in enumerate(self.results['relax_static']):
            ucell = static['relaxed_ucell']
            results = calc.calc(self.lammps_command, ucell, self.potential,
                                distance=distance, symprec=symprec,
                                numstrains=numstrains, strainrange=strainrange)
            Path('band.png').rename(f'{self.name}--{i}--band.png')
            calc.clean_files()
            self.results['phonon'].append(results)

    def run_point_defect_static(self,
                                point_defects: dict,
                                sizemult: int = 5,
                                etol: float = 0.0,
                                ftol: float = 1e-8,
                                maxiter: int = 100000,
                                maxeval: int = 1000000,
                                dmax: float = 0.01):
        
        calc = load_calculation('point_defect_static')
        self.results['point_defect_static'] = []

        for cspg in self.results['crystal_space_group']:
            ucell = cspg['ucell']
            r = {}

            for name, point_defect in point_defects.items():
                
                # Extract point_defect kwargs from a record
                if isinstance(point_defect, am.library.record.PointDefect.PointDefect):
                    point_kwargs = []
                    for params in point_defect.parameters:
                        point_kwargs.append(PointDefectParams(**params).calc_inputs(ucell))
                else:
                    point_kwargs = point_defect
                  
                cutoff = 1.05 * ucell.box.a
                system = ucell.supersize(sizemult, sizemult, sizemult)

                # Run the calculation
                results = calc.calc(self.lammps_command, system, self.potential,
                                    point_kwargs, cutoff, etol=etol, ftol=ftol,
                                    maxiter=maxiter, maxeval=maxeval, dmax=dmax)
                r[name] = results
                calc.clean_files()
            self.results['point_defect_static'].append(r)

    def run_surface_energy_static(self,
                                  surfaces: dict,
                                  minwidth: float = 30,
                                  etol: float = 0.0,
                                  ftol: float = 1e-8,
                                  maxiter: int = 100000,
                                  maxeval: int = 1000000,
                                  dmax: float = 0.01):
        
        calc = load_calculation('surface_energy_static')
        self.results['surface_energy_static'] = []

        for static in self.results['relax_static']:
            ucell = static['relaxed_ucell']
            r = {}

            for name, surface in surfaces.items():
                
                # Extract surface definition parameters
                if isinstance(surface, am.library.record.FreeSurface.FreeSurface):
                    hkl = np.array(surface.parameters['hkl'].strip().split(), dtype=float)
                    shiftindex = int(surface.parameters.get('shiftindex', 0))
                else:
                    hkl = surface['hkl']
                    shiftindex = surface.get('shiftindex', 0)
                
                
                # Run the calculation
                results = calc.calc(self.lammps_command, ucell, self.potential,
                                    hkl=hkl, minwidth=minwidth, even=True,
                                    shiftindex=shiftindex, etol=etol, ftol=ftol,
                                    maxiter=maxiter, maxeval=maxeval, dmax=dmax)
                r[name] = results
                calc.clean_files()
            self.results['surface_energy_static'].append(r)
        
        
    
###############################################################################

    def data(self,
             length_unit: str = 'angstrom',
             energy_unit: str = 'eV',
             pressure_unit: str = 'GPa',
             energy_per_area_unit: str = 'mJ/m^2',
             crystal_system: Optional[str] = None):
        
        data = [
            self.data_crystal_space_group(),
            self.data_relax_static(length_unit=length_unit,
                                   energy_unit=energy_unit,
                                   crystal_system=crystal_system),
            self.data_elastic_constants_static(pressure_unit=pressure_unit,
                                               crystal_system=crystal_system),
            self.data_surface_energy_static(energy_per_area_unit=energy_per_area_unit),
            self.data_point_defect_static(energy_unit=energy_unit),
        ]

        return pd.concat(data, axis=0)
    

    def data_crystal_space_group(self):
        
        # Build the data
        data = []
        for i in range(len(self.results['relax_static'])):
            spg = self.results['crystal_space_group'][i]
            d = {}
            d['transformed'] = spg['transformed']
            data.append(d)
        data = pd.DataFrame(data)

        return data.T


    def data_relax_static(self,
                          length_unit: str = 'angstrom',
                          energy_unit: str = 'eV',
                          crystal_system: Optional[str] = None):
        
        # Manage crystal_system input
        if crystal_system is None:
            if self.space_group is None:
                crystal_system = 'triclinic'
            else:
                crystal_system = self.crystal_system(self.space_group)

        # Build the data
        data = []
        for i in range(len(self.results['relax_static'])):
            relax = self.results['relax_static'][i]
            ucell = relax['relaxed_ucell']
            d = {}
            d['E_pot'] = uc.get_in_units(relax['E_pot'], energy_unit)
            d['a'] = uc.get_in_units(ucell.box.a, length_unit)
            d['b'] = uc.get_in_units(ucell.box.b, length_unit)
            d['c'] = uc.get_in_units(ucell.box.c, length_unit)
            d['alpha'] = ucell.box.alpha
            d['beta'] = ucell.box.beta
            d['gamma'] = ucell.box.gamma
            data.append(d)
        data = pd.DataFrame(data)

        # Delimit by crystal system
        if crystal_system == 'cubic':
            data = data[['E_pot', 'a']]
        elif crystal_system == 'hexagonal':
            data = data[['E_pot', 'a', 'c']]
        elif crystal_system == 'trigonal':
            data = data[['E_pot', 'a', 'alpha']]
        elif crystal_system == 'tetragonal':
            data = data[['E_pot', 'a', 'c']]
        elif crystal_system == 'orthorhombic':
            data = data[['E_pot', 'a', 'b', 'c']]
        elif crystal_system == 'monoclinic':
            data = data[['E_pot', 'a', 'b', 'c', 'beta']]

        return data.T


    def data_elastic_constants_static(self,
                                      pressure_unit: str = 'GPa',
                                      crystal_system: Optional[str] = None):
        
        if 'elastic_constants_static' not in self.results:
            return pd.DataFrame()


        # Manage crystal_system input
        if crystal_system is None:
            if self.space_group is None:
                crystal_system = 'triclinic'
            else:
                crystal_system = self.crystal_system(self.space_group)
                if crystal_system == 'trigonal':
                    crystal_system == 'rhombohedral'

        data = []
        for i in range(len(self.results['relax_static'])):
            cij = self.results['elastic_constants_static'][i]['C'].normalized_as(crystal_system).Cij
            d = {}
            d['C11'] = uc.get_in_units(cij[0,0], pressure_unit)
            d['C12'] = uc.get_in_units(cij[0,1], pressure_unit)
            d['C13'] = uc.get_in_units(cij[0,2], pressure_unit)
            d['C14'] = uc.get_in_units(cij[0,3], pressure_unit)
            d['C15'] = uc.get_in_units(cij[0,4], pressure_unit)
            d['C16'] = uc.get_in_units(cij[0,5], pressure_unit)
            d['C22'] = uc.get_in_units(cij[1,1], pressure_unit)
            d['C23'] = uc.get_in_units(cij[1,2], pressure_unit)
            d['C24'] = uc.get_in_units(cij[1,3], pressure_unit)
            d['C25'] = uc.get_in_units(cij[1,4], pressure_unit)
            d['C26'] = uc.get_in_units(cij[1,5], pressure_unit)
            d['C33'] = uc.get_in_units(cij[2,2], pressure_unit)
            d['C34'] = uc.get_in_units(cij[2,3], pressure_unit)
            d['C35'] = uc.get_in_units(cij[2,4], pressure_unit)
            d['C36'] = uc.get_in_units(cij[2,5], pressure_unit)
            d['C44'] = uc.get_in_units(cij[3,3], pressure_unit)
            d['C45'] = uc.get_in_units(cij[3,4], pressure_unit)
            d['C46'] = uc.get_in_units(cij[3,5], pressure_unit)
            d['C55'] = uc.get_in_units(cij[4,4], pressure_unit)
            d['C56'] = uc.get_in_units(cij[4,5], pressure_unit)
            d['C66'] = uc.get_in_units(cij[5,5], pressure_unit)
            data.append(d)
        data = pd.DataFrame(data)

        # Delimit by crystal system
        if crystal_system == 'cubic':
            data = data[['C11', 'C12', 'C44']]
        elif crystal_system == 'hexagonal':
            data = data[['C11', 'C12', 'C13', 'C33', 'C44', 'C66']]
        elif crystal_system == 'rhombohedral':
            data = data[['C11', 'C12', 'C13', 'C14', 'C15', 'C33', 'C44', 'C66']]
        elif crystal_system == 'tetragonal':
            data = data[['C11', 'C33', 'C12', 'C13', 'C16', 'C44', 'C66']]
        elif crystal_system == 'orthorhombic':
            data = data[['C11', 'C22', 'C33', 'C12', 'C13', 'C23', 'C44', 'C55', 'C66']]
        elif crystal_system == 'monoclinic':
            data = data[['C11', 'C12', 'C13', 'C15', 'C22', 'C23', 'C25', 'C33',
                         'C35', 'C44', 'C46', 'C55', 'C66']]

        return data.T


    def data_point_defect_static(self,
                                 energy_unit: str = 'eV'):
        
        if 'point_defect_static' not in self.results:
            return pd.DataFrame()
        
        data = []
        for i in range(len(self.results['relax_static'])):
            point_defects = self.results['point_defect_static'][i]
            d = {}
            for name, point_defect in point_defects.items():
                d[f'E_ptd_{name}'] = uc.get_in_units(point_defect['E_ptd_f'],
                                                      energy_unit)
            data.append(d)
        
        data = pd.DataFrame(data)
        return data.T

    def data_surface_energy_static(self,
                                   energy_per_area_unit: str = 'mJ/m^2'):
        
        if 'surface_energy_static' not in self.results:
            return pd.DataFrame()
        
        data = []
        for i in range(len(self.results['relax_static'])):
            surfaces = self.results['surface_energy_static'][i]
            d = {}
            for name, surface in surfaces.items():
                d[f'E_surf_{name}'] = uc.get_in_units(surface['E_surf_f'],
                                                      energy_per_area_unit)
            data.append(d)
        
        data = pd.DataFrame(data)
        return data.T

    def crystal_system(self, space_group_number):
        if space_group_number <= 2:
            return 'triclinic'
        elif space_group_number <= 15:
            return 'monoclinic'
        elif space_group_number <= 74:
            return 'orthorhombic'
        elif space_group_number <= 142:
            return 'tetragonal'
        elif space_group_number <= 167:
            return 'trigonal'
        elif space_group_number <= 194:
            return 'hexagonal'
        else:
            return 'cubic'
        

