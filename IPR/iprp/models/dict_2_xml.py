def dict_2_xml(lib,spaces='',out=''):
    for k,v in lib.iteritems():
        if isinstance(v, dict):
            out += '%s<%s>\n'%(spaces,k)
            out = dict_2_xml(v,spaces=spaces+'    ',out=out)
            out += '%s</%s>\n'%(spaces,k)
        elif isinstance(v, list):
            if all(isinstance(i, (int,float)) for i in v):                    
                out += '%s<%s>%s</%s>\n'%(spaces,k,' '.join(map(str,v)).lower(),k)
            else:
                for value in v:
                    if isinstance(value, dict):
                        out += '%s<%s>\n'%(spaces,k)
                        out = dict_2_xml(value,spaces=spaces+'    ',out=out)
                        out += '%s</%s>\n'%(spaces,k)
                    elif isinstance(value, (str, unicode)):
                        out += '%s<%s>%s</%s>\n'%(spaces,k,value,k)
        elif isinstance(v, (str, unicode)):
            out += '%s<%s>%s</%s>\n'%(spaces,k,v,k)
        else:
            out += '%s<%s>%s</%s>\n'%(spaces,k,str(v).lower(),k)
    return out