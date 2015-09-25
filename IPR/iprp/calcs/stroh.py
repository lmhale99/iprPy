import numpy as np

#Checks that the axes are orthogonal and returns normalized direction vectors
#The normalized array is the transformation matrix, T, relative to a [1,0,0],[0,1,0],[0,0,1] orientation
def ax_check(axes, tol=1e-8):
    mag = np.apply_along_axis(np.linalg.norm, 1, axes)
    uaxes = axes / mag[:,None]
    if (np.isclose(np.dot(uaxes[0], uaxes[1]), 0., atol=tol) == False or 
        np.isclose(np.dot(uaxes[0], uaxes[2]), 0., atol=tol) == False or 
        np.isclose(np.dot(uaxes[1], uaxes[2]), 0., atol=tol) == False):
        raise ValueError('dots are not 0!')
    if np.allclose(np.cross(uaxes[0], uaxes[1]) - uaxes[2], np.zeros(3), atol=tol) == False:
        raise ValueError('cross does not check!')
    return uaxes, mag

#Transforms the 4D elastic constant matrix, C, using the transformation matrix, T.
def c_transform(initC, T, tol=1e-8):
    Q = np.einsum('km,ln->mnkl', T, T)
    C = np.einsum('ghij,ghmn,mnkl->ijkl', Q, initC, Q)
    C[abs(C) < tol] = 0.0
    return C  

#Transforms the (6x6) Cmn elastic constants matrix to the (3x3x3x3) Cijkl matrix
def c_mn_to_c_ijkl(c_mn): 
    for m in range(6):
        for n in range(6):
            if np.isclose(c_mn[m,n],c_mn[n,m]) == False:
                raise ValueError('No ij symmetry!')

    c_ijkl = np.array([[[[c_mn[0,0],c_mn[0,5],c_mn[0,4]], [c_mn[0,5],c_mn[0,1],c_mn[0,3]], [c_mn[0,4],c_mn[0,3],c_mn[0,2]]],
                        [[c_mn[5,0],c_mn[5,5],c_mn[5,4]], [c_mn[5,5],c_mn[5,1],c_mn[5,3]], [c_mn[5,4],c_mn[5,3],c_mn[5,2]]],
                        [[c_mn[4,0],c_mn[4,5],c_mn[4,4]], [c_mn[4,5],c_mn[4,1],c_mn[4,3]], [c_mn[4,4],c_mn[4,3],c_mn[4,2]]]], 
                     
                       [[[c_mn[5,0],c_mn[5,5],c_mn[5,4]], [c_mn[5,5],c_mn[5,1],c_mn[5,3]], [c_mn[5,4],c_mn[5,3],c_mn[5,2]]],
                        [[c_mn[1,0],c_mn[1,5],c_mn[1,4]], [c_mn[1,5],c_mn[1,1],c_mn[1,3]], [c_mn[1,4],c_mn[1,3],c_mn[1,2]]],
                        [[c_mn[3,0],c_mn[3,5],c_mn[3,4]], [c_mn[3,5],c_mn[3,1],c_mn[3,3]], [c_mn[3,4],c_mn[3,3],c_mn[3,2]]]],
                     
                       [[[c_mn[4,0],c_mn[4,5],c_mn[4,4]], [c_mn[4,5],c_mn[4,1],c_mn[4,3]], [c_mn[4,4],c_mn[4,3],c_mn[4,2]]],
                        [[c_mn[3,0],c_mn[3,5],c_mn[3,4]], [c_mn[3,5],c_mn[3,1],c_mn[3,3]], [c_mn[3,4],c_mn[3,3],c_mn[3,2]]],
                        [[c_mn[2,0],c_mn[2,5],c_mn[2,4]], [c_mn[2,5],c_mn[2,1],c_mn[2,3]], [c_mn[2,4],c_mn[2,3],c_mn[2,2]]]]])
    
    return c_ijkl

#Transforms the (3x3x3x3) Cijkl elastic constants matrix to the (6x6) Cmn matrix
def c_ijkl_to_c_mn(c_ijkl):
    Check = True
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    if np.isclose(c_ijkl[i,j,k,l],c_ijkl[j,i,k,l]) == False:
                        Check = False
                    if np.isclose(c_ijkl[i,j,k,l],c_ijkl[i,j,l,k]) == False:
                        Check = False
                    if np.isclose(c_ijkl[i,j,k,l],c_ijkl[j,i,l,k]) == False:
                        Check = False
                    if np.isclose(c_ijkl[i,j,k,l],c_ijkl[k,l,i,j]) == False:
                        Check = False
    if Check:
        c_mn = np.array([[c_ijkl[0,0,0,0], c_ijkl[0,0,1,1], c_ijkl[0,0,2,2], c_ijkl[0,0,1,2], c_ijkl[0,0,0,2], c_ijkl[0,0,0,1]],
                         [c_ijkl[1,1,0,0], c_ijkl[1,1,1,1], c_ijkl[1,1,2,2], c_ijkl[1,1,1,2], c_ijkl[1,1,0,2], c_ijkl[1,1,0,1]],
                         [c_ijkl[2,2,0,0], c_ijkl[2,2,1,1], c_ijkl[2,2,2,2], c_ijkl[2,2,1,2], c_ijkl[2,2,0,2], c_ijkl[2,2,0,1]],
                         [c_ijkl[1,2,0,0], c_ijkl[1,2,1,1], c_ijkl[1,2,2,2], c_ijkl[1,2,1,2], c_ijkl[1,2,0,2], c_ijkl[1,2,0,1]],
                         [c_ijkl[0,2,0,0], c_ijkl[0,2,1,1], c_ijkl[0,2,2,2], c_ijkl[0,2,1,2], c_ijkl[0,2,0,2], c_ijkl[0,2,0,1]],
                         [c_ijkl[0,1,0,0], c_ijkl[0,1,1,1], c_ijkl[0,1,2,2], c_ijkl[0,1,1,2], c_ijkl[0,1,0,2], c_ijkl[0,1,0,1]]])
        return c_mn   
    else:
        raise ValueError('Symmetry checks failed!')
        return ''        
    
