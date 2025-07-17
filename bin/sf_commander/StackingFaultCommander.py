import argparse

from iprPy import load_database
from iprPy.analysis import StackingFaultMEPCommander

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

    commander = StackingFaultMEPCommander(args.database,
                                          nameletter = args.nameletter,
                                          family = args.family,
                                          stackingfault_id = args.stackingfault_id,
                                          potential_LAMMPS_id = args.potential_LAMMPS_id,
                                          verbose = True)
    commander.runall_mep()
