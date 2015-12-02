#Checks that the axes are orthogonal and returns normalized direction vectors
#The normalized array is the transformation matrix, T, relative to a [1,0,0],[0,1,0],[0,0,1] orientation
def axes_check(axes, tol=1e-8):
    mag = np.apply_along_axis(np.linalg.norm, 1, axes)
    uaxes = axes / mag[:,None]
    if (np.isclose(np.dot(uaxes[0], uaxes[1]), 0., atol=tol) == False or 
        np.isclose(np.dot(uaxes[0], uaxes[2]), 0., atol=tol) == False or 
        np.isclose(np.dot(uaxes[1], uaxes[2]), 0., atol=tol) == False):
        raise ValueError('dots are not 0!')
    if np.allclose(np.cross(uaxes[0], uaxes[1]) - uaxes[2], np.zeros(3), atol=tol) == False:
        raise ValueError('cross does not check!')
    return uaxes, mag