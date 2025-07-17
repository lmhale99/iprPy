# coding: utf-8

# Standard Python imports
from typing import Tuple, Optional
from uuid import uuid4

from atomman import Box

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

class MDSolidProperties(Record):
    """
    Class for representing relaxed_crystal records that provide the structure
    information for crystal structures relaxed using a specific interatomic
    potential.
    """

    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'md_solid_properties'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'md-solid-properties'

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('atomman.library.xsd', f'{self.style}.xsd')

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl transformer"""
        return ('atomman.library.xsl', f'{self.style}.xsl')
    
    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'key', valuerequired=True)
        self._add_value('str', 'url', modelpath='URL')
        self._add_value('str', 'method')
        self._add_value('bool', 'untransformed', defaultvalue=True)

        self._add_value('str', 'relaxed_crystal_key',
                        modelpath='relaxed-crystal-key')
        self._add_value('str', 'relaxed_crystal_url',
                        modelpath='relaxed-crystal-URL')
        self._add_value('str', 'relax_dynamic_key',
                        modelpath='relax_dynamic_key')
        self._add_value('str', 'relax_dynamic_url',
                        modelpath='relax-dynamic-URL')
        self._add_value('str', 'free_energy_key',
                        modelpath='free-energy-key')
        self._add_value('str', 'free_energy_url',
                        modelpath='free-energy-URL')
        self._add_value('str', 'elastic_constants_key',
                        modelpath='elastic_constants_key')
        self._add_value('str', 'elastic_constants_url',
                        modelpath='elastic-constants-URL')

        self._add_value('str', 'potential_LAMMPS_key',
                        valuerequired=True,
                        modelpath='potential-LAMMPS.key')
        self._add_value('str', 'potential_LAMMPS_id',
                        valuerequired=True,
                        modelpath='potential-LAMMPS.id')
        self._add_value('str', 'potential_LAMMPS_url',
                        modelpath='potential-LAMMPS.URL')
        self._add_value('str', 'potential_key', valuerequired=True,
                        modelpath='potential-LAMMPS.potential.key')
        self._add_value('str', 'potential_id', valuerequired=True,
                        modelpath='potential-LAMMPS.potential.id')
        self._add_value('str', 'potential_url',
                        modelpath='potential-LAMMPS.potential.URL')
        
        self._add_value('float', 'temperature',
                        defaultvalue=0.0,
                        modelpath='phase-state.temperature',
                        metadatakey='T (K)', unit='K')
        self._add_value('float', 'pressure_xx',
                        defaultvalue=0.0,
                        modelpath='phase-state.pressure-xx',
                        metadatakey='Pxx (GPa)', unit='GPa')
        self._add_value('float', 'pressure_yy',
                        defaultvalue=0.0,
                        modelpath='phase-state.pressure-yy',
                        metadatakey='Pyy (GPa)', unit='GPa')
        self._add_value('float', 'pressure_zz',
                        defaultvalue=0.0,
                        modelpath='phase-state.pressure-zz',
                        metadatakey='Pzz (GPa)', unit='GPa')
        self._add_value('float', 'pressure_xy',
                        defaultvalue=0.0,
                        modelpath='phase-state.pressure-xy',
                        metadatakey='Pxy (GPa)', unit='GPa')
        self._add_value('float', 'pressure_xz',
                        defaultvalue=0.0,
                        modelpath='phase-state.pressure-xz',
                        metadatakey='Pxz (GPa)', unit='GPa')
        self._add_value('float', 'pressure_yz',
                        defaultvalue=0.0,
                        modelpath='phase-state.pressure-yz',
                        metadatakey='Pyz (GPa)', unit='GPa')
        
        self._add_value('str', 'family', valuerequired=True,
                        modelpath='system-info.family')
        self._add_value('str', 'family_url',
                        modelpath='system-info.family-URL')
        self._add_value('strlist', 'symbols', valuerequired=True,
                        modelpath='system-info.symbol')
        self._add_value('str', 'composition', valuerequired=True,
                        modelpath='system-info.composition')

        self._add_value('int', 'natoms', valuerequired=True,
                        modelpath='system-info.cell.natoms')
        self._add_value('int', 'natypes', valuerequired=True,
                        modelpath='system-info.cell.natypes')
        self._add_value('float', 'a', valuerequired=True,
                        modelpath='system-info.cell.a')
        self._add_value('float', 'b', valuerequired=True,
                        modelpath='system-info.cell.b')
        self._add_value('float', 'c', valuerequired=True,
                        modelpath='system-info.cell.c')
        self._add_value('float', 'alpha', valuerequired=True,
                        modelpath='system-info.cell.alpha')
        self._add_value('float', 'beta', valuerequired=True,
                        modelpath='system-info.cell.beta')
        self._add_value('float', 'gamma', valuerequired=True,
                        modelpath='system-info.cell.gamma')
        
        self._add_value('float', 'volume',
                        modelpath='volume-per-atom',
                        metadatakey='V (angstrom^3/atom)', unit='angstrom^3')
        self._add_value('float', 'energy',
                        modelpath='internal-energy',
                        metadatakey='U (eV/atom)', unit='eV')
        self._add_value('float', 'enthalpy',
                        modelpath='enthalpy-energy',
                        metadatakey='H (eV/atom)', unit='eV')
        self._add_value('float', 'gibbs',
                        modelpath='gibbs-energy',
                        metadatakey='G (eV/atom)', unit='eV')
        self._add_value('float', 'helmholtz',
                        modelpath='helmholtz-energy',
                        metadatakey='F (eV/atom)', unit='eV')
        
        self._add_value('cij', 'C', modelpath='elastic-constants')

    def new_name(self, name: Optional[str] = None):
        """
        Assigns a new name to the record.  Setting this will update name, key and
        url values.
        
        Parameters
        ----------
        name : str or None, optional
            The new name for the record.  If not given will generate a new UUID4.
        """
        if name is None:
            name = str(uuid4())

        self.name = name
        self.key = name
        self.url = f'https://potentials.nist.gov/pid/rest/local/potentials/{name}'

    def extract_relaxed_crystal(self, record):
        """
        Extracts all relevant information from a relaxed_crystal record for 0K results.
        
        Parameters
        ----------
        record : atomman.library.relaxed_crystal.RelaxedCrystal
            A 0K relaxed_crystal record.
        """
        self.relaxed_crystal_key = record.key
        self.relaxed_crystal_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.key}'

        self.method = '0K'

        self.potential_LAMMPS_key = record.potential_LAMMPS_key
        self.potential_LAMMPS_id = record.potential_LAMMPS_id
        self.potential_LAMMPS_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.potential_LAMMPS_id}'
        self.potential_key = record.potential_key
        self.potential_id = record.potential_id
        self.potential_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.potential_id}'
        self.temperature = 0.0
        if record.pressure_xx is None:
            self.pressure_xx = 0.0
            self.pressure_yy = 0.0
            self.pressure_zz = 0.0
            self.pressure_xy = 0.0
            self.pressure_xz = 0.0
            self.pressure_yz = 0.0
        else:
            self.pressure_xx = record.pressure_xx
            self.pressure_yy = record.pressure_yy
            self.pressure_zz = record.pressure_zz
            self.pressure_xy = record.pressure_xy
            self.pressure_xz = record.pressure_xz
            self.pressure_yz = record.pressure_yz
        
        self.family = record.family
        self.family_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.family}'
        
        self.symbols = record.symbols
        self.composition = record.composition
        self.natoms = record.ucell.natoms
        self.natypes = len(record.symbols)
               
        self.a = record.a
        self.b = record.b
        self.c = record.c
        self.alpha = record.alpha
        self.beta = record.beta
        self.gamma = record.gamma

        box = Box(a=self.a, b=self.b, c=self.c,
                  alpha=self.alpha, beta=self.beta, gamma=self.gamma)

        V = box.volume / self.natoms
        P = (self.pressure_xx + self.pressure_yy + self.pressure_zz) / 3
        U = record.potential_energy
        H = U + P * V
        
        self.energy = U
        self.enthalpy = H
        self.gibbs = H
        self.helmholtz = U

    def extract_relax_dynamic(self, record, relaxed_crystal_key, sizemult, natoms):
        """
        Extracts all relevant information from a relax_dynamic calculation record.
        
        Parameters
        ----------
        record : iprPy.calculation.relax_dynamic.RelaxDynamic
            A record for the relax_dynamic iprPy calculation method.  Should be of
            branches at_temp or at_temp_50K.
        relaxed_crystal_key : str
            The UUID4 key for the relaxed_crystal record that this calculation originated
            from, i.e. the record for the 0K that started this series.
        sizemult : int
            The system size multiplier used on the 50 K results.  This is used to unscale
            the box dimensions of the higher temperatures.
        natoms : int
            The number of atoms in the original un-multiplied system.  This can be taken
            from the associated relaxed_crystal record.
        """
        self.relaxed_crystal_key = relaxed_crystal_key
        self.relaxed_crystal_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{relaxed_crystal_key}'

        self.relax_dynamic_key = record.key
        self.relax_dynamic_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.key}'

        self.method = record.branch

        self.potential_LAMMPS_key = record.potential.potential_LAMMPS_key
        self.potential_LAMMPS_id = record.potential.potential_LAMMPS_id
        self.potential_LAMMPS_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.potential.potential_LAMMPS_id}'
        self.potential_key = record.potential.potential_key
        self.potential_id = record.potential.potential_id
        self.potential_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.potential.potential_id}'
        self.temperature = record.temperature
        self.pressure_xx = record.pressure_xx
        self.pressure_yy = record.pressure_yy
        self.pressure_zz = record.pressure_zz
        self.pressure_xy = record.pressure_xy
        self.pressure_xz = record.pressure_xz
        self.pressure_yz = record.pressure_yz
        self.family = record.system.family
        self.family_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.system.family}'
        
        self.symbols = record.system.symbols
        self.composition = record.system.composition
        self.natoms = natoms
        self.natypes = len(record.system.symbols)
        
        if record.branch == 'at_temp_50K' or record.temperature < 51:
            box = Box(lx=record.lx_mean, ly=record.ly_mean, lz=record.lz_mean,
                      xy=record.xy_mean, xz=record.xz_mean, yz=record.yz_mean)
        else:
            box = Box(lx=record.lx_mean / sizemult,
                      ly=record.ly_mean / sizemult,
                      lz=record.lz_mean / sizemult,
                      xy=record.xy_mean / sizemult,
                      xz=record.xz_mean / sizemult,
                      yz=record.yz_mean / sizemult)
        
        self.a = box.a
        self.b = box.b
        self.c = box.c
        self.alpha = box.alpha
        self.beta = box.beta
        self.gamma = box.gamma

        V = box.volume / self.natoms
        P = (self.pressure_xx + self.pressure_yy + self.pressure_zz) / 3
        U = record.total_energy
        H = U + P * V

        self.energy = U
        self.enthalpy = H

    def extract_free_energy(self, record):
        """
        Extracts all relevant information from a free_energy calculation record.
        
        Parameters
        ----------
        record : iprPy.calculation.free_energy.FreeEnergy
            A record for the free_energy iprPy calculation method.
        """
        self.free_energy_key = record.key
        self.free_energy_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.key}'
        self.gibbs = record.gibbs
        self.helmholtz = record.helmholtz

    def extract_elastic_constants(self, record):
        """
        Extracts all relevant information from a elastic_constants_dynamic
        calculation record.
        
        Parameters
        ----------
        record : iprPy.calculation.elastic_constants_dynamic.ElasticConstantsDynamic
            A record for the elastic_constants_dynamic iprPy calculation method.
        """
        self.elastic_constants_key = record.key
        self.elastic_constants_url = f'https://potentials.nist.gov/pid/rest/local/potentials/{record.key}'
        self.C = record.C