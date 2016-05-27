import sys
import importlib

def import_calc(dir, name):

    path = list(sys.path)
    sys.path.insert(0, dir)
    try:
        calc = importlib.import_module(name)
    except:
        raise ImportError('Failed to import ' + name)
    finally:
        sys.path[:] = path # restore path
    return calc