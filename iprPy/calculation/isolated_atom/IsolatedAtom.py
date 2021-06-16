# coding: utf-8
# Standard Python libraries
import uuid
from copy import deepcopy

from datamodelbase import query

#
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

#
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Calculation
from .isolated_atom import isolated_atom
from ...calculation_subset import LammpsPotential, LammpsCommands, Units

# Global class properties
modelroot = 'calculation-isolated-atom'

class IsolatedAtom(Calculation):
    """Class for managing isolated atom energy calculations"""

############################# Core properties #################################

    def __init__(self, model=None, name=None, params=None, **kwargs):
        """
        Initializes a Calculation object for a given style.
        """

        # Initialize subsets used by the calculation
        self.__potential = LammpsPotential(self)
        self.__commands = LammpsCommands(self)
        self.__units = Units(self)

        # Initialize unique calculation attributes
        self.__isolated_atom_energy = {}
        
        # Define calc shortcut
        self.calc = isolated_atom

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
    def isolated_atom_energy(self):
        """dict : The per-symbol isolated atom energies"""
        return self.__isolated_atom_energy

    def set_values(self, name=None, **kwargs):
        """
        Used to set initial common values for the calculation.
        """
        # Set universal content
        super().set_values(name=None, **kwargs)

        # Set subset values
        self.units.set_values(**kwargs)
        self.potential.set_values(**kwargs)
        self.commands.set_values(**kwargs)

        # Set calculation-specific values


##################### Parameter file interactions ########################### 

    def load_parameters(self, params, key=None):
        
        # Load universal content
        input_dict = super().load_parameters(params, key=key)
        
        # Load input/output units
        self.units.load_parameters(input_dict)
        
        # Load calculation-specific strings
        
        # Load calculation-specific booleans
        
        # Load calculation-specific integers
        
        # Load calculation-specific unitless floats
        
        # Load calculation-specific floats with units
        
        # Load LAMMPS commands
        self.commands.load_parameters(input_dict)
        
        # Load LAMMPS potential
        self.potential.load_parameters(input_dict)
    
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
            params['buildcombos'] = 'lammpspotential potential_file intpot'

            # Copy kwargs to params
            for key in kwargs:
                
                # Rename potential-related terms for buildcombos
                if key[:10] == 'potential_':
                    params[f'intpot_{key}'] = kwargs[key]
                
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
        template += self.units.template()

        # Build calculation-specific content
        
        # Return template
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
        
        keys = [
            
            # Universal keys
            #super().multikeys,
            
            # Subset keys
            self.potential.keyset

            # Calculation-specific keys
        ]

        return keys

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

        # Build calculation-specific content

        # Build results
        if self.status == 'finished':
            for symbol, energy in self.isolated_atom_energy.items():
                isoatom = DM()
                isoatom['symbol'] = symbol
                isoatom['energy'] = uc.model(energy, self.units.energy_unit)
                calc.append('isolated-atom-energy', isoatom)

        return model

    def load_model(self, model, name=None):

        # Load universal content
        super().load_model(model, name=name)
        calc = self.model[self.modelroot]

        # Load subset content
        #self.units.load_model(calc)
        self.potential.load_model(calc)
        self.commands.load_model(calc)

        # Load calculation-specific content

        # Load results
        if self.status == 'finished':
           for isoatom in calc.aslist('isolated-atom-energy'):
               symbol = isoatom['symbol']
               energy = uc.value_unit(isoatom['energy'])
               self.isolated_atom_energy[symbol] = energy

    @staticmethod
    def mongoquery(name=None, key=None, iprPy_version=None,
                   atomman_version=None, script=None, branch=None,
                   status=None, lammps_version=None,
                   potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                   potential_key=None, potential_id=None):
        
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

        # Build calculation-specific terms
        root = f'content.{modelroot}'

        return mquery

    @staticmethod
    def cdcsquery(key=None, iprPy_version=None,
                  atomman_version=None, script=None, branch=None,
                  status=None, lammps_version=None,
                  potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                  potential_key=None, potential_id=None):
        
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

        # Build calculation-specific terms
        root = modelroot

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

        # Extract calculation-specific content
        
        # Extract results
        if self.status == 'finished':
            meta['isolated_atom_energy'] = deepcopy(self.isolated_atom_energy)

        return meta

    @property
    def compare_terms(self):
        """list: The terms to compare metadata values absolutely."""
        return [
            'script',
            'potential_LAMMPS_key',
        ]
    
    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, iprPy_version=None,
                     atomman_version=None, script=None, branch=None,
                     status=None, lammps_version=None,
                     potential_LAMMPS_key=None, potential_LAMMPS_id=None,
                     potential_key=None, potential_id=None):
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

            # Filter by calculation-specific terms
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

        # Add calculation-specific inputs

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
        results_dict = super().run(newkey=newkey, results_json=results_json,
                                   verbose=verbose)
        
        # Process results
        if self.status == 'finished':
            for symbol, energy in results_dict['energy'].items():
                self.isolated_atom_energy[symbol] = energy