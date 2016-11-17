import os
import importlib

def __load_calc():
    calc = {}
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
        #try:
        if True:
            calc[name] = importlib.import_module('.'+name, 'iprPy.calculations')
        #except:
        else:
            print 'Failed to load', name

    return calc
    

calc = __load_calc()