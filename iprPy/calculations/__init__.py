import os
import importlib

failed_calculations = []

def __load_calculations():
    calculations_dict = {}
    names = []
    dir = os.path.dirname(__file__)

    for name in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, name)):
            names.append(name)
            
        elif os.path.isfile(os.path.join(dir, name)):
            name, ext = os.path.splitext(name)
            
            if ext.lower() in ('.py', '.pyc') and name != '__init__' and name not in names:
                names.append(name)
        
    for name in names:
        if True:
        #try:
            calculations_dict[name] = importlib.import_module('.'+name, 'iprPy.calculations')
        else:
        #except:
            failed_calculations.append(name)

    return calculations_dict

calculations_dict = __load_calculations()