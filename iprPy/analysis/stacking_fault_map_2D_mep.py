import argparse
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

from DataModelDict import DataModelDict as DM

import iprPy

def stacking_fault_mep_runner(database_name: str,
                              nameletter: Optional[str] = None,
                              family: Optional[str] = None,
                              stackingfault_id: Optional[str] = None,
                              potential_LAMMPS_id: Optional[str] = None,
                              npoints: int = 31,
                              ipoints: int = 1001,
                              relaxsteps: int = 500000,
                              climbsteps: int = 500000):
    """
    Automated runner designed to iteratively evaluate minimum energy paths for
    stacking_fault_map_2D calculation results.  This script will find all such
    calculations with "finished" status and will search for the minimum energy
    path if one is not already in the calculation record.  Upon finishing, the
    calculation records will be updated and uploaded.

    Parameters
    ----------
    database_name : str
        The name of the database to use.
    nameletter : str or None, optional
        If given, this runner will only perform mep evaluations for
        calculations that have names starting with this letter.  As the
        calculation names are UUID4 strings, the first letter can have values
        of 0-9 and a-f.  This is useful for distributing work across multiple
        runners.
    family : str or None, optional
        If given, this runner will only perform mep evaluations for
        calculations with the given system prototype family.
    stackingfault_id : str or None, optional
        If given, this runner will only perform mep evaluations for
        calculations with the given stacking fault type as identified by a
        stackingfault_id value.
    potential_LAMMPS_id : str or None, optional
        If given, this runner will only perform mep evaluations for
        calculations that used the indicated LAMMPS potential.
    npoints : int, optional
        The number of discrete points to use for the path during relaxation.
        Default value is 31.
    ipoints : int, optional
        The number of discrete points to use for the path when evaluating the
        ideal shear stress.  Default value is 1000.
    relaxsteps : int, optional
        The maximum number of steps to perform during the relaxation phase of
        the mep evaluation.
    climbsteps : int, optional
        The maximum number of steps to perform during the climbing phase of
        the mep evaluation.
    """
    # Load the database
    database = iprPy.load_database(database_name)
    
    # Get all matching finished calculation results
    allrecords = database.get_records(style='calculation_stacking_fault_map_2D',
                                    family=family, stackingfault_id=stackingfault_id,
                                    potential_LAMMPS_id=potential_LAMMPS_id,
                                    status='finished', num_a1=30)
    
    # Filter records by first letter
    if nameletter is not None:
        records = []
        for record in allrecords:
            if record.name[0] == nameletter:
                records.append(record)
    else:
        records = allrecords
    print(f'{len(records)} total records found', flush=True)

    # Search for records that don't have mep results
    run_records = []
    for record in records:
        try:
            record.paths
        except ValueError:
            run_records.append(record)         
    print(f'{len(run_records)} records missing mep results', flush=True)

    for record in run_records:
        update = compute_props(record, npoints=npoints, ipoints=ipoints,
                               relaxsteps=relaxsteps, climbsteps=climbsteps)
        if update:
            database.update_record(record=record)
        break
    
def mep_relax(gamma, pos, direction, npoints=31, ipoints=1001, relaxsteps=500000,
              climbsteps=500000, climbpoints=1):
    
    # Construct initial path for relaxing along ideal
    path = gamma.build_path(pos, npoints)
    
    # Construct fine path along ideal (not for relaxing)
    idealpath = gamma.build_path(pos, ipoints)
    
    # Relax path and create fine interpolation
    path = path.relax(relaxsteps, climbsteps, climbpoints=climbpoints)
    ipath = path.interpolate_path(np.linspace(0.0, path.arccoord[-1], ipoints))
    
    # Create results DM
    results = DM()
    results['direction'] = direction
    results['minimum-energy-path'] = uc.model(path.coord, 'angstrom')
    results['unstable-fault-energy-mep'] = uc.model(ipath.energy().max(), 'mJ/m^2')
    results['unstable-fault-energy-unrelaxed-path'] = uc.model(idealpath.energy().max(), 'mJ/m^2')
    results['ideal-shear-stress-mep'] = uc.model(np.abs(ipath.force).max(), 'GPa')
    results['ideal-shear-stress-unrelaxed-path'] = uc.model(np.abs(idealpath.force).max(), 'GPa')

    return results

