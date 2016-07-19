from iprPy.tools import term_extractor

def description():
    """Returns a description for the prepare_function."""
    return "The all_elements_list prepare_function saves all element tags to the single-valued 'v_name'. If 'v_name' is not given as either a inline term or a pre-defined variable, then the list is saved to variable 'all_elements'."
    
def keywords():
    """Return the list of keywords used by this prepare_function that are searched for from the inline terms and pre-defined variables."""
    return ['v_name']

def prepare(terms, variables):
    """Assign all element names to a variable named by the prepare line terms."""
    
    #Build the prepare_function's variable dictionary, v, from inline terms and pre-defined dictionary of variables
    v = term_extractor(terms, variables, keywords())
    
    key = v.get('v_name', 'all_elements')
    assert not isinstance(key, list), 'v_name must be single-valued'
    
    variables[key] = [ 'H',                                                                                                 'He', 
                      'Li', 'Be',                                                              'B',  'C',  'N',  'O',  'F', 'Ne', 
                      'Na', 'Mg',                                                             'Al', 'Si',  'P',  'S', 'Cl', 'Ar', 
                       'K', 'Ca', 'Sc', 'Ti',  'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 
                      'Rb', 'Sr',  'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te',  'I', 'Xe', 
                      'Cs', 'Ba',       'Hf', 'Ta',  'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 
                      'Fr', 'Ra',       'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn','Uut', 'Fl','Uup', 'Lv','Uus','Uuo',
                              'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 
                              'Ac', 'Th', 'Pa',  'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr']