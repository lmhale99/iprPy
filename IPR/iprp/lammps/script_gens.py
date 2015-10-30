import os
import iprp
import subprocess
from file_converters import *

#Generates the LAMMPS script lines associated with having LAMMPS create the system
def sys_gen_script(alat = np.array([1., 1., 1.]),
                   ucell = [iprp.Atom(1,np.array([0.0, 0.0, 0.0])),
                            iprp.Atom(1,np.array([0.5, 0.5, 0.0])),
                            iprp.Atom(1,np.array([0.0, 0.5, 0.5])),
                            iprp.Atom(1,np.array([0.5, 0.0, 0.5]))],
                   axes = np.array([[1,0,0], [0,1,0], [0,0,1]]),
                   shift = np.array([0.0, 0.0, 0.0]),
                   size = np.array([[-3,3], [-3,3], [-3,3]],dtype=np.int)):

    ntypes = 0
    pos_basis = ''
    type_basis = ''
    for i in xrange(len(ucell)):
        pos_basis += 'basis %f %f %f ' %(ucell[i].get('x'), ucell[i].get('y'), ucell[i].get('z'))
        if ucell[i].get('type') > ntypes:
            ntypes = ucell[i].get('type')
        if ucell[i].get('type') > 1:
            type_basis += ' basis %i %i'%(i+1, ucell[i].get('type'))
    
    #compute b/a and c/a ratios
    a_ratios = [alat[0] / alat[0], alat[1] / alat[0], alat[2] / alat[0]]

    #Adjust crystal spacing to be consistent with axes
    spacing = np.zeros(3)
    for i in xrange(3):
        spacing[i] = a_ratios[i] * (axes[i,0]**2 + axes[i,1]**2 + axes[i,2]**2)**0.5
    
    newline = '\n'
    script = newline.join(['#Script prepared by NIST',
                           'variable alat0 equal %.12f' %(alat[0]),
                           'lattice custom ${alat0} a1 1.0 0.0 0.0 a2 0.0 %.12f 0.0 a3 0.0 0.0 %.12f &' %(a_ratios[1], a_ratios[2]),
                           'origin %f %f %f &' %(shift[0], shift[1], shift[2]),
                           'spacing %.12f %.12f %.12f &' %(spacing[0], spacing[1], spacing[2]),
                           'orient x %i %i %i orient y %i %i %i orient z %i %i %i &' %(axes[0,0], axes[0,1], axes[0,2],
                                                                                       axes[1,0], axes[1,1], axes[1,2],
                                                                                       axes[2,0], axes[2,1], axes[2,2]),
                           pos_basis,
                           '',
                           'region box block %i %i %i %i %i %i' %(size[0,0], size[0,1], size[1,0], size[1,1], size[2,0], size[2,1]),
                           'create_box %i box' %(ntypes),
                           'create_atoms 1 box' + type_basis]) 
    return script

#Uses LAMMPS to create a iprp.System from the supplied system parameters    
def create_sys(lammps, atomtypes, pbc,
               alat = np.array([1., 1., 1.]),
               ucell = [iprp.Atom(1, np.array([0.0, 0.0, 0.0])),
                        iprp.Atom(1, np.array([0.5, 0.5, 0.0])),
                        iprp.Atom(1, np.array([0.0, 0.5, 0.5])),
                        iprp.Atom(1, np.array([0.5, 0.0, 0.5]))],
               axes = np.array([[1,0,0], [0,1,0], [0,0,1]]),
               shift = np.array([0.0, 0.0, 0.0]),
               size = np.array([[-3,3], [-3,3], [-3,3]],dtype=np.int)):
          
    sys_gen = sys_gen_script(alat, ucell, axes, shift, size)

    newline = '\n'
    script = newline.join(['boundary p p p',
                           'units metal',
                           'atom_style atomic',
                           '',
                           sys_gen,
                           '',
                           'mass * 1',
                           'pair_style morse 0.5',
                           'pair_coeff * * 0.0 2.0 1.5'
                           '',                           
                           'dump dumpit all custom 100000 sys0.dump id type x y z',
                           'dump_modify dumpit format "%i %i %.13e %.13e %.13e"',                           
                           'run 0'])
    f = open('create_sys.in', 'w')
    f.write(script)
    f.close()
    output = subprocess.check_output(lammps + ' -in create_sys.in', shell=True)

    sys0 = read_dump('sys0.dump', atomtypes)
    sys0.set('pbc', pbc)
    sys0.set('axes', axes)
    os.remove('sys0.dump')
    os.remove('create_sys.in')
    os.remove('log.lammps')
    return sys0      