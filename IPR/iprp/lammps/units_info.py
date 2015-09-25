def get_units(units):
    if units == 'lj':
         unit_dict = {"mass":            "m",
                     "distance":         "sigma",
                     "time":             "tau",
                     "energy":           "epsilon",
                     "velocity":         "sigma/tau",
                     "force":            "epsilon/sigma",
                     "torque":           "epsilon",
                     "temperature":      "reduced LJ temperature",
                     "pressure":         "reduced LJ pressure",
                     "dynamic viscosity":"reduced LJ viscosity",
                     "charge":           "reduced LJ charge",
                     "dipole":           "reduced LJ dipole",
                     "electric field":   "force/charge",
                     "density":          "m/volume"}
    elif units == 'real':
        unit_dict = {"mass":             "grams/mole", 
                     "distance":         "Angstroms", 
                     "time":             "femtoseconds", 
                     "energy":           "Kcal/mole", 
                     "velocity":         "Angstroms/femtosecond", 
                     "force":            "Kcal/mole-Angstrom",
                     "torque":           "Kcal/mole",
                     "temperature":      "Kelvin",
                     "pressure":         "atmospheres",
                     "dynamic viscosity":"Poise",
                     "charge":           "electron charge",
                     "dipole":           "charge*Angstroms",
                     "electric field":   "volts/Angstrom",
                     "density":          "gram/cm^dim"} 
    elif units == 'metal':
        unit_dict = {"mass":             "grams/mole", 
                     "distance":         "Angstroms", 
                     "time":             "picoseconds", 
                     "energy":           "eV", 
                     "velocity":         "Angstroms/picosecond", 
                     "force":            "eV/Angstrom",
                     "torque":           "eV",
                     "temperature":      "Kelvin",
                     "pressure":         "bars",
                     "dynamic viscosity":"Poise",
                     "charge":           "electron charge",
                     "dipole":           "charge*Angstroms",
                     "electric field":   "volts/Angstrom",
                     "density":          "gram/cm^dim"}
    elif units == 'si':
        unit_dict = {"mass":             "kilograms",
                     "distance":         "meters",
                     "time":             "seconds",
                     "energy":           "Joules",
                     "velocity":         "meters/second",
                     "force":            "Newtons",
                     "torque":           "Newton-meters",
                     "temperature":      "Kelvin",
                     "pressure":         "Pascals",
                     "dynamic viscosity":"Pascal*second",
                     "charge":           "Coulombs",
                     "dipole":           "Coulombs*meters",
                     "electric field":   "volts/meter",
                     "density":          "kilograms/meter^dim"}
    elif units == 'cgs':
        unit_dict = {"mass":             "grams",
                     "distance":         "centimeters",
                     "time":             "seconds",
                     "energy":           "ergs",
                     "velocity":         "centimeters/second",
                     "force":            "dynes",
                     "torque":           "dyne-centimeters",
                     "temperature":      "Kelvin",
                     "pressure":         "barye",
                     "dynamic viscosity":"Poise",
                     "charge":           "statcoulombs",
                     "dipole":           "statcoulomb-centimeters",
                     "electric field":   "statvolt/centimeter",
                     "density":          "grams/centimeter^dim"}
    elif units == 'electron':
        unit_dict = {"mass":             "atomic mass units",
                     "distance":         "Bohr",
                     "time":             "femtoseconds",
                     "energy":           "Hartrees",
                     "velocity":         "Bohr/atomic time units",
                     "force":            "Hartrees/Bohr",
                     "torque":           "dyne-centimeters",
                     "temperature":      "Kelvin",
                     "pressure":         "Pascals",
                     "charge":           "electron charge",
                     "dipole moment":    "Debye",
                     "electric field":   "volts/cm"}
    elif units == 'micro':
        unit_dict = {"mass":             "picograms",
                     "distance":         "micrometers",
                     "time":             "microseconds",
                     "energy":           "picogram-micrometer^2/microsecond^2",
                     "velocity":         "micrometers/microsecond",
                     "force":            "picogram-micrometer/microsecond^2",
                     "torque":           "picogram-micrometer^2/microsecond^2",
                     "temperature":      "Kelvin",
                     "pressure":         "picogram/(micrometer-microsecond^2)",
                     "dynamic viscosity":"picogram/(micrometer-microsecond)",
                     "charge":           "picocoulombs",
                     "dipole":           "picocoulomb-micrometer",
                     "electric field":   "volt/micrometer",
                     "density":          "picograms/micrometer^dim"}

    elif units == 'nano':
        unit_dict = {"mass":             "attograms",
                     "distance":         "nanometers",
                     "time":             "nanoseconds",
                     "energy":           "attogram-nanometer^2/nanosecond^2",
                     "velocity":         "nanometers/nanosecond",
                     "force":            "attogram-nanometer/nanosecond^2",
                     "torque":           "attogram-nanometer^2/nanosecond^2",
                     "temperature":      "Kelvin",
                     "pressure":         "attogram/(nanometer-nanosecond^2)",
                     "dynamic viscosity":"attogram/(nanometer-nanosecond)",
                     "charge":           "electron charge",
                     "dipole":           "charge-nanometer",
                     "electric field":   "volt/nanometer",
                     "density":          "attograms/nanometer^dim"}                 
    else:
        raise ValueError('Unknown LAMMPS unit style')
    return unit_dict

def get_timestep_size(units):
    if units == 'lj':
        dt = [0.005, "tau"]
    elif units == 'real':
        dt = [1.0, "femtosecond"]
    elif units == 'metal':
        dt = [0.001, "picosecond"]
    elif units == 'si':
        dt = [1.0e-8, "second"]
    elif units == 'cgs':
        dt = [1.0e-8, "second"]
    elif units == 'electron':
        dt = [0.001, "femtosecond"]
    elif units == 'micro':
        dt = [2.0, "microsecond"]
    elif units == 'nano':
        dt = [0.00045, "nanosecond"] 
    return dt