#Does the initial Stroh calculations and returns a dictionary containing system wide parameters
def stroh_setup(C, tol=1e-8):
    #Matrixes of Cijkl constants used to construct N
    m = np.array([1.0, 0.0, 0.0])
    n = np.array([0.0, 1.0, 0.0])
    mm = np.einsum('i,ijkl,l', m, C, m)
    mn = np.einsum('i,ijkl,l', m, C, n)
    nm = np.einsum('i,ijkl,l', n, C, m)
    nn = np.einsum('i,ijkl,l', n, C, n)
    
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
    p = eig[0]
    eigvec = np.transpose(eig[1])
    
    #round out near zero terms
    p.real[abs(p.real) < tol] = 0.0
    p.imag[abs(p.imag) < tol] = 0.0
    eigvec.real[abs(eigvec.real) < tol] = 0.0
    eigvec.imag[abs(eigvec.imag) < tol] = 0.0

    #separate the eigenvectors into A and L
    A = np.array([eigvec[0,:3], eigvec[1,:3], eigvec[2,:3], eigvec[3,:3], eigvec[4,:3], eigvec[5,:3]])
    L = np.array([eigvec[0,3:], eigvec[1,3:], eigvec[2,3:], eigvec[3,3:], eigvec[4,3:], eigvec[5,3:]])
    
    #calculate k
    k = 1. / (2. * np.einsum('si,si->s', A, L))
    
    #Checks and elastic coefficient calculations
    Check1 = np.einsum('s,si,sj->ij', k, A, L)
    Check2 = np.einsum('s,si,sj->ij', k, A, A)
    Check3 = np.einsum('s,si,sj->ij', k, L, L)
    Check4 = np.einsum('s,t,si,ti->st', k**.5, k**.5, A, L) + np.einsum('s,t,ti,si->st', k**.5, k**.5, A, L)
    
    #Round away near zero terms
    Check1.real[abs(Check1.real) < tol] = 0.0
    Check1 = np.real_if_close(Check1, tol = tol)
    Check2.real[abs(Check2.real) < tol] = 0.0
    Check2 = np.real_if_close(Check2, tol = tol)
    Check3.real[abs(Check3.real) < tol] = 0.0
    Check3 = np.real_if_close(Check3, tol = tol)    
    Check4.real[abs(Check4.real) < tol] = 0.0
    Check4.imag[abs(Check4.imag) < tol] = 0.0
    Check4 = np.real_if_close(Check4, tol=tol)
    
    #These are what the checks should equal
    Check1a = np.identity(3)
    Check2a = np.zeros((3, 3))
    Check3a = np.zeros((3, 3))
    Check4a = np.identity(6)
    
    #Return A, L, p and k if checks pass
    if (np.allclose(Check1, Check1a, atol=tol) and 
        np.allclose(Check2, Check2a, atol=tol) and 
        np.allclose(Check3, Check3a, atol=tol) and 
        np.allclose(Check4, Check4a, atol=tol)):
        return {'A':A, 'L':L, 'p':p, 'k':k}     
    else:
        print 'Stroh checks failed!'
        print str(Check1)
        print str(Check2)
        print str(Check3)
        print str(Check4)
        raise ArithmeticError('Stroh checks failed!')

#Calculate the pre-ln energy factor in eV
def stroh_preln(b, sd, tol=1e-8):
    ii = np.array([1.j])
    updn = np.array([1, -1, 1, -1, 1, -1])
    coeff = ii * np.einsum('s,s,si,sj->ij', updn, sd['k'], sd['L'], sd['L'])
    coeff.real[abs(coeff.real) < tol] = 0.0
    coeff = np.real_if_close(coeff, tol=tol)
    return b.dot(coeff.dot(b)) * 4.96683295e-4

#Calculate the Stroh displacement associated with x,y coordinates for one point
def stroh_disp_point(x, y, b, sd, tol=1e-8):
    ii = np.array([1.j])
    updn = np.array([1, -1, 1, -1, 1, -1])

    Nu = x + sd['p'] * y
    disp = 1 / (2 * np.pi * ii) * np.einsum('a,a,ai,a,a->i', updn, sd['k'], sd['A'], sd['L'].dot(b), np.log(Nu))
    disp.real[abs(disp.real) < tol] = 0.0
    disp = np.real_if_close(disp, tol=tol)
    return disp

#Calculate the Stroh stress solution associated with x,y coordinates for one point
def stroh_stress_point(x, y, b, C, sd, tol=1e-8):
    ii = np.array([1.j])
    updn = np.array([1, -1, 1, -1, 1, -1])
    
    Nu = x + sd['p'] * y
    mpn = np.array([1.0, 0.0, 0.0]) + np.einsum('a,l->al', sd['p'], np.array([0.0, 1.0, 0.0]))
    stress = 1 / (2 * np.pi * ii) * np.einsum('a,a,ijkl,al,ak,a,a->ij', updn, sd['k'], C, mpn, sd['A'], sd['L'].dot(b), 1/Nu)
    stress.real[abs(stress.real) < tol] = 0.0
    stress = np.real_if_close(stress, tol=tol)
    return stress