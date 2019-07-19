from .subset_classes import loaded

def subset(style, prefix=''):
    return loaded[style](prefix=prefix)