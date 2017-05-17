from DataModelDict import DataModelDict as DM

def todict(record, full=True):

    model = DM(record)

    proto = model['crystal-prototype']
    params = {}
    params['key'] =             proto['key']
    params['id'] =              proto['id']
    params['name'] =            proto['name']
    params['prototype'] =       proto['prototype']
    params['Pearson_symbol'] =  proto['Pearson-symbol']
    params['Strukturbericht'] = proto['Strukturbericht']
    
    params['sg_number'] =       proto['space-group']['number']
    params['sg_HG'] =           proto['space-group']['Hermann-Maguin']
    params['sg_Schoen'] =       proto['space-group']['Schoenflies']
    
    cell = proto['atomic-system']['cell']
    params['crystal_family'] =  cell.keys()[0]
    params['a'] =               cell.find('a')['value']
    try:    params['b'] =       cell.find('b')['value']
    except: params['b'] =       params['a']
    try:    params['c'] =       cell.find('c')['value']
    except: params['c'] =       params['a']
    params['natypes'] =         max(proto['atomic-system'].finds('component'))   
    
    return params 