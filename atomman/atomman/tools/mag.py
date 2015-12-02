import numpy as np

#Returns the magnitude of a vector
def mag(vector):
    magval = 0.0
    for term in vector:
        magval += term**2.
    return magval ** 0.5

