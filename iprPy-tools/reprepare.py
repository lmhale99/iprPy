import os
import shutil
import glob

xml_dir = 'C:/users/lmh1/Documents/iprPy_run/xml_library'
sim_dir = 'C:/users/lmh1/Documents/iprPy_run/'
calc =    'C:/users/lmh1/Documents/iprPy/calculation/calc_structure_static.py'

to_run = os.path.join(sim_dir, 'to_run')

for badlist in glob.iglob(os.path.join(xml_dir, '*', 'structure_static', 'badlist.txt')):
    #with open(badlist) as f:
    #    for bad in f.read().split():
    #        sim_dir = os.path.join(has_ran, bad)
    #        if os.path.isdir(sim_dir):
    #            shutil.move(os.path.join(has_ran, bad), to_run)
    os.remove(badlist)
            
#for fname in glob.iglob(os.path.join(to_run, '*', '*.bid')):
#    os.remove(fname)
    
#for sim_dir in glob.iglob(os.path.join(to_run, '*')):
#    shutil.copy(calc, sim_dir)

