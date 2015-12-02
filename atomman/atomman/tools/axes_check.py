import numpy as np

def axes_check(axes, tol=1e-8):
    #Checks axis relationship and returns transformation matrix, T, and axis magnitudes, mag
    mag = np.apply_along_axis(np.linalg.norm, 1, axes)
    uaxes = axes / mag[:,None]
    if (np.isclose(np.dot(uaxes[0], uaxes[1]), 0., atol=tol) == False or 
        np.isclose(np.dot(uaxes[0], uaxes[2]), 0., atol=tol) == False or 
        np.isclose(np.dot(uaxes[1], uaxes[2]), 0., atol=tol) == False):
        raise ValueError('dots are not 0!')
    if np.allclose(np.cross(uaxes[0], uaxes[1]) - uaxes[2], np.zeros(3), atol=tol) == False:
        raise ValueError('cross does not check!')
    return uaxes, mag