def units(input_dict):
    """
    Process input terms that define calculation input/output units
    """
    input_dict['length_unit'] =   input_dict.get('length_unit',   'angstrom')
    input_dict['energy_unit'] =   input_dict.get('energy_unit',   'eV')
    input_dict['pressure_unit'] = input_dict.get('pressure_unit', 'GPa')
    input_dict['force_unit'] =    input_dict.get('force_unit',    'eV/angstrom')