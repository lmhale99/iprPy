from pathlib import Path
import iprPy

csv_root_dir = Path('E:/website/IPR-website/potentials/entry')
database = iprPy.load_database('iprhub')

iprPy.analysis.process_all_relaxations(database, csv_root_dir=csv_root_dir, verbose=True)