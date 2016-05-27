import os
import sys
import importlib

def __load_calc():
    calc = {}
    names = []
    dir = os.path.dirname(__file__)

    for name in os.listdir(dir):
        
        if '.' in name:
            name, type = name.split('.')
            if type.lower() not in ('py', 'pyc') or name == '__init__':
                continue
        names.append(name)
          
    path = list(sys.path)
    sys.path.insert(0, dir)
    try:
        for name in names:
            try:
                calc[name] = importlib.import_module(name)
            except:
                print 'Failed to load', name
    finally:
        sys.path[:] = path # restore path

    return calc
    

calc = __load_calc()