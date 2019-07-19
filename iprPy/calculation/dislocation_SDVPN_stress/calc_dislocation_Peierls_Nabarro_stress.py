#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
from collections import OrderedDict
import os
import sys
import uuid

# http://www.numpy.org/
import numpy as np

# http://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.defect import SDVPN

# https://github.com/usnistgov/iprPy
import iprPy
from iprPy.compatibility import range

# Define calc_style and record_style
calc_style = 'dislocation_Peierls_Nabarro_stress'
record_style = 'calculation_dislocation_Peierls_Nabarro_stress'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    results_dict = peierlsnabarrostress(input_dict['peierlsnabarro'],
                                        input_dict['delta_tau'],
                                        tausteps=input_dict['tausteps'],
                                        cdiffstress=input_dict['cdiffstress'],
                                        fullstress=input_dict['fullstress'],
                                        min_method=input_dict['minimize_style'],
                                        min_options=input_dict['minimize_options'])
    
    # Save data model of results
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict,
                               results_dict)
    
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def peierlsnabarrostress(pnsolution, delta_tau, tausteps=1,
                         cdiffstress=False, fullstress=True,
                         min_method='Powell', min_options={}):
    """
    Applies stress to a semi-discrete Peierls-Nabarro solution.
    """
    total_energies = []
    tau_xys = []
    tau_yys = []
    tau_yzs = []
    
    # Loop over stress states
    for i in range(0, tausteps+1):
        tau = i * delta_tau
        pnsolution.solve(tau=tau, cdiffstress=cdiffstress,
                         fullstress=fullstress,
                         min_method=min_method, min_options=min_options)
        sys.stdout.flush()
        
        # Save values
        total_energies.append(pnsolution.total_energy())
        tau_xys.append(tau[1,0])
        tau_yys.append(tau[1,1])
        tau_yzs.append(tau[1,2])
        
        # Save solution to file
        model = pnsolution.model()
        with open(os.path.join(str(i)+'.json'), 'w') as f:
            model.json(fp=f)
    
    # Initialize results dict
    results_dict = {}
    results_dict['total_energy'] = total_energies
    results_dict['tau_xy'] = tau_xys
    results_dict['tau_yy'] = tau_yys
    results_dict['tau_yz'] = tau_yzs
    
    return results_dict

def process_input(input_dict, UUID=None, build=True):
    """
    Processes str input parameters, assigns default values if needed, and
    generates new, more complex terms as used by the calculation.
    
    Parameters
    ----------
    input_dict :  dict
        Dictionary containing the calculation input parameters with string
        values.  The allowed keys depends on the calculation style.
    UUID : str, optional
        Unique identifier to use for the calculation instance.  If not 
        given and a 'UUID' key is not in input_dict, then a random UUID4 
        hash tag will be assigned.
    build : bool, optional
        Indicates if all complex terms are to be built.  A value of False
        allows for default values to be assigned even if some inputs 
        required by the calculation are incomplete.  (Default is True.)
    """
    
    # Set calculation UUID
    if UUID is not None: 
        input_dict['calc_key'] = UUID
    else: 
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.units(input_dict)
    
    # These are calculation-specific default strings
    input_dict['minimize_style'] = input_dict.get('minimize_style', 'Powell')
    input_dict['minimize_options'] = input_dict.get('minimize_options', '')
    
    # These are calculation-specific default booleans
    input_dict['cdiffstress'] = iprPy.input.boolean(input_dict.get('cdiffstress',
                                                                   False))
    input_dict['fullstress'] = iprPy.input.boolean(input_dict.get('fullstress',
                                                                  True))
    
    # These are calculation-specific default integers
    input_dict['tausteps'] = int(input_dict.get('tausteps', 1))
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    input_dict['delta_tau_xy'] = iprPy.input.value(input_dict, 'delta_tau_xy',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    input_dict['delta_tau_yy'] = iprPy.input.value(input_dict, 'delta_tau_yy',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    input_dict['delta_tau_yz'] = iprPy.input.value(input_dict, 'delta_tau_yz',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    
    # Process delta_tau
    txy = input_dict['delta_tau_xy']
    tyy = input_dict['delta_tau_yy']
    tyz = input_dict['delta_tau_yz']
    input_dict['delta_tau'] = np.array([[0.0, txy, 0.0],
                                        [txy, tyy, tyz],
                                        [0.0, tyz, 0.0]])
    
    # Process minimize_options
    boolkeys = ['disp']
    intkeys = ['maxiter', 'maxfev']
    floatkeys = ['xatol', 'fatol', 'xtol', 'ftol', 'gtol', 'norm', 'eps']
    keys = boolkeys + intkeys + floatkeys
    min_options = iprPy.tools.termtodict(input_dict['minimize_options'], keys)
    for boolkey in boolkeys:
        if boolkey in min_options:
            min_options[boolkey] = iprPy.input.boolean(min_options[boolkey])
    for intkey in intkeys:
        if intkey in min_options:
            min_options[intkey] = int(min_options[intkey])
    for floatkey in floatkeys:
        if floatkey in min_options:
            min_options[floatkey] = float(min_options[floatkey])
    input_dict['minimize_options'] = min_options
    
    # Load ucell system
    iprPy.input.systemload(input_dict, build=build)
    
    # Load dislocation parameters
    iprPy.input.dislocationmonopole(input_dict)
    
    # Load system manipulate to process parameters without building
    iprPy.input.systemmanipulate(input_dict, build=False)
    
    # Load gamma surface
    iprPy.input.gammasurface(input_dict, build=build)
    
    # Load Peierls-Nabarro solution
    iprPy.input.peierlsnabarro(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])