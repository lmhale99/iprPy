from yabadabado.calculation import CalculationSubset

__all__ = ['LammpsCommands']

class LammpsCommands(CalculationSubset):
    """Handles calculation terms for LAMMPS executable commands"""

############################# Core properties #################################

    def _init_values(self):

        self._add_value('input_lammps', 'lammps_command',
                        modelpath = 'LAMMPS-version',
                        metadatakey = 'LAMMPS_version',
                        description = "Specifies which LAMMPS to use: either a path to a LAMMPS executable or give 'LAMMPSLIB' to use the LAMMPS library interface")

        self._add_value('input_str', 'mpi_command',
                        modelpath = None,
                        metadatakey = False,
                        description = "The path to the MPI executable and any command line options to use for calling LAMMPS to run in parallel on your system. LAMMPS will run as a serial process if not given.")

########################### Calculation interactions ##########################

    @property
    def modelroot(self):
        return 'commands'

    @property
    def modelsortkeys(self) -> list | None:
        return [
            'iprPy-version',
            'atomman-version',
            'LAMMPS-version',
            'script',
            'branch',
        ]

####################### Parameter file interactions ###########################

    @property
    def template_header(self) -> str:
        return '# LAMMPS and MPI Commands'