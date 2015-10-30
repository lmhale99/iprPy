#import sys
#sys.path.append('../..')
import iprpy
import numpy as np
from iprpy.tools import mag

#Generates the LAMMPS script lines associated with having LAMMPS create the system
def sys_gen(units = 'metal',
            atom_style = 'atomic',
            pbc = (True, True, True),
            ucell_box = iprpy.Box(),
            ucell_atoms = [iprpy.Atom(1, np.array([0.0, 0.0, 0.0])),
                           iprpy.Atom(1, np.array([0.5, 0.5, 0.0])),
                           iprpy.Atom(1, np.array([0.0, 0.5, 0.5])),
                           iprpy.Atom(1, np.array([0.5, 0.0, 0.5]))],
            axes = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
            shift = np.array([0.1, 0.1, 0.1]),
            size = np.array([[-3,3], [-3,3], [-3,3]], dtype=np.int)):

    boundary = ''
    for i in xrange(3):
        if pbc[i]:
            boundary += 'p '
        else:
            boundary += 'm '
    
    ntypes = 0
    pos_basis = ''
    type_basis = ''
    for i in xrange(len(ucell_atoms)):
        pos_basis += '        basis %f %f %f' %(ucell_atoms[i].pos(0), ucell_atoms[i].pos(1), ucell_atoms[i].pos(2))
        if i < len(ucell_atoms) - 1:
            pos_basis += ' &\n'
        if ucell_atoms[i].atype() > ntypes:
            ntypes = ucell_atoms[i].atype()
        if ucell_atoms[i].atype() > 1:
            type_basis += ' &\n             basis %i %i'%(i+1, ucell_atoms[i].atype())
    
    vects = (ucell_box.get('avect'), ucell_box.get('bvect'), ucell_box.get('cvect'))
    
    #Test if box is cubic
    if vects[1][0] == 0.0 and vects[2][0] == 0.0 and vects[2][1] == 0.0:
        region_box = 'region box block %i %i %i %i %i %i' % (size[0,0], size[0,1], size[1,0], size[1,1], size[2,0], size[2,1])
        ortho = True
    else:
        assert np.allclose(axes[0], [1,0,0]) and np.allclose(axes[1], [0,1,0]) and np.allclose(axes[2], [0,0,1]), 'Rotation of non-orthogonal box not suppported'
        ortho = False
        size_xy = vects[1][0] * (size[0,1] - size[0,0]) / mag(vects[0])
        size_xz = vects[2][0] * (size[0,1] - size[0,0]) / mag(vects[0])
        size_yz = vects[2][1] * (size[1,1] - size[1,0]) / mag(vects[1])
        region_box = 'region box prism %i %i %i %i %i %i %f %f %f' % (size[0,0], size[0,1], size[1,0], 
                                                                      size[1,1], size[2,0], size[2,1], 
                                                                      size_xy,   size_xz,   size_yz)
        
    #Adjust crystal spacing for systems to be (nearly) perfectly periodic across boundaries
    spacing = np.zeros(3)
    for i in xrange(3):
        spacing[i] = vects[i][i] * mag(axes[i])

    
    newline = '\n'
    script = newline.join(['#Script prepared by NIST iprPy code',
                           '',
                           'units ' + units,
                           'atom_style ' + atom_style,
                           ''
                           'boundary ' + boundary,
                           '',
                           'lattice custom 1.0 &',
                           '        a1 %.12f %.12f %.12f &'      % (vects[0][0], vects[0][1], vects[0][2]),
                           '        a2 %.12f %.12f %.12f &'      % (vects[1][0], vects[1][1], vects[1][2]),
                           '        a3 %.12f %.12f %.12f &'      % (vects[2][0], vects[2][1], vects[2][2]),
                           '        origin %f %f %f &'           % (shift[0], shift[1], shift[2]),
                           '        spacing %.12f %.12f %.12f &' % (spacing[0], spacing[1], spacing[2]),
                           '        orient x %i %i %i &'         % (axes[0,0], axes[0,1], axes[0,2]),
                           '        orient y %i %i %i &'         % (axes[1,0], axes[1,1], axes[1,2]),
                           '        orient z %i %i %i &'         % (axes[2,0], axes[2,1], axes[2,2]),
                           pos_basis,
                           '',
                           region_box,
                           'create_box %i box' %(ntypes),
                           'create_atoms 1 box' + type_basis]) 
    return script

    
