# coding: utf-8
# Standard Python libraries

from yabadaba import query

# http://www.numpy.org/
import numpy as np

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
        subsets = (self.commands, self.potential, self.system,
                   self.units)

        # Initialize unique calculation attributes
        self.strainrange = 0.01
        self.displacementdistance = uc.set_in_units(0.01, 'angstrom')
        self.symmetryprecision = 1e-5         
        self.numstrains = 5
        self.a_mult = 2 
        self.b_mult = 2
        self.c_mult = 2
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
        super().__init__(model=model, name=name, params=params,
                         subsets=subsets, **kwargs)

    @property
    def filenames(self):
        """list: the names of each file used by the calculation."""
        return [
            'calc_phonon.py',
            'phonon.template'
        ]

############################## Class attributes ###############################

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
    def a_mult(self):
        """int: Number of replicas along the a box vect to use"""
        return self.__a_mult

    @a_mult.setter
    def a_mult(self, value):
        self.__a_mult = int(value)

    @property
    def b_mult(self):
        """int: Number of replicas along the b box vect to use"""
        return self.__b_mult

    @b_mult.setter
    def b_mult(self, value):
        self.__b_mult = int(value)

    @property
    def c_mult(self):
        """int: Number of replicas along the c box vect to use"""
        return self.__c_mult

    @c_mult.setter
    def c_mult(self, value):
        self.__c_mult = int(value)

    @property
    def sizemults(self):
        """tuple: All three sets of size multipliers"""
        return (self.a_mult, self.b_mult, self.c_mult)

    @sizemults.setter
    def sizemults(self, value):
        if len(value) == 3:
            self.a_mult = value[0]
            self.b_mult = value[1]
            self.c_mult = value[2]
        else:
            raise ValueError('len of sizemults must be 3')

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
        """
        Set calculation values directly.  Any terms not given will be set
        or reset to the calculation's default values.

        Parameters
        ----------
        name : str, optional
            The name to assign to the calculation.  By default, this is set as
            the calculation's key.
        strainrange : float, optional
            Strain step size to use for quasiharmonic method.
        numstrains : int, optional
            The number of strain states to evaluate for the quasiharmonic
            method.
        symmetryprecision : float, optional
            Tolerance used for identifying crystal symmetry elements
        displacementdistance : float, optional
            Random max atomic displacement to use for phonon calculations
        **kwargs : any, optional
            Any keyword parameters supported by the set_values() methods of
            the parent Calculation class and the subset classes.
        """
        # Call super to set universal and subset content
        super().set_values(name=name, **kwargs)

        # Set calculation-specific values
        if 'strainrange' in kwargs:
            self.strainrange = kwargs['strainrange']
        if 'numstrains' in kwargs:
            self.numstrains = kwargs['numstrains']
        if 'symmetryprecision' in kwargs:
            self.symmetryprecision = kwargs['symmetryprecision']
        if 'displacementdistance' in kwargs:
            self.displacementdistance = kwargs['displacementdistance']
        if 'sizemults' in kwargs:
            if 'a_mult' in kwargs or 'b_mult' in kwargs or 'c_mult' in kwargs:
                raise ValueError('Cannot set sizemults and individual mults at the same time')
            self.sizemults = kwargs['sizemults']
        if 'a_mult' in kwargs:
            self.a_mult = kwargs['a_mult']
        if 'b_mult' in kwargs:
            self.a_mult = kwargs['b_mult']
        if 'c_mult' in kwargs:
            self.a_mult = kwargs['c_mult']

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
        self.numstrains = int(input_dict.get('numstrains', 11))

        # Load calculation-specific unitless floats
        self.symmetryprecision = float(input_dict.get('symmetryprecision', 1e-5))
        self.strainrange = float(input_dict.get('strainrange', 0.05))

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

        # Handle sizemults
        self.sizemults = np.array(input_dict['sizemults'].strip().split(), dtype=int)

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
    def templatekeys(self):
        """dict : The calculation-specific input keys and their descriptions."""

        return {
            'displacementdistance': ' '.join([
                "Max distance atoms are displaced for the phonon evaluations.",
                "Default  value is 0.01 angstrom"]),
            'symmetryprecision': ' '.join([
                "Precision tolerance to use for identifying symmetry elements.",
                "Default value is 1e-5."]),
            'numstrains': ' '.join([
                "The number of strain states to evaluate for performing the",
                "quasiharmonic approximation.  If set to 1, then the quasiharmonic",
                "calculations will be skipped.  Default value is 11."]),
            'strainrange': ' '.join([
                "The range of strains to apply for performing the",
                "quasiharmonic approximation.  Default value is 0.05."]),
            'sizemults': ' '.join([
                "Multiplication parameters to construct a supercell system.",
                "Limited to three values for this calculation.  Default value"
                "is 3 3 3."]),
        } 

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

        keys = (
            # Universal multikeys
            super().multikeys +

            # Combination of potential and system keys
            [
                self.potential.keyset + 
                self.system.keyset
            ] +

            # Run parameters
            [
                [
                    'displacementdistance',
                    'symmetryprecision',
                    'numstrains',
                    'strainrange',
                    'sizemults'
                ]
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'calculation-phonon'

    def build_model(self):
        """
        Generates and returns model content based on the values set to object.
        """
        # Build universal content
        model = super().build_model()
        calc = model[self.modelroot]

        # Build subset content
        self.commands.build_model(calc, after='atomman-version')
        self.potential.build_model(calc, after='calculation')
        self.system.build_model(calc, after='potential-LAMMPS')

        # Build calculation-specific content
        if 'calculation' not in calc:
            calc['calculation'] = DM()
        if 'run-parameter' not in calc['calculation']:
            calc['calculation']['run-parameter'] = DM()
        run_params = calc['calculation']['run-parameter']
        run_params['size-multipliers'] = DM()
        run_params['size-multipliers']['a'] = [0, self.a_mult]
        run_params['size-multipliers']['b'] = [0, self.b_mult]
        run_params['size-multipliers']['c'] = [0, self.c_mult]
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
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
        # Load universal and subset content
        super().load_model(model, name=name)
        calc = self.model[self.modelroot]

        # Load calculation-specific content
        run_params = calc['calculation']['run-parameter']
        self.a_mult = run_params['size-multipliers']['a'][1]
        self.b_mult = run_params['size-multipliers']['b'][1]
        self.c_mult = run_params['size-multipliers']['c'][1]
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

    def mongoquery(self, strainrange=None, numstrains=None,
                   symmetryprecision=None, displacementdistance=None, **kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.

        Parameters
        ----------
        strainrange : float or list, optional
            strainrange values to parse by.
        numstrains : int or list, optional
            numstrains values to parse by.
        symmetryprecision : float or list, optional
            symmetryprecision values to parse by.
        displacementdistance : float or list, optional
            displacementdistance values to parse by.
        **kwargs : any
            Any extra query terms that are universal for all calculations
            or associated with one of the calculation's subsets.        
        
        Returns
        -------
        dict
            The Mongo-style query.
        """
        # Call super to build universal and subset terms
        mquery = super().mongoquery(**kwargs)

        # Build calculation-specific terms
        root = f'content.{self.modelroot}'
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.strainrange', strainrange)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.numstrains', numstrains)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.symmetryprecision', symmetryprecision)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.displacementdistance', displacementdistance)

        return mquery

    def cdcsquery(self, strainrange=None, numstrains=None,
                  symmetryprecision=None, displacementdistance=None, **kwargs):
        """
        Builds a CDCS-style query based on kwargs values for the record style.

        Parameters
        ----------
        strainrange : float or list, optional
            strainrange values to parse by.
        numstrains : int or list, optional
            numstrains values to parse by.
        symmetryprecision : float or list, optional
            symmetryprecision values to parse by.
        displacementdistance : float or list, optional
            displacementdistance values to parse by.
        **kwargs : any
            Any extra query terms that are universal for all calculations
            or associated with one of the calculation's subsets.       
        
        Returns
        -------
        dict
            The CDCS-style query.
        """
        # Call super to build universal and subset terms
        mquery = super().cdcsquery(**kwargs)

        # Build calculation-specific terms
        root = self.modelroot
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.strainrange', strainrange)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.numstrains', numstrains)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.symmetryprecision', symmetryprecision)
        query.str_match.mongo(mquery, f'{root}.calculation.run-parameter.displacementdistance', displacementdistance)

        return mquery

########################## Metadata interactions ##############################

    def metadata(self):
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        # Call super to extract universal and subset content
        meta = super().metadata()

        # Extract calculation-specific content
        meta['displacementdistance'] = self.displacementdistance
        meta['symmetryprecision'] = self.symmetryprecision
        meta['strainrange'] = self.strainrange
        meta['numstrains'] = self.numstrains

        # Extract results
        if self.status == 'finished':
            #meta['bandstructure'] = self.bandstructure
            #meta['thermal'] = self.thermal
            #meta['dos'] = self.dos
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
            'potential_key',
            
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {
            'symmetryprecision':1e-7,
        }

    def pandasfilter(self, dataframe, strainrange=None, numstrains=None,
                     symmetryprecision=None, displacementdistance=None,
                     **kwargs):
        """
        Parses a pandas dataframe containing the subset's metadata to find 
        entries matching the terms and values given. Ideally, this should find
        the same matches as the mongoquery and cdcsquery methods for the same
        search parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The metadata dataframe to filter.
        strainrange : float or list, optional
            strainrange values to parse by.
        numstrains : int or list, optional
            numstrains values to parse by.
        symmetryprecision : float or list, optional
            symmetryprecision values to parse by.
        displacementdistance : float or list, optional
            displacementdistance values to parse by.
        kwargs : any
            Any extra query terms that are universal for all calculations
            or associated with one of the calculation's subsets. 

        Returns
        -------
        pandas.Series of bool
            True for each entry where all filter terms+values match, False for
            all other entries.
        """
        # Call super to filter by universal and subset terms
        matches = super().pandasfilter(dataframe, **kwargs)

        # Filter by calculation-specific terms
        matches = (matches
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
        for subset in self.subsets:
            subset.calc_inputs(input_dict)

        # Add calculation-specific inputs
        input_dict['distance'] = self.displacementdistance
        input_dict['symprec'] = self.symmetryprecision
        input_dict['strainrange'] = self.strainrange
        input_dict['numstrains'] = self.numstrains
        input_dict['a_mult'] = self.a_mult
        input_dict['b_mult'] = self.b_mult
        input_dict['c_mult'] = self.c_mult

        # Return input_dict
        return input_dict
    
    def process_results(self, results_dict):
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
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