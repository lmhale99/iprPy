from DataModelDict import DataModelDict as DM

def term_extractor(terms, keys):
    t = DM()
    i = 0
    key = None
    while i < len(terms):
        if terms[i] in keys:
            key = terms[i]
        else:
            if key is None:
                raise ValueError('Invalid terms line')
            else:
                t.append(key, terms[i])
        i += 1
    return t        
