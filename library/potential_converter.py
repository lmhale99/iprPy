from __future__ import print_function, division
import os
import glob
import uuid
import shutil

from DataModelDict import DataModelDict as DM

# Create new library directory
if not os.path.isdir('potential-LAMMPS'):
    os.mkdir('potential-LAMMPS')

# Loop over all LAMMPS-potential json files
for fname in glob.iglob(os.path.join('LAMMPS-potential', '*.json')):
    
    # Read in old model
    with open(fname) as f:
        oldmodel = DM(f)
    
    # Generate new model with unique key, id
    oldid = oldmodel['LAMMPS-potential']['potential']['id']
    newid = oldid + '--LAMMPS--ipr1'
    newmodel = DM()
    newmodel['potential-LAMMPS'] = DM()
    newmodel['potential-LAMMPS']['key'] = str(uuid.uuid4())
    newmodel['potential-LAMMPS']['id'] = newid
    
    # Copy over all other model keys
    for key in oldmodel['LAMMPS-potential']:
        newmodel['potential-LAMMPS'][key] = oldmodel['LAMMPS-potential'][key]
        
    # Save new record
    with open(os.path.join('potential-LAMMPS', newid + '.json'), 'w') as f:
        newmodel.json(fp=f, indent=4)
        
    # Copy over all associated potential files
    potfiles = oldmodel.finds('file')
    if len(potfiles) > 0 and not os.path.isdir(os.path.join('potential-LAMMPS', newid)):
        os.mkdir(os.path.join('potential-LAMMPS', newid))
    for potfile in potfiles:
        shutil.copy(os.path.join('LAMMPS-potential', oldid, potfile),
                    os.path.join('potential-LAMMPS', newid, potfile))
        