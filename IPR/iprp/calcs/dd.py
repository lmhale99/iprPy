import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import PatchCollection
from calc_tools import mag


def dd(base, data, prange, burgers, scale=[1], save=False, show=True):
    #initialize fig and define image size
    if len(scale)==1:
        fig, ax1, = plt.subplots(1, 1,squeeze=True,figsize=(7,7), dpi=72)
    elif len(scale)==2:
        fig, (ax1, ax2) = plt.subplots(1, 2,squeeze=True,figsize=(16,7), dpi=72)
    wscale = 1./200.
    bmag = mag(burgers)
    radius = bmag/10
    bvect = burgers/bmag
    
    natoms = len(base.atoms)
    nlist = base.get('nlist')
    
    for i in xrange(natoms):
        #identify all base atoms i in prange
        if (base.atoms[i].get('z') > prange[2,0] and base.atoms[i].get('z') < prange[2,1] and
            base.atoms[i].get('y') > prange[1,0] and base.atoms[i].get('y') < prange[1,1] and
            base.atoms[i].get('x') > prange[0,0] and base.atoms[i].get('x') < prange[0,1]):
            
            #Construct xy map of base atom positions colored by z position
            color = cm.hsv((base.atoms[i].get('z') - prange[2,0]) / (prange[2,1] - prange[2,0]) )
            ax1.add_patch(mpatches.Circle((base.atoms[i].get('x'), base.atoms[i].get('y')), radius, fc=color))
            if len(scale)==2:
                ax2.add_patch(mpatches.Circle((base.atoms[i].get('x'), base.atoms[i].get('y')), radius, fc=color))
            
            #for all neighbors j of base atoms i
            for jj in xrange(nlist[i][0]):
                j = nlist[i][jj+1] - 1
                
                deltabase = base.atoms[i].get('pos') - base.atoms[j].get('pos')
                #if the base atoms have different xy coordinates
                if mag(deltabase[:2]>1e-5):
                    deltadata = data.atoms[i].get('pos') - data.atoms[j].get('pos')
                    
                    #c = centerpoint, dd = differential displacement vector for i-j
                    c = (base.atoms[j].get('pos') + base.atoms[i].get('pos')) / 2
                    dd = (deltadata - deltabase)
                    ddcomp = dd.dot(bvect)
                    if ddcomp > bmag / 2:
                        ddcomp -= bmag
                    elif ddcomp < -bmag / 2:
                        ddcomp += bmag
                    
                    dds = deltabase[:2] / mag(deltabase[:2]) * ddcomp * scale[0]
                    wide = mag(dds) * wscale
                    ax1.quiver(c[0], c[1], dds[0], dds[1], angles='xy', scale_units='xy', scale=1, pivot='middle', width=wide)
                    ax1.axis([prange[0,0], prange[0,1], prange[1,0], prange[1,1]])
                    
                    if len(scale)==2:
                        dde = dd[:2] * scale[1]
                        if deltabase[2] > 0:
                            dde = -dde

                        wide = mag(dde) * wscale
                        ax2.quiver(c[0], c[1], dde[0], dde[1], angles='xy', scale_units='xy', scale=1, pivot='middle', width=wide)
                        ax2.axis([prange[0,0], prange[0,1], prange[1,0], prange[1,1]])
    
    if save:
        plt.savefig('DD.png', dpi=800)
    if show==False:
        plt.close(fig)
    plt.show()        