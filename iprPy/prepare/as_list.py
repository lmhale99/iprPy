def iter_as_list(term):
    """Iterate over list representation of term"""
    if isinstance(term, (str, unicode)):
        yield term
    else:
        try:
            for t in term:
                yield t
        except:
            yield term
            
def as_list(term):
    """Return list representation of term"""
    return [t for t in iter_as_list(term)]