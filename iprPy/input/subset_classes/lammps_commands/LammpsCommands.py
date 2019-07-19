import atomman.lammps as lmp

from DataModelDict import DataModelDict as DM

from ..Subset import Subset

class LammpsCommands(Subset):
    """
    Defines interactions for input keys associated with specifying input/output
    units.
    """
    
    @property
    def templatekeys(self):
        """
        list : The default input keys used by the calculation.
        """
        return  [
                    'lammps_command',
                    'mpi_command',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The default input keys used by prepare.
        """
        return  self.templatekeys + []
        
    @property
    def interpretkeys(self):
        """
        list : The default input keys accessed when interpreting input files.
        """
        return  self.preparekeys + [
                    'lammps_version',
                    'lammps_date'
                ]
    
    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Command lines for LAMMPS and MPI'
        
        return super().template(header=header)

    def interpret(self, input_dict):
        """
        Interprets calculation parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary containing input parameter key-value pairs.
        """

        # Set default keynames
        keymap = self.keymap
        
        # Extract input values and assign default values
        lammps_command = input_dict[keymap['lammps_command']]
        mpi_command = input_dict.get(keymap['mpi_command'], None)
        
        # Retrieve lammps_version info
        lammps_version = lmp.checkversion(lammps_command)
        
        # Save processed terms
        input_dict[keymap['mpi_command']] = mpi_command
        input_dict[keymap['lammps_version']] = lammps_version['version']
        input_dict[keymap['lammps_date']] = lammps_version['date']

    def buildcontent(self, record_model, input_dict, results_dict=None):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        record_model : DataModelDict.DataModelDict
            The record content (after root element) to add content to.
        input_dict : dict
            Dictionary of all input parameter terms.
        results_dict : dict, optional
            Dictionary containing any results produced by the calculation.
        """
        prefix = self.prefix
        modelprefix = prefix.replace('_', '-')
        
        if 'calculation' not in record_model:
            record_model['calculation'] = DM()
        record_model['calculation'][f'{modelprefix}LAMMPS-version'] = input_dict[f'{prefix}lammps_version']
        
    def todict(self, record_model, params, full=True, flat=False):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        record_model : DataModelDict.DataModelDict
            The record content (after root element) to interpret.
        params : dict
            The dictionary to add the interpreted content to
        full : bool, optional
            Flag used by the calculation records.  A True value will include
            terms for both the calculation's input and results, while a value
            of False will only include input terms (Default is True).
        flat : bool, optional
            Flag affecting the format of the dictionary terms.  If True, the
            dictionary terms are limited to having only str, int, and float
            values, which is useful for comparisons.  If False, the term
            values can be of any data type, which is convenient for analysis.
            (Default is False).
        """
        prefix = self.prefix
        modelprefix = prefix.replace('_', '-')
        params[f'{prefix}LAMMPS_version'] = record_model['calculation'][f'{modelprefix}LAMMPS-version']