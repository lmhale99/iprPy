
from yabadaba import unitconvert as uc
from yabadabado.value import ResultValue

# iprPy imports
from .. import Calculation
from .isolated_atom import isolated_atom

class EnergyDict(ResultValue):
    """Represents the elemental isolated atom energies as a dict"""
    
    @property
    def unit(self):
        """All values should default to eV in model form"""
        return 'eV'

    def set_value_mod(self, val):        

        # Return None for unset results
        if val is None:
            return None

        # Convert dict values to floats if needed
        elif isinstance(val, dict) and 'energy' not in val:
            for k, v in val.items():
                val[k] = uc.set_in_units(v)

        # Convert single model dict entry to proper format
        elif isinstance(val, dict) and 'energy' in val:
            val = {val['symbol']: uc.value_unit(val['energy'])}

        elif isinstance(val, list):
            newval = {}
            for valentry in val:
                if not isinstance(valentry, dict):
                    raise TypeError('list values must contain only dicts')
                newval[valentry['symbol']] = uc.value_unit(valentry['energy'])
            val = newval

        else:
            raise TypeError('invalid input value: should be None, dict or list')
        
        return val
    
    def build_model_value(self):
        if self.value is None:
            return None

        if len(self.value) == 1:
            symbol = list(self.value.keys())[0]
            energy = self.value[symbol]
            return {
                'symbol': symbol,
                'energy': uc.model(self.value[symbol], self.unit)
            }

        values = []
        for symbol, energy in self.value.items():
            values.append({
                'symbol': symbol,
                'energy': uc.model(energy, self.unit)
            })
        
        return values
           
    def metadata(self, meta):
        """
        Adds the parameter to the record's metadata dict.

        Parameters
        ----------
        meta : dict
            The metadata dict being built for the record.
        """
        if self.value is None:
            return
        
        # Convert values to unit 
        value = {}
        for key, val in self.value.items():
            value[key] = uc.get_in_units(val, self.unit)

        if self.metadataparent is None:
            meta[self.metadatakey] = value

        else:
            if self.metadataparent not in meta:
                meta[self.metadataparent] = {}
            meta[self.metadataparent][self.metadatakey] = value



class IsolatedAtom(Calculation):
    """Class for managing isolated atom energy calculations"""

############################# Core properties #################################

    def _init_calc(self):
        self.calc = isolated_atom

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """

        # Set the core calculation values
        super()._init_values()

        self._add_value('calculation_subset', 'commands',
                        modelpath='calculation',
                        recordclass = 'subset_lammpscommands',
                        loadorder = 2,
                        description = 'The LAMMPS (and MPI) commands to use')
        
        self._add_value('calculation_subset', 'potential',
                        recordclass = 'subset_lammpspotential',
                        loadorder = 3,
                        description = 'The LAMMPS potential')

        self._add_value('calculation_subset', 'units',
                        recordclass = 'subset_units',
                        modelpath = False,
                        metadatakey = False,
                        loadorder = 1,
                        description = 'input/output units')

        self._add_value(EnergyDict, 'isolated_atom_energy',
                        calcname='energy',
                        description = 'The isolated atom energy for each unique element model')

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""
        return [
            'isolated_atom.py'
        ]

############################## Class attributes ###############################

    def master_prepare_inputs(self,
                              branch: str = 'main',
                              **kwargs) -> dict:
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
    def singularkeys(self) -> list:
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
    def multikeys(self) -> list:
        """list: Calculation key sets that can have multiple values during prepare."""

        keys = (
            # Universal multikeys
            super().multikeys +

            # Potential keys
            [
                self.potential.keyset
            ]
        )
        return keys

########################### Data model interactions ###########################

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'calculation-isolated-atom'

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        return [
            'potential_LAMMPS_key',
            'potential_key',
        ]

    @property
    def compare_fterms(self) -> dict:
        """dict: The terms to compare metadata values using a tolerance."""
        return {}

########################### Calculation interactions ##########################

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return [
            'init.dat',
            'log.lammps',
            'run0.in'
        ]
