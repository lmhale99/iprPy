from .. import recordmanager

# Dynamically import subsets as records with prefix subset_
ignorelist = ['__pycache__', '__init__']
recordmanager.dynamic_import(__name__, ignorelist, 'subset_')