# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# iprPy imports
from ...analysis import assign_currentIPR

from itertools import permutations

__all__ = ['defectmobility']

def defectmobility(database, keys, record=None, content_dict=None, query=None, **kwargs):
    
    load_key='atomic-system'
    load_style = 'relaxed_crystal'
    if 'allowable_impurity_numbers' in kwargs.keys():
        allowable_impurity_numbers = kwargs['allowable_impurity_numbers'] #Put something here that will take a kwarg defined in the beginning script which will define the types of impurity simulations that you want to run
        del kwargs['allowable_impurity_numbers']
    else:
        allowable_impurity_numbers = [0, 1]
    
    #Check to see if there is a list of impurities defined of forbidden to be simulated 
    
    if 'impurity_list' in kwargs.keys() and 'impurity_blacklist' in kwargs.keys():
        raise Exception('Cannot define both impurity_list and impurity_blacklist')
    elif 'impurity_list' in kwargs.keys():
        impurity_list = kwargs['impurity_list']
        del kwargs['impurity_list']
        impurity_blacklist = None
    elif 'impurity_blacklist' in kwargs.keys():
        impurity_blacklist = kwargs['impurity_blacklist']
        del kwargs['impurity_blacklist']
        impurity_list = None
    else:
        impurity_list = None
        impurity_blacklist = None
    
    
    if content_dict is None:
        content_dict = {}
   
    
    #Determine the number and specific of the total number of elements that can be in the system
    if 'potential_file' in keys or 'potential_content' in keys or 'potential_dir' in keys:
        include_potentials = True
        
        # Extract kwargs starting with "potential"
        potential_kwargs = {}
        for key in list(kwargs.keys()):
            if key[:10] == 'potential_':
                potential_kwargs[key[10:]] = kwargs.pop(key)

        # Pull out potential get_records parameters
        potential_record = potential_kwargs.pop('record', 'potential_LAMMPS')
        potential_query = potential_kwargs.pop('query', None)
        currentIPR = potential_kwargs.pop('currentIPR', potential_record=='potential_LAMMPS')
        
        # Fetch potential records 
        potentials, potential_df = database.get_records(style=potential_record, return_df=True,
                                                        query=potential_query, **potential_kwargs)

        # Filter by currentIPR (note that DataFrame index is unchanged)
        if currentIPR:
            assign_currentIPR(pot_df=potential_df)
            potential_df = potential_df[potential_df.currentIPR == True]

    else:
        include_potentials = False
    
    # Fetch reference records
    parents, parent_df = database.get_records(style=load_style, return_df=True,
                                              query=query, **kwargs)
    
                                               
    #Deterime the number and specific of the original symbols in the systems
    
    defectmobilities, defectmobility_df = database.get_records(style=record, return_df=True,
                                           query=query, **kwargs)

    
    
    structureList = []
    strucSymb = {}
    structPotential = {}
    potSymb = {}

    
    # Search for potential keys
    potential_file_key = None
    potential_content_key = None
    potential_family_key = None
    inputs = {}
    
   
    # Search for defect keys
    mobility_file_key = None
    mobility_content_key = None
    mobility_family_key = None

    for key in keys:
        inputs[key] = []
        if key == 'pointdefect_mobility_file':
            if mobility_file_key is None:
                mobility_file_key = key
            else:
                raise KeyError('Multiple <defect>_file keys found')
        elif key == 'pointdefect_mobility_content':
            if mobility_content_key is None:
                mobility_content_key = key
            else:
                raise KeyError('Multiple <defect>_content keys found')
        elif key == 'pointdefect_mobility_family':
            if mobility_family_key is None:
                mobility_family_key = key
            else:
                raise KeyError('Multiple <defect>_family keys found')
    
    
    if mobility_file_key is None:
        raise KeyError('No <defect>_file key found')
    if mobility_content_key is None:
        raise KeyError('No <defect>_content key found')
    if mobility_family_key is None:
        raise KeyError('No <defect>_family key found')
    
    # Gather all the information about the parent structures and point defects for use in defining simulations
    
    for i, parent_series in parent_df.iterrows():
        parent = parents[i]
        content_dict[parent.name] = parent.content
        
    for j, defectmobility_series in defectmobility_df.iterrows():    
        defectmobility = defectmobilities[j]
        content_dict[defectmobility.name] = defectmobility.content
    
    # need to figure out how to get infromation on the impurity number here
    
    inputs = {}
    for key in keys:
        inputs[key] = []
    
    # Beginning the process to generate all possible combinations of the defect_mobility calculation
    
    for i, parent_series in parent_df.iterrows():
        
        parent = parents[i]
        
        if include_potentials:
            try:
                potential_id = parent_series.potential_LAMMPS_id
            except:
                # Search grandparents for name of potential
                potential_id = None
                for grandparent in database.get_parent_records(record=parent):
                    try:
                        potential_id = grandparent.todict(full=False, flat=True)['potential_LAMMPS_id']
                    except:
                        pass
                    else:
                        break
                if potential_id is None:
                    raise ValueError('potential info not found')
            try:
                potential_series = potential_df[potential_df.id == potential_id].iloc[0]
            except:
                continue
            
            potential = potentials[potential_series.name]
            content_dict[potential.name] = potential.content

        # Determine number of systems in parent to iterate over
        if parent_series.status == 'not calculated':
            nparents = 1
        elif parent_series.status == 'error':
            nparents = 0
        elif parent_series.status == 'finished':
            if 'load_options' in keys:
                nparents = len(parent.content.finds(load_key))
            else:
                nparents = 1
        else:
            raise ValueError('Unsupported record status')
        
        #Going through the structure and gathering all the symbol information to be used for defining allSymbols for defect mobility
        
        pureStructureElements = []
        
        #Getting the information on the elements used in the base structure for the simulation 
        
        if isinstance(content_dict[parent.name]['relaxed-crystal']['atomic-system']['atom-type-symbol'],str):
            pureStructureElements = [content_dict[parent.name]['relaxed-crystal']['atomic-system']['atom-type-symbol']]
        else:
            pureStructureElements = content_dict[parent.name]['relaxed-crystal']['atomic-system']['atom-type-symbol']
        
        #Determining the number of elements used in the base element structure
        
        numberPureElements = len(pureStructureElements)
        
        #Defining all the elements defined in the potential and that could be used in the system
        
        potentialElementList = []
        
        for elements in content_dict[potential.name]['potential-LAMMPS']['atom']:
            potentialElementList.append(elements['element'])
        
        #Finding the number of elements which can be used
        
        totalPotentialElementNum = len(potentialElementList)
        
        # Generating the beginning of the allSymbols string which will be added to the input file
        
        allSymbolsBase = ''
        
        for elements in pureStructureElements:
            if allSymbolsBase == '':
                allSymbolsBase = allSymbolsBase + elements 
            else: 
                allSymbolsBase = allSymbolsBase +' '+ elements
        
        # Generating a list of possible impurity elements for the structure, removing any elements in the pure structure, any elements
        # not in impurity_list, or any elements in impurity_blacklist
        
        potentialImpurityElements = potentialElementList
        
        for elements in pureStructureElements:
            potentialImpurityElements.remove(elements)
        
        if impurity_list is not None:
            for elements in potentialImpurityElements:
                if elements not in impurity_list:
                    potentialImpurityElements.remove(elements)
        
        if impurity_blacklist is not None:
            for elements in potentialImpurityElements:
                if elements in impurity_blacklist:
                    potentialImpurityElements.remove(elements)
        
        # Determining the number of possible ImpurityElements which can be used, and generating a list of indexes
        # which can be used to generate all the possible permutations for each defect mobility calculation
        
        potentialImpurityNumber = len(potentialImpurityElements)
        impIndexes = []
        for number in range(potentialImpurityNumber):
            impIndexes.append(number)
        
        
        for j in range(nparents):
            
            # Iterating over all the possible point defects for the structure
            
            for k, defectmobility_series in defectmobility_df.iterrows():
                
                defectmobility = defectmobilities[k]
                
                numberTotalElements = numberPureElements
                
                # identifying the number of impurities used in the defect calculation
                
                for tag in content_dict[defectmobility.name]['point-defect-mobility']:
                    if tag[-22:] == 'calculation-parameters':
                        for tag2 in content_dict[defectmobility.name]['point-defect-mobility'][tag]:
                            if isinstance(tag2,str):
                                if tag2 == 'atype':
                                    if content_dict[defectmobility.name]['point-defect-mobility'][tag][tag2] > numberTotalElements:
                                        numberTotalElements = content_dict[defectmobility.name]['point-defect-mobility'][tag][tag2]

                            else:
                                for tag3 in tag2:
                                    if tag3 == 'atype':
                                        if tag2[tag3] > numberTotalElements:
                                            numberTotalElements = tag2[tag3]
                
                numberImpurities = numberTotalElements - numberPureElements
                
                #Going through the process of actually generating the possible element combinations used for defect_mobility simulations
                
                if totalPotentialElementNum >= numberTotalElements: #Determining if the potential has enough elements to run the selected
                                                                    #defect mobility simulation
                    if numberImpurities in allowable_impurity_numbers: #Determining if the number if impurities is on the list of allowed impurities
                        if numberImpurities > 0: #Determining if there are actually any impurities in the simulation - if yes, the script generates all possible permutations of the allowed symbols for the simulation, otherwise it moves onto giving the pure simulation 
                            indexPerm = permutations(impIndexes, numberImpurities) #Generates all possible permutations of the impurityindexes, which are used to call the actual impurities, given the selection of the correct number of impurities
                            for perm in indexPerm:
                                allSymbols = allSymbolsBase
                                for indexThing in perm:
                                    allSymbols = allSymbols +' '+ potentialImpurityElements[indexThing]
                                for key in keys:
                                    if key == 'potential_file':
                                        inputs['potential_file'].append(f'{potential.name}.json')
                                    elif key == 'potential_content':
                                        inputs['potential_content'].append(f'record {potential.name}')
                                    elif key == 'potential_dir':
                                        inputs['potential_dir'].append(potential.name)
                                    elif key == 'potential_dir_content':
                                        inputs['potential_dir_content'].append(f'tar {potential.name}')
                                    elif key == 'load_file':
                                        inputs['load_file'].append(f'{parent.name}.json')
                                    elif key == 'load_content':
                                        inputs['load_content'].append(f'record {parent.name}')
                                    elif key == 'load_style':
                                        inputs['load_style'].append('system_model')
                                    elif key == 'load_options':
                                        if j == 0:
                                            inputs['load_options'].append(f'key {load_key}')
                                        else:
                                            inputs['load_options'].append(f'key {load_key} index {j}')
                                    elif key == 'family':
                                        inputs['family'].append(parent_series.family)
                                    elif key == 'elasticconstants_file':
                                        inputs['elasticconstants_file'].append(f'{parent.name}.json')
                                    elif key == 'elasticconstants_content':
                                        inputs['elasticconstants_content'].append(f'record {parent.name}')
                                    elif key == 'allSymbols':
                                        inputs['allSymbols'].append(allSymbols)
                                    elif key == mobility_file_key:
                                        inputs[key].append(f'{defectmobility.name}.json')
                                    elif key == mobility_content_key:
                                        inputs[key].append(f'record {defectmobility.name}')
                                    elif key == mobility_family_key:
                                        inputs[key].append(defectmobility_series.family)
                                    else:
                                        inputs[key].append('')
                                
                        else:
                            allSymbols = allSymbolsBase
                            for key in keys:
                                if key == 'potential_file':
                                    inputs['potential_file'].append(f'{potential.name}.json')
                                elif key == 'potential_content':
                                    inputs['potential_content'].append(f'record {potential.name}')
                                elif key == 'potential_dir':
                                    inputs['potential_dir'].append(potential.name)
                                elif key == 'potential_dir_content':
                                    inputs['potential_dir_content'].append(f'tar {potential.name}')
                                elif key == 'load_file':
                                    inputs['load_file'].append(f'{parent.name}.json')
                                elif key == 'load_content':
                                    inputs['load_content'].append(f'record {parent.name}')
                                elif key == 'load_style':
                                    inputs['load_style'].append('system_model')
                                elif key == 'load_options':
                                    if j == 0:
                                        inputs['load_options'].append(f'key {load_key}')
                                    else:
                                        inputs['load_options'].append(f'key {load_key} index {j}')
                                elif key == 'family':
                                    inputs['family'].append(parent_series.family)
                                elif key == 'elasticconstants_file':
                                    inputs['elasticconstants_file'].append(f'{parent.name}.json')
                                elif key == 'elasticconstants_content':
                                    inputs['elasticconstants_content'].append(f'record {parent.name}')
                                elif key == 'allSymbols':
                                    inputs['allSymbols'].append(allSymbols)
                                elif key == mobility_file_key:
                                    inputs[key].append(f'{defectmobility.name}.json')
                                elif key == mobility_content_key:
                                    inputs[key].append(f'record {defectmobility.name}')
                                elif key == mobility_family_key:
                                    inputs[key].append(defectmobility_series.family)
                                else:
                                    inputs[key].append('')
                                    
    return inputs, content_dict