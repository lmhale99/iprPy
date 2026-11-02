from yabadabado import valuemanager, load_value

# Dynamically import value submodules
ignorelist = ['__pycache__', '__init__']
valuemanager.dynamic_import(__name__, ignorelist)