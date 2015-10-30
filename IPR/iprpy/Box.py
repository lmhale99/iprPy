import numpy as np
from copy import deepcopy
from tools import mag

#Returns the ange between two vectors
def vect_angle(vect1, vect2):
    return 180 * np.arccos(np.dot(vect1, vect2)/(mag(vect1) * mag(vect2))) / np.pi

class Box:
#Class for representing a triclinic box

    def __init__(self, origin=None,
                 avect=None, bvect=None, cvect=None,
                 a=None, b=None, c=None, alpha=None, beta=None, gamma=None,
                 lx=None, ly=None, lz=None, xy=None, xz=None, yz=None,
                 xlo=None, xhi=None, ylo=None, yhi=None, zlo=None, zhi=None):
    
        #Call set_vectors if all three vects are supplied and nothing else
        if avect is not None or bvect is not None or cvect is not None:
            assert a is None and b is None and c is None,                  'Box vectors and magnitudes cannot both be given!'
            assert alpha is None and beta is None and gamma is None,       'Box vectors and angles cannot both be given!'
            assert lx is None and ly is None and lz is None,               'Box vectors and lengths cannot both be given!'
            assert xy is None and xz is None and yz is None,               'Box vectors and tilts cannot both be given!'
            assert xlo is None and xhi is None,                            'Box vectors and hi/los cannot both be given!'
            assert ylo is None and yhi is None,                            'Box vectors and hi/los cannot both be given!'
            assert zlo is None and zhi is None,                            'Box vectors and hi/los cannot both be given!'
            
            self.set_vectors(origin=origin, avect=avect, bvect=bvect, cvect=cvect)

        #Call set_abc if any of a,b,c and angles are supplied and not any lengths or tilts
        elif a is not None or b is not None or c is not None or alpha is not None or beta is not None or gamma is not None:
            assert lx is None and ly is None and lz is None,               'Box magnitudes/angles and lengths cannot both be given!'
            assert xy is None and xz is None and yz is None,               'Box magnitudes/angles and tilts cannot both be given!'
            assert xlo is None and xhi is None,                            'Box magnitudes/angles and hi/los cannot both be given!'
            assert ylo is None and yhi is None,                            'Box magnitudes/angles and hi/los cannot both be given!'
            assert zlo is None and zhi is None,                            'Box magnitudes/angles and hi/los cannot both be given!'
   
            self.set_abc(origin=origin, a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)
            
        #Call set_lengths if none of the above
        else:
            self.set_lengths(origin=origin, lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz,
                             xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi, zlo=zlo, zhi=zhi)                
    
    def set_origin(self, origin=None):
    #Sets the box origin    
        
        if origin is None:
            origin = np.zeros(3)
        
        assert isinstance(origin, (list, tuple, np.ndarray)) and len(origin) == 3
        self.__origin = origin
            
    
    def set_vectors(self, origin=None, avect=None, bvect=None, cvect=None):
    #Set the direction vectors of the box. Will rotate the box so that avect[1] = avect[2] = bvect[2] = 0.
        
        assert isinstance(avect, (list, tuple, np.ndarray)) and len(avect) == 3, 'Incorrect Box vector!'
        assert isinstance(bvect, (list, tuple, np.ndarray)) and len(bvect) == 3, 'Incorrect Box vector!'
        assert isinstance(cvect, (list, tuple, np.ndarray)) and len(cvect) == 3, 'Incorrect Box vector!'
        self.__avect = np.array(avect, dtype=np.float)
        self.__bvect = np.array(bvect, dtype=np.float)
        self.__cvect = np.array(cvect, dtype=np.float)
        
        self.normalize()
        self.set_origin(origin=origin)
        
    def set_abc(self, origin=None, a=None, b=None, c=None, alpha=None, beta=None, gamma=None):
    #Set the direction vectors using vector magnitudes (a, b, c) and angles (alpha, beta, gamma).If values not supplied, defaults are magnitudes = 1 and angles = 90.
    
        if a is None and b is None and c is None:
            a = 1.0
            b = 1.0
            c = 1.0
        
        assert isinstance(a, (int, long, float)), 'Incorrect Box magnitude!'
        assert isinstance(b, (int, long, float)), 'Incorrect Box magnitude!'
        assert isinstance(c, (int, long, float)), 'Incorrect Box magnitude!'

        if alpha is None:
            alpha = 90.0
        if beta is None:
            beta = 90.0
        if gamma is None:
            gamma = 90.0
        assert isinstance(alpha, (int, long, float)), 'Incorrect Box angle!'
        assert isinstance(beta,  (int, long, float)), 'Incorrect Box angle!'
        assert isinstance(gamma, (int, long, float)), 'Incorrect Box angle!' 
        
        lx = a
        xy_tilt = b * np.cos(gamma * np.pi / 180)
        xz_tilt = c * np.cos(beta * np.pi / 180)
        ly = (b**2 - xy_tilt**2)**0.5
        yz_tilt = (b * c * np.cos(alpha * np.pi / 180) - xy_tilt * xz_tilt) / ly
        lz = (c**2 - xz_tilt**2 - yz_tilt**2)**0.5

        self.__avect = np.array([lx, 0.0, 0.0])
        self.__bvect = np.array([xy_tilt, ly, 0.0])
        self.__cvect = np.array([xz_tilt, yz_tilt, lz])
        
        self.__avect[abs(self.__avect) < mag(self.__avect) * 1e-8] = 0.0
        self.__bvect[abs(self.__bvect) < mag(self.__bvect) * 1e-8] = 0.0
        self.__cvect[abs(self.__cvect) < mag(self.__cvect) * 1e-8] = 0.0
        
        self.set_origin(origin=origin)
        
    def set_lengths(self, origin=None, lx=None, ly=None, lz=None, xy=None, xz=None, yz=None,
                    xlo=None, xhi=None, ylo=None, yhi=None, zlo=None, zhi=None):
    #Set the direction vectors using lengths (lx, ly, lz) and tilts (xy, xz, yz). If values not supplied, defaults are lengths = 1 and tilts = 0.
        
        if lx is not None or ly is not None or lz is not None:
            assert lx is not None and ly is not None and lz is not None, 'Incorrect Box lengths!'
            assert xlo is None and xhi is None,                          'Box lengths and hi/los cannot both be given!'
            assert ylo is None and yhi is None,                          'Box lengths and hi/los cannot both be given!'
            assert zlo is None and zhi is None,                          'Box lengths and hi/los cannot both be given!'
   
        elif xlo is not None or xhi is not None or ylo is not None or yhi is not None or zlo is not None or zhi is not None:
            assert xlo is not None and xhi is not None and ylo is not None and yhi is not None and zlo is not None and zhi is not None, 'Incorrect Box hi/los!'
            assert origin is None,          'Box origin and hi/los cannot both be given!'
            lx = xhi - xlo
            ly = yhi - ylo
            lz = zhi - zlo
            origin = np.array([xlo, ylo, zlo])            
        
        else:
            lx = 1.0
            ly = 1.0
            lz = 1.0
        
        assert isinstance(lx, (int, long, float)), 'Incorrect Box length!'
        assert isinstance(ly, (int, long, float)), 'Incorrect Box length!'
        assert isinstance(lz, (int, long, float)), 'Incorrect Box length!'
        
        if xy is None:
            xy = 0.0
        if xz is None:
            xz = 0.0
        if yz is None:
            yz = 0.0

        assert isinstance(xy, (int, long, float)), 'Incorrect Box tilt!'
        assert isinstance(xz, (int, long, float)), 'Incorrect Box tilt!'
        assert isinstance(yz, (int, long, float)), 'Incorrect Box tilt!' 
        
        self.__avect = np.array([lx, 0.0, 0.0])
        self.__bvect = np.array([xy, ly, 0.0])
        self.__cvect = np.array([xz, yz, lz])
        
        self.__avect[abs(self.__avect) < mag(self.__avect) * 1e-8] = 0.0
        self.__bvect[abs(self.__bvect) < mag(self.__bvect) * 1e-8] = 0.0
        self.__cvect[abs(self.__cvect) < mag(self.__cvect) * 1e-8] = 0.0
        
        self.set_origin(origin)
        
    def normalize(self):
    #Rotates the box so that avect_y = avect_z = bvect_z = 0.
        
        #test right handedness
        test = np.dot(np.cross(self.__avect, self.__bvect), self.__cvect)
        if test > 0:
            a = self.__avect
            b = self.__bvect
            c = self.__cvect
            
            a_x = mag(a)
            b_x = np.dot(b, a/a_x)
            b_y = (mag(b)**2 - b_x**2)**0.5
            c_x = np.dot(c, a/a_x)
            c_y = (np.dot(b, c) - b_x * c_x) / b_y
            c_z = (mag(c)**2 - c_x**2 - c_y**2)**0.5
        
            self.__avect = np.array([a_x, 0.0, 0.0])
            self.__bvect = np.array([b_x, b_y, 0.0])
            self.__cvect = np.array([c_x, c_y, c_z])
            
            self.__avect[abs(self.__avect) < mag(self.__avect) * 1e-8] = 0.0
            self.__bvect[abs(self.__bvect) < mag(self.__bvect) * 1e-8] = 0.0
            self.__cvect[abs(self.__cvect) < mag(self.__cvect) * 1e-8] = 0.0
        
        else:
            raise ValueError('Supplied vectors are not right handed: inversion needed!')
            
    def get(self, term):
    #Returns vectors (avect,bvect,cvect), magnitudes (a,b,c), angles (alpha,beta,gamma), lengths (lx,ly,lz), and tilts (xy,xz,yz)
    
        if   term == 'avect':
            value = deepcopy(self.__avect)
        elif term == 'bvect':
            value = deepcopy(self.__bvect)
        elif term == 'cvect':
            value = deepcopy(self.__cvect)
        elif term == 'a':
            value = mag(self.__avect)
        elif term == 'b':
            value = mag(self.__bvect)
        elif term == 'c':
            value = mag(self.__cvect)
        elif term == 'alpha':
            value = vect_angle(self.__bvect, self.__cvect)
        elif term == 'beta':
            value = vect_angle(self.__avect, self.__cvect)
        elif term == 'gamma':
            value = vect_angle(self.__avect, self.__bvect)
        elif term == 'lx':
            value = self.__avect[0]
        elif term == 'ly':
            value = self.__bvect[1]
        elif term == 'lz':
            value = self.__cvect[2]
        elif term == 'xy':
            value = self.__bvect[0]
        elif term == 'xz':
            value = self.__cvect[0]
        elif term == 'yz':
            value = self.__cvect[1]
        elif term == 'xlo':
            value = self.__origin[0] 
        elif term == 'xhi':
            value = self.__origin[0] + self.__avect[0]
        elif term == 'ylo':
            value = self.__origin[1]
        elif term == 'yhi':
            value = self.__origin[1] + self.__bvect[1]
        elif term == 'zlo':
            value = self.__origin[2]
        elif term == 'zhi':
            value = self.__origin[2] + self.__cvect[2]   
        elif term == 'origin':
            value = deepcopy(self.__origin)
        else:
            value = None
        
        return value