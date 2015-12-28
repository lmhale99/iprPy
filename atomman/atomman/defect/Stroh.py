import numpy as np
from atomman.tools import ElasticConstants, axes_check

class Stroh():
    #Object for calculating the Stroh anisotropic elasticity solution for a perfectly straight dislocation
    
    def __init__(self, C, b, axes=None, tol=1e-8): 
        try:
            test = C.Cijkl()
        except:
            C = ElasticConstants(C)
                
        self.burgers = np.array(b, dtype=float)        
        assert self.burgers.shape == (3,)
        
        if axes is not None:
            T = axes_check(axes)
            self.burgers = T.dot(self.burgers)
            C = C.transform(axes)
        self.C = C.Cijkl()
        self.tol = float(tol)
        
        self.setup()

    def setup(self):
        #Does the initial Stroh calculations and returns a dictionary containing system wide parameters
        
        #Matrixes of Cijkl constants used to construct N
        m = np.array([1.0, 0.0, 0.0])
        n = np.array([0.0, 1.0, 0.0])
        mm = np.einsum('i,ijkl,l', m, self.C, m)
        mn = np.einsum('i,ijkl,l', m, self.C, n)
        nm = np.einsum('i,ijkl,l', n, self.C, m)
        nn = np.einsum('i,ijkl,l', n, self.C, n)
        
        #The four 3x3 matrixes that represent the quadrants of N
        NB = -np.linalg.inv(nn)
        NA = NB.dot(nm)
        NC = mn.dot(NA) + mm
        ND = mn.dot(NB)
        
        #N is the 6x6 array, where the eigenvalues are the roots p
        #and the eigenvectors give A and L
        N =  np.array(np.vstack((np.hstack((NA, NB)), np.hstack((NC, ND)))))
        
        #Calculate the eigenvectors and eigenvalues
        eig = np.linalg.eig(N)
        self.p = eig[0]
        eigvec = np.transpose(eig[1])
        
        #round out near zero terms
        self.p.real[abs(self.p.real) < self.tol] = 0.0
        self.p.imag[abs(self.p.imag) < self.tol] = 0.0
        eigvec.real[abs(eigvec.real) < self.tol] = 0.0
        eigvec.imag[abs(eigvec.imag) < self.tol] = 0.0

        #separate the eigenvectors into A and L
        self.A = np.array([eigvec[0,:3], eigvec[1,:3], eigvec[2,:3], eigvec[3,:3], eigvec[4,:3], eigvec[5,:3]])
        self.L = np.array([eigvec[0,3:], eigvec[1,3:], eigvec[2,3:], eigvec[3,3:], eigvec[4,3:], eigvec[5,3:]])
        
        #calculate k
        self.k = 1. / (2. * np.einsum('si,si->s', self.A, self.L))
        
        #Checks and elastic coefficient calculations
        Check1 = np.einsum('s,si,sj->ij', self.k, self.A, self.L)
        Check2 = np.einsum('s,si,sj->ij', self.k, self.A, self.A)
        Check3 = np.einsum('s,si,sj->ij', self.k, self.L, self.L)
        Check4 = np.einsum('s,t,si,ti->st', self.k**.5, self.k**.5, self.A, self.L) + np.einsum('s,t,ti,si->st', self.k**.5, self.k**.5, self.A, self.L)
        
        #Round away near zero terms
        Check1.real[abs(Check1.real) < self.tol] = 0.0
        Check1 = np.real_if_close(Check1, tol = self.tol)
        Check2.real[abs(Check2.real) < self.tol] = 0.0
        Check2 = np.real_if_close(Check2, tol = self.tol)
        Check3.real[abs(Check3.real) < self.tol] = 0.0
        Check3 = np.real_if_close(Check3, tol = self.tol)    
        Check4.real[abs(Check4.real) < self.tol] = 0.0
        Check4.imag[abs(Check4.imag) < self.tol] = 0.0
        Check4 = np.real_if_close(Check4, tol=self.tol)
        
        #Verify checks passed
        assert np.allclose(Check1, np.identity(3),   atol=self.tol), 'Stroh checks failed!'
        assert np.allclose(Check2, np.zeros((3, 3)), atol=self.tol), 'Stroh checks failed!'
        assert np.allclose(Check3, np.zeros((3, 3)), atol=self.tol), 'Stroh checks failed!'
        assert np.allclose(Check4, np.identity(6),   atol=self.tol), 'Stroh checks failed!'   
        
    def preln(self):
        #Calculate the pre-ln energy factor in eV
        
        ii = np.array([1.j])
        updn = np.array([1, -1, 1, -1, 1, -1])
        
        coeff = ii * np.einsum('s,s,si,sj->ij', updn, self.k, self.L, self.L)
        coeff.real[abs(coeff.real) < self.tol] = 0.0
        coeff = np.real_if_close(coeff, tol=self.tol)
        
        return self.burgers.dot(coeff.dot(self.burgers)) * 4.96683295e-4

    def displacement_point(self, x, y):
        #Calculate the Stroh displacement associated with x,y coordinates for one point
        
        ii = np.array([1.j])
        updn = np.array([1, -1, 1, -1, 1, -1])

        Nu = x + self.p * y
        disp = 1 / (2 * np.pi * ii) * np.einsum('a,a,ai,a,a->i', updn, self.k, self.A, self.L.dot(self.burgers), np.log(Nu))
        disp.real[abs(disp.real) < self.tol] = 0.0
        disp = np.real_if_close(disp, tol=self.tol)
        return disp

    def stress_point(self, x, y):
        #Calculate the Stroh stress solution associated with x,y coordinates for one point
        
        ii = np.array([1.j])
        updn = np.array([1, -1, 1, -1, 1, -1])
        
        Nu = x + sd['p'] * y
        mpn = np.array([1.0, 0.0, 0.0]) + np.einsum('a,l->al', sd['p'], np.array([0.0, 1.0, 0.0]))
        stress = 1 / (2 * np.pi * ii) * np.einsum('a,a,ijkl,al,ak,a,a->ij', updn, sd['k'], self.C, mpn, sd['A'], sd['L'].dot(self.burgers), 1/Nu)
        stress.real[abs(stress.real) < self.tol] = 0.0
        stress = np.real_if_close(stress, tol=self.tol)
        return stress