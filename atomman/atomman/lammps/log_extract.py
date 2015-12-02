#Take LAMMPS screen output and parse out the thermo data into a list
def log_extract(output):
    thermo = False
    first = True
    thermolist = []
    
    lines = output.split('\n')
    for line in lines:
        terms = line.split()
        
        #If the line has terms
        if len(terms)>0:
            #If the line starts with Step, then set thermo
            if terms[0] == 'Step':
                thermo = True
                #Make the first line of the returned array the thermo data headers
                if first:
                    thermolist.append(terms)
                    first = False
                    
            #If thermo has been set, the lines probably contain data
            elif thermo:
                #Check that the first term is an integer
                if terms[0].isdigit():
                    thermolist.append(terms)                   
                else:
                    thermo = False                    

    return thermolist     