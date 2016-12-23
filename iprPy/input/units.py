def units(input_dict, **kwargs):
    """
    Handles input parameters associated with the input/output units.
    1. Sets default value of 'angstrom' to 'length_unit' term if needed.
    2. Sets default value of 'eV' to 'energy_unit' term if needed.
    3. Sets default value of 'GPa' to 'pressure_unit' term if needed.
    4. Sets default value of 'eV/angstrom' to 'force_unit' term if needed.
    
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    length_unit -- replacement parameter key name for 'length_unit'
    energy_unit -- replacement parameter key name for 'energy_unit'
    pressure_unit -- replacement parameter key name for 'pressure_unit'
    force_unit -- replacement parameter key name for 'force_unit'
    """
    
    #Set default keynames
    keynames = ['length_unit', 'energy_unit', 'pressure_unit', 'force_unit']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    #Set default unit styles to any terms not given
    input_dict[kwargs['length_unit']] =   input_dict.get(kwargs['length_unit'],   'angstrom')
    input_dict[kwargs['energy_unit']] =   input_dict.get(kwargs['energy_unit'],   'eV')
    input_dict[kwargs['pressure_unit']] = input_dict.get(kwargs['pressure_unit'], 'GPa')
    input_dict[kwargs['force_unit']] =    input_dict.get(kwargs['force_unit'],    'eV/angstrom')