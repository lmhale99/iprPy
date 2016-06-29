from DataModelDict import DataModelDict as DM

def file_to_dict(infile):
    input_dict = DM()
    
    #Convert input file values into dictionary key-value pairs
    for line in infile:
        terms = line.split()
        if len(terms) > 1 and terms[0][0] != '#':
            if terms[0] in input_dict:
                raise ValueError(terms[0] + ' already listed')
            else:
                input_dict[terms[0]] = ' '.join(terms[1:])
                
    return input_dict