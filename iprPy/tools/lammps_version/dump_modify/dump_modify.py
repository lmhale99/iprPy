import os
import atomman.lammps as lmp

def dump_modify(lammps_command):
    """Does a quick call to a LAMMPS executable to test the dump_modify version"""
    filedir = os.path.dirname(os.path.abspath(__file__))
    try:
        lmp.run(lammps_command, 
                os.path.join(filedir, 'dump_modify_test1.in'), 
                logfile='dump_modify_test.lammps')
        version = 0
    except:
        try:
            lmp.run(lammps_command, 
                    os.path.join(filedir, 'dump_modify_test2.in'),
                    logfile='dump_modify_test.lammps')
            version = 1
        except:
            raise ValueError('LAMMPS command failed both known versions for dump_modify')
    
    os.remove('dump_modify_test.lammps')
    return version
    
