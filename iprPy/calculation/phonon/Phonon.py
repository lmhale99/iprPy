# coding: utf-8
# Standard Python libraries

from datamodelbase import query

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .calc_phonon import phonon_quasiharmonic
from ...calculation_subset import *
from ...input import value, boolean
from ...tools import aslist, dict_insert

# Global class properties
modelroot = 'calculation-phonon'

class Phonon(Calculation):
    """Class for managing phonon and quasiharmonic calculations using phonopy"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """Initializes a Calculation object for a given style."""
        
        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)
        self.__system = AtommanSystemLoad(self)
        self.__system_mods = AtommanSystemManipulate(self)

        # Initialize unique calculation attributes
        self.strainrange = 0.01
        self.displacementdistance = uc.set_in_units(0.01, 'angstrom')
        self.symmetryprecision = 1e-5         
        self.numstrains = 5 
        self.__bandstructure = None
        self.__dos = None
        self.__thermal = None
        self.__volumescan = None
        self.__E0 = None
        self.__B0 = None
        self.__B0prime = None
        self.__V0 = None
        self.__phonons = None
        self.__qha = None
        
        # Define calc shortcut
        self.calc = phonon_quasiharmonic

        # Call parent constructor
        super().__init__(model=model, name=name, params=params, **kwargs)

############################## Class attributes ################################

    @property
    def commands(self):
        """LammpsCommands subset"""
        return self.__commands

    @property
    def potential(self):
        """LammpsPotential subset"""
        return self.__potential

    @property
    def units(self):
        """Units subset"""
        return self.__units

    @property
    def system(self):
        """AtommanSystemLoad subset"""
        return self.__system

    @property
    def system_mods(self):
        """AtommanSystemManipulate subset"""
        return self.__system_mods

    @property
    def strainrange(self):
        """float: Strain step size to use for quasiharmonic method"""
        return self.__strainrange

    @strainrange.setter
    def strainrange(self, value):
        self.__strainrange = float(value)

    @property
    def numstrains(self):
        """int: Number of strain states to use for quasiharmonic method"""
        return self.__numstrains

    @numstrains.setter
    def numstrains(self, value):
        self.__numstrains = int(value)

    @property
    def symmetryprecision(self):
        """float: Precision tolerance to use to identify symmetry elements"""
        return self.__symmetryprecision

    @symmetryprecision.setter
    def symmetryprecision(self, value):
        self.__symmetryprecision = float(value)

    @property
    def displacementdistance(self):
        """float: Random max atomic displacement to use for phonon calculations"""
        return self.__displacementdistance

    @displacementdistance.setter
    def displacementdistance(self, value):
        self.__displacementdistance = float(value)
        
    @property
    def bandstructure(self):
        """dict: band structure information"""
        if self.__bandstructure is None:
            raise ValueError('No results yet!')
        return self.__bandstructure

    @property
    def dos(self):
        """dict: density of states information"""
        if self.__dos is None:
            raise ValueError('No results yet!')
        return self.__dos

    @property
    def thermal(self):
        """dict: estimated properties vs temperature"""
        if self.__thermal is None:
            raise ValueError('No results yet!')
        return self.__thermal

    @property
    def phonons(self):
        """list: phonopy.Phonopy objects for each strain"""
        if self.__phonons is None:
            raise ValueError('phonon objects not set...')
        return self.__phonons

    @property
    def qha(self):
        """phonopy.PhonopyQHA: quasiharmonic approximation object"""
        if self.__qha is None:
            raise ValueError('phonon qha object not set...')
        return self.__qha

    @property
    def volumescan(self):
        """dict: volume-energy scan used for quasiharmonic"""
        if self.__volumescan is None:
            raise ValueError('No quasiharmonic results!')
        return self.__volumescan

    @property
    def E0(self):
        """float: energy estimated for the equilibrium structure from the volume scan"""
        if self.__E0 is None:
            raise ValueError('No quasiharmonic results!')
        return self.__E0
    
    @property
    def B0(self):
        """float: bulk modulus estimated at the equilibrium structure from the volume scan"""
        if self.__B0 is None:
            raise ValueError('No quasiharmonic results!')
        return self.__B0
    
    @property
    def B0prime(self):
        """float: bulk prime modulus estimated at the equilibrium structure from the volume scan"""
        if self.__B0prime is None:
            raise ValueError('No quasiharmonic results!')
        return self.__B0prime

    @property
    def V0(self):
        """float: volume estimated for the equilibrium structure from the volume scan"""
        if self.__V0 is None:
            raise ValueError('No quasiharmonic results!')
        return self.__V0

    def set_values(self, name=None, **kwargs):
        """Used to set initial common values for the calculation."""
        
        # Set universal content
        super().set_values(name=None, **kwargs)

        # Set subset values
        self.units.set_values(**kwargs)
        self.potential.set_values(**kwargs)
        self.commands.set_values(**kwargs)
        self.system.set_values(**kwargs)
        self.system_mods.set_values(**kwargs)

        # Set calculation-specific values
        if 'strainrange' in kwargs:
            self.strainrange = kwargs['strainrange']
        if 'numstrains' in kwargs:
            self.numstrains = kwargs['numstrains']
        if 'symmetryprecision' in kwargs:
            self.symmetryprecision = kwargs['symmetryprecision']
        if 'displacementdistance' in kwargs:
            self.displacementdistance = kwargs['displacementdistance']

####################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Load universal content
        input_dict = super().load_parameters(params, key=key)
        
        # Load input/output units
        self.units.load_parameters(input_dict)
        
        # Change default values for subset terms
        input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
        input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')

        # Load calculation-specific strings

        # Load calculation-specific booleans
        
        # Load calculation-specific integers
        self.numstrains = int(input_dict.get('numstrains', 5))

        # Load calculation-specific unitless floats
        self.symmetryprecision = float(input_dict.get('symmetryprecision', 1e-5))
        self.strainrange = float(input_dict.get('strainrange', 1e-6))

        # Load calculation-specific floats with units
        self.displacementdistance = value(input_dict, 'displacementdistance',
                                          default_unit=self.units.length_unit,
                                          default_term='0.01 angstrom')

        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)

        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)

        # Load initial system
        self.system.load_parameters(input_dict)

        # Manipulate system
        self.system_mods.load_parameters(input_dict)

    def master_prepare_inputs(self, branch='main', **kwargs):
        """
        Utility method that build input parameters for prepare according to the
        workflows used by the NIST Interatomic Potentials Repository.  In other
        words, transforms inputs from master_prepare into inputs for prepare.

        Parameters
        ----------
        branch : str, optional
            Indicates the workflow branch to prepare calculations for.  Default
            value is 'main'.
        **kwargs : any
            Any parameter modifications to make to the standard workflow
            prepare scripts.

        Returns
        -------
        params : dict
            The full set of prepare parameters based on the workflow branch
        """
        # Initialize params and copy over branch
        params = {}
        params['branch'] = branch

        # main branch
        if branch == 'main':
            
            # Check for required kwargs
            assert 'lammps_command' in kwargs

            # Set default workflow settings
            params['buildcombos'] = 'atomicparent load_file parent'
            params['parent_record'] = 'relaxed_crystal'
            params['parent_method'] = 'dynamic'
            params['parent_standing'] = 'good'
            params['sizemults'] = '3 3 3'

            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'parent_{key}'] = kwargs[key]
                
                # Copy/overwrite other terms
                else:
                    params[key] = kwargs[key]

        else:
            raise ValueError(f'Unknown branch {branch}')

        return params

    @property
    def template(self):
        """
        str: The template to use for generating calc.in files.
        """
        # Build universal content
        template = super().template

        # Build subset content
        template += self.commands.template()
        template += self.potential.template()
        template += self.system.template()
        template += self.system_mods.template()
        template += self.units.template()

        # Build calculation-specific content
        header = 'Run parameters'
        keys = ['displacementdistance', 'symmetryprecision', 'numstrains',
                'strainrange']
        template += self._template_builder(header, keys)
        
        return template

    @property
    def singularkeys(self):
        """list: Calculation keys that can have single values during prepare."""
        
        keys = (
            # Universal keys
            super().singularkeys

            # Subset keys
            + self.commands.keyset
            + self.units.keyset

            # Calculation-specific keys
        )
        return keys

    @property
    def multikeys(self):
        """list: Calculation key sets that can have multiple values during prepare."""

        # Fetch universal key sets from parent
        universalkeys = super().multikeys
        
        # Specify calculation-specific key sets 
        keys =  [
            self.potential.keyset + self.system.keyset,
            self.system_mods.keyset,
            [
                'displacementdistance',
                'symmetryprecision',
                'numstrains',
                'strainrange',
            ],
        ]
          
        # Join and return
        return universalkeys + keys

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        return modelroot

    def build_model(self):

        # Build universal content
        model = super().build_model()
        calc = model[self.modelroot]

        # Build subset content
        self.commands.build_model(calc, after='atomman-version')
        self.potential.build_model(calc, after='calculation')
        self.system.build_model(calc, after='potential-LAMMPS')
        self.system_mods.build_model(calc)

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']
        run_params['displacementdistance'] = uc.model(self.displacementdistance,
                                                      self.units.length_unit)
        run_params['symmetryprecision'] = self.symmetryprecision
        run_params['strainrange'] = self.strainrange
        run_params['numstrains'] = self.numstrains

        # Build results
        if self.status == 'finished':
            calc['band-structure'] = DM()

            for qpoints in self.bandstructure['qpoints']:
                calc['band-structure'].append('qpoints', uc.model(qpoints))
                
            for distances in self.bandstructure['distances']:
                calc['band-structure'].append('distances', uc.model(distances))
                
            for frequencies in self.bandstructure['frequencies']:
                calc['band-structure'].append('frequencies', uc.model(frequencies))

            calc['density-of-states'] = DM()
            calc['density-of-states']['frequency'] = uc.model(self.dos['frequency'], 'THz')
            calc['density-of-states']['total_dos'] = uc.model(self.dos['total_dos'])
            calc['density-of-states']['projected_dos'] = uc.model(self.dos['projected_dos'])

            calc['thermal-properties'] = DM()
            calc['thermal-properties']['temperature'] = uc.model(self.thermal['temperature'], 'K')
            calc['thermal-properties']['Helmholtz'] = uc.model(self.thermal['Helmholtz'], 'eV')
            calc['thermal-properties']['entropy'] = uc.model(self.thermal['entropy'], 'J/K/mol')
            calc['thermal-properties']['heat_capacity_v'] = uc.model(self.thermal['heat_capacity_v'], 'J/K/mol')

            # Add qha results
            if self.__volumescan is not None:
                calc['thermal-properties']['volume'] = uc.model(self.thermal['volume'], 'angstrom^3')
                calc['thermal-properties']['thermal_expansion'] = uc.model(self.thermal['thermal_expansion'])
                calc['thermal-properties']['Gibbs'] = uc.model(self.thermal['Gibbs'], 'eV')
                calc['thermal-properties']['bulk_modulus'] = uc.model(self.thermal['bulk_modulus'], 'GPa')
                calc['thermal-properties']['heat_capacity_p_numerical'] = uc.model(self.thermal['heat_capacity_p_numerical'], 'J/K/mol')
                calc['thermal-properties']['heat_capacity_p_polyfit'] = uc.model(self.thermal['heat_capacity_p_polyfit'], 'J/K/mol')
                calc['thermal-properties']['gruneisen'] = uc.model(self.thermal['gruneisen'])
                
                calc['volume-scan'] = DM()
                calc['volume-scan']['volume'] = uc.model(self.volumescan['volume'], 'angstrom^3')
                calc['volume-scan']['strain'] = uc.model(self.volumescan['strain'])
                calc['volume-scan']['energy'] = uc.model(self.volumescan['energy'], 'eV')

                calc['E0'] = uc.model(self.E0, 'eV')
                calc['B0'] = uc.model(self.B0, 'GPa')
                calc['B0prime'] = uc.model(self.B0prime, 'GPa')
                calc['V0'] = uc.model(self.V0, 'angstrom^3')

        self._set_model(model)
        return model

    def load_model(self, model, name=None):

        # Load universal content
        super().load_model(model, name=name)
        calc = self.model[self.modelroot]

        # Load subset content
        #self.units.load_model(calc)
        self.potential.load_model(calc)
        self.commands.load_model(calc)
        self.system.load_model(calc)
        self.system_mods.load_model(calc)

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.displacementdistance = uc.value_unit(run_params['displacementdistance'])
        self.symmetryprecision = run_params['symmetryprecision']
        self.strainrange = run_params['strainrange']
        self.numstrains = run_params['numstrains']

        # Load results
        if self.status == 'finished':
            
            self.__bandstructure = {}
            self.bandstructure['qpoints'] = []
            for qpoints in calc['band-structure']['qpoints']:
                self.bandstructure['qpoints'].append(uc.value_unit(qpoints))
            
            self.bandstructure['distances'] = []
            for distances in calc['band-structure']['distances']:
                self.bandstructure['distances'].append(uc.value_unit(distances))
            
            self.bandstructure['frequencies'] = []
            for frequencies in calc['band-structure']['frequencies']:
                self.bandstructure['frequencies'].append(uc.value_unit(frequencies))

            self.__dos = {}
            self.dos['frequency'] = uc.value_unit(calc['density-of-states']['frequency'])
            self.dos['total_dos'] = uc.value_unit(calc['density-of-states']['total_dos'])
            self.dos['projected_dos'] = uc.value_unit(calc['density-of-states']['projected_dos'])

            self.__thermal = {}
            self.thermal['temperature'] = uc.value_unit(calc['thermal-properties']['temperature'])
            self.thermal['Helmholtz'] = uc.value_unit(calc['thermal-properties']['Helmholtz'])
            self.thermal['entropy'] = uc.value_unit(calc['thermal-properties']['entropy'])
            self.thermal['heat_capacity_v'] = uc.value_unit(calc['thermal-properties']['heat_capacity_v'])

            # Add qha results
            if 'volume-scan' in calc:
                self.thermal['volume'] = uc.value_unit(calc['thermal-properties']['volume'])
                self.thermal['thermal_expansion'] = uc.value_unit(calc['thermal-properties']['thermal_expansion'])
                self.thermal['Gibbs'] = uc.value_unit(calc['thermal-properties']['Gibbs'])
                self.thermal['bulk_modulus'] = uc.value_unit(calc['thermal-properties']['bulk_modulus'])
                self.thermal['heat_capacity_p_numerical'] = uc.value_unit(calc['thermal-properties']['heat_capacity_p_numerical'])
                self.thermal['heat_capacity_p_polyfit'] = uc.value_unit(calc['thermal-properties']['heat_capacity_p_polyfit'])
                self.thermal['gruneisen'] = uc.value_unit(calc['thermal-properties']['gruneisen'])
                
                self.__volumescan = {}
                self.volumescan['volume'] = uc.value_unit(calc['volume-scan']['volume'])
                self.volumescan['strain'] = uc.value_unit(calc['volume-scan']['strain'])
                self.volumescan['energy'] = uc.value_unit(calc['volume-scan']['energy'])

                self.__E0 = uc.value_unit(calc['E0'])
                self.__B0 = uc.value_unit(calc['B0'])
                self.__B0prime = uc.value_unit(calc['B0prime'])
                self.__V0 = uc.value_unit(calc['V0'])

    @staticmethod
    def mongoquery(name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None, lammps_version=None,
                   potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                   potential_key=None, potential_id=None, strainrange=None,
                   numstrains=None, symmetryprecision=None, displacementdistance=None,
                   ):
        
        # Build universal terms
        mquery = Calculation.mongoquery(modelroot, name=name, key=key,
                                    iprPy_version=iprPy_version,
                                    atomman_version=atomman_version,
                                    script=script, branch=branch,
                                    status=status)

        # Build subset terms
        mquery.update(LammpsCommands.mongoquery(modelroot,
                                                lammps_version=lammps_version))
        mquery.update(LammpsPotential.mongoquery(modelroot,
                                                 potential_LAMMPS_key=potential_LAMMPS_key,
                                                 potential_LAMMPS_id=potential_LAMMPS_id,
                                                 potential_key=potential_key,
                                                 potential_id=potential_id))
        #mquery.update(AtommanSystemLoad.mongoquery(modelroot,...)
        #mquery.update(AtommanSystemManipulate.mongoquery(modelroot,...)

        # Build calculation-specific terms
        root = f'content.{modelroot}'
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.strainrange', strainrange)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.numstrains', numstrains)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.symmetryprecision', symmetryprecision)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.displacementdistance', displacementdistance)

        return mquery

    @staticmethod
    def cdcsquery(key=None, iprPy_version=None,
                  atomman_version=None, script=None, branch=None,
                  status=None, lammps_version=None,
                  potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                  potential_key=None, potential_id=None, strainrange=None,
                  numstrains=None, symmetryprecision=None, displacementdistance=None,
                  ):
        
        # Build universal terms
        mquery = Calculation.cdcsquery(modelroot, key=key,
                                    iprPy_version=iprPy_version,
                                    atomman_version=atomman_version,
                                    script=script, branch=branch,
                                    status=status)

        # Build subset terms
        mquery.update(LammpsCommands.cdcsquery(modelroot,
                                               lammps_version=lammps_version))
        mquery.update(LammpsPotential.cdcsquery(modelroot,
                                                potential_LAMMPS_key=potential_LAMMPS_key,
                                                potential_LAMMPS_id=potential_LAMMPS_id,
                                                potential_key=potential_key,
                                                potential_id=potential_id))
        #mquery.update(AtommanSystemLoad.mongoquery(modelroot,...)
        #mquery.update(AtommanSystemManipulate.mongoquery(modelroot,...)

        # Build calculation-specific terms
        root = modelroot
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.strainrange', strainrange)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.numstrains', numstrains)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.symmetryprecision', symmetryprecision)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.displacementdistance', displacementdistance)

        return mquery

########################## Metadata interactions ##############################

    def metadata(self):
        """
        Converts the structured content to a simpler dictionary.
        
        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        # Extract universal content
        meta = super().metadata()
        
        # Extract subset content
        self.potential.metadata(meta)
        self.commands.metadata(meta)
        self.system.metadata(meta)
        self.system_mods.metadata(meta)

        # Extract calculation-specific content
        meta['displacementdistance'] = self.displacementdistance
        meta['symmetryprecision'] = self.symmetryprecision
        meta['strainrange'] = self.strainrange
        meta['numstrains'] = self.numstrains

        # Extract results
        if self.status == 'finished':
            meta['bandstructure'] = self.bandstructure
            meta['thermal'] = self.thermal
            meta['dos'] = self.dos
            if self.__volumescan is not None:
                meta['volumescan'] = self.volumescan
                meta['E0'] = self.E0
                meta['B0'] = self.B0
                meta['B0prime'] = self.B0prime
                meta['V0'] = self.V0
        
        return meta

    @property
    def compare_terms(self):
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',
        
            'load_file',
            'load_options',
            'symbols',
            
            'potential_LAMMPS_key',
            
            'a_mult',
            'b_mult',
            'c_mult',
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'symmetryprecision':1e-7,
        }

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, iprPy_version=None,
                     atomman_version=None, script=None, branch=None,
                     status=None, lammps_version=None,
                     potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                     potential_key=None, potential_id=None, strainrange=None,
                     numstrains=None, symmetryprecision=None, displacementdistance=None,
                     ):
        matches = (
            # Filter by universal terms
            Calculation.pandasfilter(dataframe, name=name, key=key,
                                 iprPy_version=iprPy_version,
                                 atomman_version=atomman_version,
                                 script=script, branch=branch, status=status)
            
            # Filter by subset terms
            &LammpsCommands.pandasfilter(dataframe,
                                         lammps_version=lammps_version)
            &LammpsPotential.pandasfilter(dataframe,
                                          potential_LAMMPS_key=potential_LAMMPS_key,
                                          potential_LAMMPS_id=potential_LAMMPS_id,
                                          potential_key=potential_key,
                                          potential_id=potential_id)
            #&AtommanSystemLoad.pandasfilter(dataframe, ...)
            #&AtommanSystemManipulate.pandasfilter(dataframe, ...)

            # Filter by calculation-specific terms
            &query.str_match.pandas(dataframe, 'strainrange', strainrange)
            &query.str_match.pandas(dataframe, 'numstrains', numstrains)
            &query.str_match.pandas(dataframe, 'symmetryprecision', symmetryprecision)
            &query.str_match.pandas(dataframe, 'displacementdistance', displacementdistance)

        )
        
        return matches

