from collections import OrderedDict
import json
from copy import deepcopy

class DataModel:
    def __init__(self, file_name = None):
        if file_name != None:
            self.load(file_name)
        else:
            self.__data = OrderedDict()
    
    def load(self, file_name):
        if file_name[-5:] == '.json':
            with open(file_name,'r') as f:
                self.__data = json.load(f, object_pairs_hook = OrderedDict) 
                
        elif file_name[-4:] == '.xml':
            with open(file_name, 'r') as f:
                self.__data = xml_2_dict(f.read())
        
        else:
            raise ValueError('Unsupported file type for DataModel load')
    
    def dump(self, file_name):
        if file_name[-5:] == '.json':
            with open(file_name,'w') as f:
                f.write(json.dumps( self.__data, indent = 4, separators = (',',': ') ))
        
        elif file_name[-4:] == '.xml':
            with open(file_name,'w') as f:
                f.write(dict_2_xml(self.__data))
        
        else:
            raise ValueError('Unsupported file type for DataModel dump')
    
    def get(self, safe = True):
        if safe:
            return deepcopy(self.__data)
        else:
            return self.__data
            

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
    
 