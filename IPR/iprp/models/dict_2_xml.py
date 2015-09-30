def dict_2_xml(lib,spaces='',out=''):
    #evaluate each key, value pair for the dictionary
    for k,v in lib.iteritems():
        
        #if the value is another dictionary, add spaces and run recursively
        if isinstance(v, dict):
            out += '%s<%s>\n'%(spaces,k)
            out = dict_2_xml(v,spaces=spaces+'    ',out=out)
            out += '%s</%s>\n'%(spaces,k)
        
        #if the value is a list
        elif isinstance(v, list):
            
            #if all terms are numbers, then print with space delimiters
            if all(isinstance(i, (int,float)) for i in v):                    
                out += '%s<%s>%s</%s>\n'%(spaces,k,' '.join(map(str,v)).lower(),k)
            #if not all numers, each term is added with the same key
            else:
                #investigate each term in list
                for value in v:
                    #if term is a dictionary, add spaces and run recursively
                    if isinstance(value, dict):
                        out += '%s<%s>\n'%(spaces,k)
                        out = dict_2_xml(value,spaces=spaces+'    ',out=out)
                        out += '%s</%s>\n'%(spaces,k)
                    #if not a dictionary, add as a string
                    elif isinstance(value, (str, unicode)):
                        out += '%s<%s>%s</%s>\n'%(spaces,k,value,k)
        
        #if the value is a string
        elif isinstance(v, (str, unicode)):
            out += '%s<%s>%s</%s>\n'%(spaces,k,v,k)
        #if the value is None, add empty element
        elif v is None:
            out += '%s<%s></%s>\n'%(spaces,k,k)
        #for everything else, convert to a string
        else:
            out += '%s<%s>%s</%s>\n'%(spaces,k,str(v).lower(),k)
    return out