# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

def sdvpn(ucell: am.System,
          C: am.ElasticConstants,
          burgers: Union[list, np.ndarray],
          ξ_uvw: Union[list, np.ndarray],
          slip_hkl: Union[list, np.ndarray],
          gamma: am.defect.GammaSurface,
          m: Union[list, np.ndarray] = [0,1,0],
          n: Union[list, np.ndarray] = [0,0,1],
          cutofflongrange: float = uc.set_in_units(1000, 'angstrom'),
          tau: np.ndarray = np.zeros((3,3)),
          alpha: list = [0.0],
          beta: np.ndarray = np.zeros((3,3)),
          cdiffelastic: bool = False,
          cdiffsurface: bool = True,
          cdiffstress: bool = False,
          fullstress: bool = True,
          halfwidth: float = uc.set_in_units(1, 'angstrom'),
          normalizedisreg: bool = True,
          xnum: Optional[int] = None,
          xmax: Optional[float] = None,
          xstep: Optional[float] = None,
          xscale: bool = False,
          min_method: str = 'Powell',
          min_options: dict = {},
          min_cycles: int = 10) -> dict:
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

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'SDVPN_solution'** (*atomman.defect.SDVPN*) - The SDVPN solution
          object at the end of the run.
        - **'minimization_energies'** (*list*) - The total energy values
          measured after each minimization cycle.
        - **'disregistry_profiles'** (*list*) - The disregistry profiles
          obtained after each minimization cycle.
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