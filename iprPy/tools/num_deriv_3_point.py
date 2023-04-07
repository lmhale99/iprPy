# coding: utf-8

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

def num_deriv_3_point(x: npt.ArrayLike,
                      y: npt.ArrayLike) -> np.ndarray:
    """
    Evaluates the numerical derivative of a tabulated series using three values per point, i.e.
    fits a second order polynomial and finds the derivative at the point in question.  For equally
    spaced points, this is the 3 point central difference for the intermediate points and 3 point
    forward/backward difference for the end points.
    
    Parameters
    ----------
    x : array-like object
        The x coordinates where the y values are evaluated.  Should be in order
        and evenly spaced.
    y : array-like object
        The y coordinates to find derivatives of.
    
    Returns
    -------
    numpy.ndarray
        The computed numerical derivative of dy/dx.
    """
    # Initialize as a numpy array problem
    x = np.asarray(x)
    y = np.asarray(y)
    assert len(x) == len(y)
    dy = np.empty_like(x)

    # Split x, y into three sets
    x1 = x[:-2]
    x2 = x[1:-1]
    x3 = x[2:]
    y1 = y[:-2]
    y2 = y[1:-1]
    y3 = y[2:]

    # Compute shared terms used by the solution
    c = (x2**2 - x1**2) / (x1 - x2)
    d = (y1 - y2) / (x1 - x2)

    # Compute polynomial constants
    A = (y3 - y1 + d * (x1 - x3)) / (x3**2 - x1**2 + c * (x3 - x1))
    B = A * c + d

    # Compute the derivatives for the intermediate points
    dy[1:-1] = 2 * A * x2 + B

    # Compute the derivatives for the end points
    dy[0] = 2 * A[0] * x[0] + B[0]
    dy[-1] = 2 * A[-1] * x[-1] + B[-1]

    return dy