########################### Calculation interactions ##########################

    def calc_inputs(self):
        """Builds calculation inputs from the class's attributes"""
        
        # Initialize input_dict
        input_dict = {}

        # Add subset inputs
        self.commands.calc_inputs(input_dict)
        self.potential.calc_inputs(input_dict)
        self.system.calc_inputs(input_dict)
        #self.system_mods.calc_inputs(input_dict)

        # Remove unused subset inputs

        # Add calculation-specific inputs
        input_dict['distance'] = self.displacementdistance
        input_dict['symprec'] = self.symmetryprecision
        input_dict['strainrange'] = self.strainrange
        input_dict['numstrains'] = self.numstrains
        input_dict['a_mult'] = self.system_mods.a_mults[1] - self.system_mods.a_mults[0]
        input_dict['b_mult'] = self.system_mods.b_mults[1] - self.system_mods.b_mults[0]
        input_dict['c_mult'] = self.system_mods.c_mults[1] - self.system_mods.c_mults[0]

        # Return input_dict
        return input_dict
    
    def run(self, newkey=False, results_json=False, verbose=False):
        """
        Runs the calculation using the current class attribute values. Status
        after running will be either "finished" or "error".

        Parameters
        ----------
        newkey : bool, optional
            If True, then the calculation's key and name will be replaced with
            a new UUID4.  This allows for iterations on previous runs to be
            uniquely labeled.  Default value is False.
        results_json : bool, optional
            If True, then a "results.json" file will be generated following
            the run.
        verbose : bool, optional
            If True, a message relating to the calculation's status will be
            printed upon completion.  Default value is False.
        """
        # Run calculation
        results_dict = super().run(newkey=newkey, verbose=verbose)
        
        # Process results
        if self.status == 'finished':
            self.__phonons = results_dict['phonon_objects']
            self.__qha = results_dict['qha_object']
            self.__bandstructure = results_dict['band_structure']
            self.__dos = results_dict['density_of_states']
            self.__thermal = results_dict['thermal_properties']
            if 'volume_scan' in results_dict:
                self.__volumescan = results_dict['volume_scan']
                self.__E0 = results_dict['E0']
                self.__B0 = results_dict['B0']
                self.__B0prime = results_dict['B0prime']
                self.__V0 = results_dict['V0']

        self._results(json=results_json)