def compute_props(record, npoints=31, ipoints=1001, relaxsteps=500000, climbsteps=500000):

    # Check if content already exists
    content = record.model
    calc = content['calculation-stacking-fault-map-2D']
    if 'slip-path' in calc:
        return False
    
    print(record.name, flush=True)
    
    # Load gamma surface
    gamma = record.gamma
    
    # Select path calculation(s) based on defect id
    sfid = record.defect.id
    if sfid == 'A1--Cu--fcc--100sf':
        
        # Compute slip path mep
        direction = 'a/2 [0 -1 1]'
        pos = np.array([[0,0,0],
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
              
    elif sfid == 'A1--Cu--fcc--111sf':
        
        # Add intrinsic stacking fault energy
        calc['intrinsic-fault-energy'] = uc.model(gamma.E_gsf(a1=1/3, a2=1/3), 'mJ/m^2')
     
        # Compute slip path mep
        direction = 'a/2 [0 -1 1]'
        pos = np.array([[0,0,0],
                        (gamma.a1vect+gamma.a2vect)/3,
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=2)
        calc.append('slip-path', sp)
    
    elif sfid == 'A2--W--bcc--110sf':
        
        # Compute slip path mep
        direction = 'a/2 [-1 1 -1]'
        pos = np.array([[0,0,0],
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
        
    elif sfid == 'A2--W--bcc--112sf':
    
        # Compute slip path mep
        direction = 'a/2 [-1 -1 1]'
        pos = np.array([[0,0,0],
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
    
    elif sfid == 'A2--W--bcc--123sf':
    
        # Compute slip path mep
        direction = 'a/2 [-1 -1 1]'
        pos = np.array([[0,0,0],
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
    
    elif sfid == 'A3--Mg--hcp--0001sf':
    
        # Add intrinsic stacking fault energy
        calc['intrinsic-fault-energy'] = uc.model(gamma.E_gsf(a1=1/3, a2=1/3), 'mJ/m^2')
        
        # Compute slip path mep
        direction = 'a/3 [-2 1 1 0]'
        pos = np.array([[0,0,0],
                        (gamma.a1vect+gamma.a2vect)/3,
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=2)
        calc.append('slip-path', sp)
        
    elif sfid == 'A3--Mg--hcp--1010sf-1':
    
        # Compute slip path mep
        direction = 'a/3 [-1 2 -1 0]'
        pos = np.array([[0,0,0],
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
    
    elif sfid == 'A3--Mg--hcp--1010sf-2':
    
        # Compute slip path mep
        direction = 'a/3 [-1 2 -1 0]'
        pos = np.array([[0,0,0],
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
        
    elif sfid == 'A3--Mg--hcp--1011sf-1':
    
        # Compute slip path mep
        direction = 'a/3 [-1 2 -1 0]'
        pos = np.array([[0,0,0],
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
        
        # Compute slip path mep
        direction = 'a/3 [-2 1 1 3]'
        pos = np.array([[0,0,0],
                        gamma.a2vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
    
    elif sfid == 'A3--Mg--hcp--1011sf-2':
        
        # Compute slip path mep
        direction = 'a/3 [-1 2 -1 0]'
        pos = np.array([[0,0,0],
                        gamma.a1vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
        
        # Compute slip path mep
        direction = 'a/3 [-2 1 1 3]'
        pos = np.array([[0,0,0],
                        gamma.a2vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
    
    elif sfid == 'A3--Mg--hcp--2112sf':
        # Compute slip path mep
        direction = 'a/3 [-2 1 1 3]'
        pos = np.array([[0,0,0],
                        gamma.a2vect])
        sp = mep_relax(gamma, pos, direction, npoints=npoints, ipoints=ipoints,
                       relaxsteps=relaxsteps, climbsteps=climbsteps, climbpoints=1)
        calc.append('slip-path', sp)
        
    return True
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='runner for stacking fault map 2D minimum energy path evaluations')

    parser.add_argument('database',
                        help='database name')
    parser.add_argument('-n', '--nameletter', default=None,
                        help='first letter of calculation names (0-9 or a-f) to limit calculation pool by')
    parser.add_argument('-f', '--family', default=None,
                        help='crystal prototype to limit calculation pool by')
    parser.add_argument('-s', '--stackingfault_id', default=None,
                        help='defect id to limit calculation pool by')
    parser.add_argument('-p', '--potential_LAMMPS_id', default=None,
                        help='potential_LAMMPS_id to limit calculation pool by')
    args = parser.parse_args()


    stacking_fault_mep_runner(args.database,
                              nameletter=args.nameletter, family=args.family,
                              stackingfault_id=args.stackingfault_id,
                              potential_LAMMPS_id=args.potential_LAMMPS_id)