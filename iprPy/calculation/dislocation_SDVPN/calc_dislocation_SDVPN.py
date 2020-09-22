#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard Python libraries
from pathlib import Path
import sys
import uuid

# http://www.numpy.org/
import numpy as np

# http://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define record_style
record_style = 'calculation_dislocation_SDVPN'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    results_dict = peierlsnabarro(input_dict['ucell'],
                                  input_dict['C'],
                                  input_dict['dislocation_burgers'],
                                  input_dict['dislocation_ξ_uvw'],
                                  input_dict['dislocation_slip_hkl'],
                                  input_dict['gamma'],
                                  m = input_dict['dislocation_m'],
                                  n = input_dict['dislocation_n'],
                                  cutofflongrange=input_dict['cutofflongrange'],
                                  tau=input_dict['tau'],
                                  alpha=input_dict['alpha'],
                                  beta=input_dict['beta'],
                                  cdiffelastic=input_dict['cdiffelastic'],
                                  cdiffsurface=input_dict['cdiffsurface'],
                                  cdiffstress=input_dict['cdiffstress'],
                                  fullstress=input_dict['fullstress'],
                                  halfwidth=input_dict['halfwidth'],
                                  normalizedisreg=input_dict['normalizedisreg'],
                                  xnum=input_dict['xnum'],
                                  xstep=input_dict['xstep'],
                                  xmax=input_dict['xmax'],
                                  min_method=input_dict['minimize_style'],
                                  min_options=input_dict['minimize_options'],
                                  min_cycles=input_dict['minimize_cycles'])
    
    # Save data model of results
    script = Path(__file__).stem
    
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def peierlsnabarro(ucell, C, burgers, ξ_uvw, slip_hkl, gamma,
                   m=[0,1,0], n=[0,0,1],
                   cutofflongrange=uc.set_in_units(1000, 'angstrom'),
                   tau=np.zeros((3,3)), alpha=[0.0], beta=np.zeros((3,3)),
                   cdiffelastic=False, cdiffsurface=True, cdiffstress=False,
                   fullstress=True,
                   halfwidth=uc.set_in_units(1, 'angstrom'),
                   normalizedisreg=True,
                   xnum=None, xmax=None, xstep=None, xscale=False,
                   min_method='Powell', min_options={}, min_cycles=10):
    """
    Solves a Peierls-Nabarro dislocation model.

    Parameters
    ----------
    ucell : atomman.System
        The unit cell to use as the seed for the dislocation system.  Note that
        only box information is used and not atomic positions.
    C : atomman.ElasticConstants
        The elastic constants associated with the bulk crystal structure
        for ucell.
    burgers : array-like object
        The dislocation's Burgers vector given as a Miller or
        Miller-Bravais vector relative to ucell.
    ξ_uvw : array-like object
        The dislocation's line direction given as a Miller or
        Miller-Bravais vector relative to ucell.
    slip_hkl : array-like object
        The dislocation's slip plane given as a Miller or Miller-Bravais
        plane relative to ucell.
    m : array-like object, optional
        The m unit vector for the dislocation solution.  m, n, and ξ
        (dislocation line) should be right-hand orthogonal.  Default value
        is [0,1,0] (y-axis).
    n : array-like object, optional
        The n unit vector for the dislocation solution.  m, n, and ξ
        (dislocation line) should be right-hand orthogonal.  Default value
        is [0,0,1] (z-axis). n is normal to the dislocation slip plane.
    cutofflongrange : float, optional
        The cutoff distance to use for computing the long-range energy.
        Default value is 1000 angstroms.
    tau : numpy.ndarray, optional
        A (3,3) array giving the stress tensor to apply to the system
        using the stress energy term.  Only the xy, yy, and yz components
        are used.  Default value is all zeros.
    alpha : list of float, optional
        The alpha coefficient(s) used by the nonlocal energy term.  Default
        value is [0.0].
    beta : numpy.ndarray, optional
        The (3,3) array of beta coefficient(s) used by the surface energy
        term.  Default value is all zeros.
    cdiffelastic : bool, optional
        Flag indicating if the dislocation density for the elastic energy
        component is computed with central difference (True) or simply
        neighboring values (False).  Default value is False.
    cdiffsurface : bool, optional
        Flag indicating if the dislocation density for the surface energy
        component is computed with central difference (True) or simply
        neighboring values (False).  Default value is True.
    cdiffstress : bool, optional
        Flag indicating if the dislocation density for the stress energy
        component is computed with central difference (True) or simply
        neighboring values (False).  Only matters if fullstress is True.
        Default value is False.
    fullstress : bool, optional
        Flag indicating which stress energy algorithm to use.  Default
        value is True.
    halfwidth : float, optional
        A dislocation halfwidth guess to use for generating the initial
        disregistry guess.  Does not have to be accurate, but the better the
        guess the fewer minimization steps will likely be needed.  Default
        value is 1 Angstrom.
    normalizedisreg : bool, optional
        If True, the initial disregistry guess will be scaled such that it
        will have a value of 0 at the minimum x and a value of burgers at the
        maximum x.  Default value is True.  Note: the disregistry of end points
        are fixed, thus True is usually preferential.
    xnum :  int, optional
        The number of x value points to use for the solution.  Two of xnum,
        xmax, and xstep must be given.
    xmax : float, optional
        The maximum value of x to use.  Note that the minimum x value will be
        -xmax, thus the range of x will be twice xmax.  Two of xnum, xmax, and
        xstep must be given.
    xstep : float, optional
        The delta x value to use, i.e. the step size between the x values used.
        Two of xnum, xmax, and xstep must be given.
    xscale : bool, optional
        Flag indicating if xmax and/or xstep values are to be taken as absolute
        or relative to ucell's a lattice parameter.  Default value is False,
        i.e. the x parameters are absolute and not scaled.
    min_method : str, optional
        The scipy.optimize.minimize method to use.  Default value is
        'Powell'.
    min_options : dict, optional
        Any options to pass on to scipy.optimize.minimize. Default value
        is {}.
    min_cycles : int, optional
        The number of minimization runs to perform on the system.  Restarting
        after obtaining a solution can help further refine to the best pathway.
        Default value is 10. 
    """

    # Solve Volterra dislocation
    volterra = am.defect.solve_volterra_dislocation(C, burgers, ξ_uvw=ξ_uvw,
                                                    slip_hkl=slip_hkl, box=ucell.box,
                                                    m=m, n=n)
    
    # Generate SDVPN object
    pnsolution = am.defect.SDVPN(volterra=volterra, gamma=gamma,
                                 tau=tau, alpha=alpha, beta=beta,
                                 cutofflongrange=cutofflongrange,
                                 fullstress=fullstress, cdiffelastic=cdiffelastic,
                                 cdiffsurface=cdiffsurface, cdiffstress=cdiffstress,
                                 min_method=min_method, min_options=min_options)

    # Scale xmax and xstep by alat
    if xscale is True:
        if xmax is not None:
            xmax *= ucell.box.a
        if xstep is not None:
            xstep *= ucell.box.a
    
    # Generate initial disregistry guess
    x, idisreg = am.defect.pn_arctan_disregistry(xmax=xmax, xstep=xstep, xnum=xnum,
                                                 burgers=pnsolution.burgers,
                                                 halfwidth=halfwidth,
                                                 normalize=normalizedisreg)
    
    # Set up loop parameters
    cycle = 0
    disregistries = [idisreg]
    minimization_energies = [pnsolution.total_energy(x, idisreg)]
    
    # Run minimization for min_cycles
    pnsolution.x = x
    pnsolution.disregistry = idisreg
    while cycle < min_cycles:
        cycle += 1
        pnsolution.solve()
        disregistries.append(pnsolution.disregistry)
        minimization_energies.append(pnsolution.total_energy())

    # Initialize results dict
    results_dict = {}
    results_dict['SDVPN_solution'] = pnsolution
    results_dict['minimization_energies'] = minimization_energies
    results_dict['disregistry_profiles'] = disregistries
    
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
    iprPy.input.subset('units').interpret(input_dict)
    pl_unit = input_dict['pressure_unit']+'*'+input_dict['length_unit']
    p_per_l_unit = input_dict['pressure_unit']+'/'+input_dict['length_unit']
    
    # These are calculation-specific default strings
    input_dict['alpha'] = input_dict.get('alpha', '0.0')
    input_dict['minimize_style'] = input_dict.get('minimize_style', 'Powell')
    input_dict['minimize_options'] = input_dict.get('minimize_options', '')
    
    # These are calculation-specific default booleans
    input_dict['cdiffelastic'] = iprPy.input.boolean(input_dict.get('cdiffelastic', False))
    input_dict['cdiffsurface'] = iprPy.input.boolean(input_dict.get('cdiffsurface', True))
    input_dict['cdiffstress'] = iprPy.input.boolean(input_dict.get('cdiffstress', False))
    input_dict['fullstress'] = iprPy.input.boolean(input_dict.get('fullstress', True))
    input_dict['normalizedisreg'] = iprPy.input.boolean(input_dict.get('normalizedisreg',
                                                                       True))

    # These are calculation-specific default integers
    input_dict['xnum'] = int(input_dict.get('xnum', 0))
    input_dict['minimize_cycles'] = int(input_dict.get('minimize_cycles', 10))
    
    # These are calculation-specific default unitless floats
    input_dict['xstep'] = float(input_dict.get('xstep', 0.0))
    input_dict['xmax'] = float(input_dict.get('xmax', 0.0))
    
    # These are calculation-specific default floats with units
    input_dict['beta_xx'] = iprPy.input.value(input_dict, 'beta_xx',
                                    default_unit=pl_unit,
                                    default_term='0.0 GPa*angstrom')
    input_dict['beta_xy'] = iprPy.input.value(input_dict, 'beta_xy',
                                    default_unit=pl_unit,
                                    default_term='0.0 GPa*angstrom')
    input_dict['beta_xz'] = iprPy.input.value(input_dict, 'beta_xz',
                                    default_unit=pl_unit,
                                    default_term='0.0 GPa*angstrom')
    input_dict['beta_yy'] = iprPy.input.value(input_dict, 'beta_yy',
                                    default_unit=pl_unit,
                                    default_term='0.0 GPa*angstrom')
    input_dict['beta_yz'] = iprPy.input.value(input_dict, 'beta_yz',
                                    default_unit=pl_unit,
                                    default_term='0.0 GPa*angstrom')
    input_dict['beta_zz'] = iprPy.input.value(input_dict, 'beta_zz',
                                    default_unit=pl_unit,
                                    default_term='0.0 GPa*angstrom')
    input_dict['tau_xy'] = iprPy.input.value(input_dict, 'tau_xy',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    input_dict['tau_yy'] = iprPy.input.value(input_dict, 'tau_yy',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    input_dict['tau_yz'] = iprPy.input.value(input_dict, 'tau_yz',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    input_dict['halfwidth'] = iprPy.input.value(input_dict, 'halfwidth',
                                    default_unit=input_dict['length_unit'],
                                    default_term='1.0 angstrom')
    input_dict['cutofflongrange'] = iprPy.input.value(input_dict,
                                    'cutofflongrange',
                                    default_unit=input_dict['length_unit'],
                                    default_term='1000 angstrom')
    
    # Process tau
    txy = input_dict['tau_xy']
    tyy = input_dict['tau_yy']
    tyz = input_dict['tau_yz']
    input_dict['tau'] = np.array([[0.0, txy, 0.0],
                                  [txy, tyy, tyz],
                                  [0.0, tyz, 0.0]])
    
    # Process beta
    bxx = input_dict['beta_xx']
    bxy = input_dict['beta_xy']
    bxz = input_dict['beta_xz']
    byy = input_dict['beta_yy']
    byz = input_dict['beta_yz']
    bzz = input_dict['beta_zz']
    input_dict['beta'] = np.array([[bxx, bxy, bxz],
                                   [bxy, byy, byz],
                                   [bxz, byz, bzz]])
    
    # Process alpha
    alpha = input_dict['alpha'].split()
    unit = p_per_l_unit
    if len(alpha) > 1:
        try:
            float(alpha[-1])
        except:
            unit = alpha.pop()
    for i in range(len(alpha)):
        alpha[i] = uc.set_in_units(float(alpha[i]), unit)
    input_dict['alpha'] = alpha
    
    # Process xmax, xstep, xnum
    for xkey in ['xmax', 'xstep', 'xnum']:
        if input_dict[xkey] == 0:
            input_dict[xkey] = None
    
    # Process minimize_options
    boolkeys = ['disp']
    intkeys = ['maxiter', 'maxfev']
    floatkeys = ['xatol', 'fatol', 'xtol', 'ftol', 'gtol', 'norm', 'eps']
    keys = boolkeys + intkeys + floatkeys
    min_options = iprPy.input.termtodict(input_dict['minimize_options'], keys)
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
    
    # Load system
    iprPy.input.subset('atomman_systemload').interpret(input_dict, build=build)
    
    # Load dislocation parameters
    iprPy.input.subset('dislocation').interpret(input_dict)
    
    # Load elastic constants
    iprPy.input.subset('atomman_elasticconstants').interpret(input_dict, build=build)
    
    # Load gamma surface
    iprPy.input.subset('atomman_gammasurface').interpret(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])