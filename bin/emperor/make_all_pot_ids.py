import iprPy
import numpy as np

database = iprPy.load_database('iprhub')
database.build_potdb(remote=False)
lmppots_df = database.potdb.get_lammps_potentials(return_df=True)[1]
all_lmppot_ids = np.unique(lmppots_df.id).tolist()

maxlen = 0
for lmppot_id in all_lmppot_ids:
    if len(lmppot_id) > maxlen:
        maxlen = len(lmppot_id)

with open('all_pot_ids.txt', 'w') as f:
    for i, lmppot_id in enumerate(all_lmppot_ids):
        f.write(f'potential_id {lmppot_id:{maxlen+1}} # {i}\n')
