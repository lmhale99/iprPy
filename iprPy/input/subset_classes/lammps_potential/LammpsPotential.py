import atomman.lammps as lmp

from DataModelDict import DataModelDict as DM

from ..Subset import Subset

class LammpsPotential(Subset):
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
                    'potential_file',
                    'potential_dir',
                ]
    
    @property
    def preparekeys(self):
        """
        list : The default input keys used by prepare.
        """
        return  self.templatekeys + [
                    'potential_content',
                    'potential_dir_content',
                ]

    @property
    def interpretkeys(self):
        """
        list : The default input keys accessed when interpreting input files.
        """
        return  self.preparekeys + [
                    'potential',
                ]
  
    def template(self, header=None):
        """
        str : The input file template lines.
        """
        # Specify default header
        if header is None:
            header = '\n# Potential definition and directory containing associated files'
        
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
        potential_file = input_dict[keymap['potential_file']]
        potential_dir = input_dict.get(keymap['potential_dir'], '')
        potential_content = input_dict.get(keymap['potential_content'], None)
        
        # Use potential_content instead of potential_file if given
        if potential_content is not None:
            potential_file = potential_content
        
        # Save processed terms
        input_dict[keymap['potential_dir']] = potential_dir
        input_dict[keymap['potential']] = lmp.Potential(potential_file,
                                                        potential_dir)

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

        record_model[f'{modelprefix}potential-LAMMPS'] = pot = DM()

        pot['key'] = input_dict[f'{prefix}potential'].key
        pot['id'] = input_dict[f'{prefix}potential'].id
        pot['potential'] = DM()
        pot['potential']['key'] = input_dict[f'{prefix}potential'].potkey
        pot['potential']['id'] = input_dict[f'{prefix}potential'].potid
        
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
        
        pot = record_model[f'{modelprefix}potential-LAMMPS']
        params[f'{prefix}potential_LAMMPS_key'] = pot['key']
        params[f'{prefix}potential_LAMMPS_id'] = pot['id']
        params[f'{prefix}potential_key'] = pot['potential']['key']
        params[f'{prefix}potential_id'] = pot['potential']['id']