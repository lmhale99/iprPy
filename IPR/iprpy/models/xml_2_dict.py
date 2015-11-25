from collections import OrderedDict
def xml_2_dict(text,i=0):
    text = unicode(text)
    while i < len(text):
        #ignore empty characters
        if text[i] == '\n' or text[i] == ' ' or text[i] == '\t' or text[i] == '\r':
            i += 1
        #identify tags
        elif text[i] == '<':
            i += 1
            #ignore header info
            if text[i] == '?':
                i += 1
                while i < len(text):
                    if text[i-1] == '?' and text[i] == '>':
                        i += 1
                        break
                    i += 1
            #read in tags
            else:
                #save tag name as key
                key = u''
                while i < len(text) and text[i] != '>':
                    key += text[i]
                    i += 1
                i += 1
                #if tag is ender
                if key[0] == '/':
                    #try to send up value
                    try:
                        return term, i
                    except:
                        #try to send up lower structure
                        try:
                            return out, i
                        #if neither value or structure, then indicate an empty element
                        except:
                            return None, i
                #if tag is starter
                else:
                    #pass text after tag to the converter
                    lowerout, newi = xml_2_dict(text,i=i)
                    i = newi
                    #test if dictionary exists at the current level and create it if needed
                    try:
                        test = out                            
                    except:
                        out = OrderedDict()  
                    #add lowerout to out
                    try:    
                        test = out[key]
                        if isinstance(test, list):
                            out[key].append(lowerout)
                        else:
                            out[key] = [test]
                            out[key].append(lowerout)
                    except:
                        out[key] = lowerout
        #identify element terms
        else:
            term = u''
            #extract term string
            while i < len(text) and text[i] != '<':
                term += text[i]
                i += 1
            #break into space delimited terms
            terms = term.split(' ')          
            #try to convert to ints and floats
            term = numconvert(terms)
    return out
    
def numconvert(terms):
    test = True
    for term in terms:
        try:
            temp = int(term)
        except:
            test = False
            break
    
    if test:
        for i in xrange(len(terms)):
            terms[i] = int(terms[i])
        if len(terms) == 1:
            return terms[0]
        else:
            return terms
    
    test = True
    for term in terms:
        try:
            temp = float(term)
        except:
            test = False
            break
    
    if test:
        for i in xrange(len(terms)):
            terms[i] = float(terms[i])
        if len(terms) == 1:
            return terms[0]
        else:
            return terms

    test = True
    for term in terms:
        if term == 'true' or term == 'True' or term == 'false' or term == 'False':
            pass
        else:
            test = False
            break
    
    if test:
        for i in xrange(len(terms)):
            if terms[i] == 'true' or terms[i] == 'True':
                terms[i] = True
            elif terms[i] == 'false' or terms[i] == 'False':
                terms[i] = False
        if len(terms) == 1:
            return terms[0]
        else:
            return terms
    
    return ' '.join(terms)
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            