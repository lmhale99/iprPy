from DataModelDict import DataModelDict as DM
import numpy as np

def assign_composition(calc_df, database):
    """
    Identifies crystal prototype compositions.
    """
    prototypes = database.get_records(style='crystal_prototype')
    # Build counts for each prototype
    counts = {}
    for prototype in prototypes:
        counts[prototype.name] = np.unique(prototype.content.finds('component'), return_counts=True)[1]
    
    # Identify compositions
    compositions = []
    for calc in calc_df.itertuples():
        compositions.append(composition(calc.symbols, counts[calc.family]))
    calc_df['composition'] = compositions
    #calc_df = calc_df.assign(composition=compositions)

def composition(symbols, counts):
    """
    Generates a composition string for a unit cell.
    
    Parameters
    ----------
    symbols : list
        All element model symbols.
    count : list
        How many unique sites are occupied by each symbol.
    
    Returns
    -------
    str
        The composition string.
    """
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]
    
    sym_dict = {}
    for i in range(len(symbols)):
        sym_dict[symbols[i]] = counts[i]
    
    for prime in primes:
        if max(sym_dict.values()) < prime:
            break
        
        while True:
            breaktime = False
            for value in sym_dict.values():
                if value % prime != 0:
                    breaktime = True
                    break
            if breaktime:
                break
            for key in sym_dict:
                sym_dict[key] /= prime
    
    composition_str =''
    for key in sorted(sym_dict):
        if sym_dict[key] > 0:
            composition_str += key
            if sym_dict[key] != 1:
                composition_str += str(int(sym_dict[key]))
    
    return composition_str