import numpy as np
from mag import mag

def axes_check(axes, tol=1e-8):
    #Checks axis relationship and returns transformation matrix, T
    uaxes = np.empty((3,3))
    for i in xrange(3):
        uaxes[i] = axes[i] / mag(axes[i])
    
    assert np.isclose(np.dot(uaxes[0], uaxes[1]), 0., atol=tol), 'dots are not 0!'
    assert np.isclose(np.dot(uaxes[0], uaxes[2]), 0., atol=tol), 'dots are not 0!'
    assert np.isclose(np.dot(uaxes[1], uaxes[2]), 0., atol=tol), 'dots are not 0!'
    assert np.allclose(np.cross(uaxes[0], uaxes[1]) - uaxes[2], np.zeros(3), atol=tol), 'cross does not check!'
    
    return uaxes