from pathlib import Path
from tqdm import tqdm
import iprPy

def sort_calculations(calc_style, source_run_directory, target_run_directory):
    """
    Searches for all calculations of the given type in the source 
    directory and moves them into the target directory.

    Parameters
    ----------
    calc_style : str
        The calculation style name to sort out.
    source_run_directory : str
        The run_directory name that indicates the source directory.
    target_run_directory : str
        The run_directory name that indicates the source directory.
    """
    script_name = f'calc_{calc_style}.in'

    source = iprPy.load_run_directory(source_run_directory)
    target = iprPy.load_run_directory(target_run_directory)

    print(f'Moving {calc_style} from {source_run_directory} to {target_run_directory}')

    for script_path in tqdm(Path(source).glob(f'*/{script_name}')):
        calc_path = script_path.parent
        new_path = Path(target, calc_path.name)
        calc_path.rename(new_path)


if __name__ == '__main__':
    
    # This is the directory that all orphans were reset into
    source_run_directory = 'iprhub_33'

    sort_calculations('crystal_space_group', 'iprhub_33', 'iprhub_5')
    sort_calculations('relax_static', 'iprhub_33', 'iprhub_1')
    sort_calculations('stacking_fault_map_2D', 'iprhub_33', 'iprhub_7')