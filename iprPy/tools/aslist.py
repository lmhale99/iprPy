def iaslist(term):
    """Iterate over list representation of term"""
    if isinstance(term, (str, unicode)):
        yield term
    else:
        try:
            for t in term:
                yield t
        except:
            yield term
            
def aslist(term):
    """Return list representation of term"""
    return [t for t in iaslist(term)]