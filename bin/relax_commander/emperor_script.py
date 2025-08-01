from typing import Optional, Union

from pathlib import Path

from iprPy.workflow import Emperor
from iprPy.input import parse



def main(command_script: Union[Path, str],
         pools: Optional[list] = None,
         skip: Optional[list] = None,
         settings_script: Union[str, Path, None] = None,
         pool_script_directory: Union[Path, str] = '.',
         run_style: Optional[str] = None,
         debug: bool = False,
         ):
    """
    

    Parameters
    ----------
    command_script : Path or str
        The path to a file containing the database_name, lammps_command(s),
        and optional mpi_command to use.
    pools : list, optional
        The list of pools to prepare (and run) in order.  If None, then all
        supported prepare pools (not listed in skip) will be performed in
        incremental order.
    skip : list, optional
        For pools=None, skip gives a list of pools to not prepare.
    settings_script : Path or str, optional
        The path to a file containing any calculation setting changes that
        are to be applied to all calculation pools.  The settings in this
        script will override both the default settings and the pool-specific
        settings from the pool_scripts.  Default is None, meaning no script to
        load.
    pool_script_directory : Path or str
        Directory containing any "pool_{number}.in" scripts that provide
        pool-specific prepare settings.  Default value is '.' for the
        current working directory.  The settings in these scripts will override
        the default calculation settings but will be overridden themselves by
        the settings_script values.  Missing and empty pool scripts are allowed
        and indicate no modifications to make for that pool.
    
    """

    emperor = Emperor.from_script(command_script)

    if pools is None:
        pools = list(range(1, 20))
        if skip is not None:
            for i in skip:
                pools.pop(pools.index(i))

    if settings_script is not None:
        kwargs = parse(input_script)

    for pool in pools:
        
        input_script = Path(pool_script_directory, f'pool_{pool}.in')
        if not input_script.exists():
            input_script = None
        
        emperor.prepare(pool, input_script=input_script, debug=debug, **kwargs)

if __name__ == '__main__':
