import iprp
import numpy as np
from scipy.interpolate import griddata
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import PatchCollection

#Returns the magnitude of a vector
def mag(vector):
    magval = 0.0
    for term in vector:
        magval += term**2.
    return magval ** 0.5

#Calculates the shortest interatomic distance, r, wrt a
def calculate_r_a(proto, alat=None):

    ucell = proto.get('ucell')
    cell = []
    
    if alat is None:
        lat_mult = proto.get('lat_mult')
    else:
        lat_mult = np.array([1.0, alat[1]/alat[0], alat[2]/alat[0]])
    for atom in ucell:
        cell.append(atom * lat_mult)
    
    box = np.array([[0.0, lat_mult[0], 0.0], 
                    [0.0, lat_mult[1], 0.0], 
                    [0.0, lat_mult[2], 0.0]])
    minimum_r = min(lat_mult)  
    
    pro_sys = iprp.System(atoms=cell, box=box, pbc=[True, True, True])
    
    for i in xrange(len(ucell)):
        for j in xrange(i):
            rdist = mag(pro_sys.dvect(i,j))
            if rdist < minimum_r:
                minimum_r = rdist
    
    return minimum_r

#Allows for dynamic iteration over all arrays of length b where each term is in range 0-a                           
def iterbox(a,b):
    for i in xrange(a):    
        if b > 1:
            for j in iterbox(a,b-1):
                yield [i] + j    
        elif b == 1:
            yield [i] 
            
def print_cij(o_cij):
    cij = np.empty((6,6))
    for i in xrange(6):
        for j in xrange(6):
            if np.isclose(o_cij[i,j], 0.0, rtol=0, atol=0.01):
                cij[i,j] = 0.0
            else:
                cij[i,j] = o_cij[i,j]
    
    print '[[%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (cij[0,0], cij[0,1], cij[0,2], cij[0,3], cij[0,4], cij[0,5])
    print ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (cij[1,0], cij[1,1], cij[1,2], cij[1,3], cij[1,4], cij[1,5])
    print ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (cij[2,0], cij[2,1], cij[2,2], cij[2,3], cij[2,4], cij[2,5])
    print ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (cij[3,0], cij[3,1], cij[3,2], cij[3,3], cij[3,4], cij[3,5])
    print ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (cij[4,0], cij[4,1], cij[4,2], cij[4,3], cij[4,4], cij[4,5])
    print ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f]]' % (cij[5,0], cij[5,1], cij[5,2], cij[5,3], cij[5,4], cij[5,5])
 
def grid_interpolate_2d(x, y, v, bins=50, range=None):
    #Handle range and bins options
    if range is None:
        range=[[x.min() ,x.max()], [y.min(), y.max()]]
    if isinstance(bins, int):
        xi = np.linspace(range[0][0], range[0][1], num=bins)
        yi = np.linspace(range[1][0], range[1][1], num=bins)
    elif isinstance(bins, list) or isinstance(bob, tuple) or isinstance(bins, np.ndarray):
        if len(bins)==2 and isinstance(bins[0], int) and isinstance(bins[1], int):
            xi = np.linspace(range[0][0], range[0][1], num=bins[0])
            yi = np.linspace(range[1][0], range[1][1], num=bins[1])
    
    #Create continuum grid from atomic information
    x0, y0 = np.meshgrid(xi, yi)
    
    grid = griddata((x, y), v, (x0, y0))
    
    return grid, range[0], range[1]

def prettygrid(grid, xedges, yedges, cmap=cm.get_cmap('jet'), propname='', czero=True, scale=1):

    #This scales the color plot to be fancy
    #czero=True makes zero the halfway point of the scale
    if czero:
        vmax = abs(grid).max()
        if vmax != 0.0:
            vrounder = np.floor(np.log10(vmax))
            vmax = np.around(2 * vmax / 10.**vrounder) * 10.**vrounder / 2.
        else:
            vmax = 1e-15
        vmin = -vmax
    else:
        vmax = grid.max()
        vmin = grid.min()
        if abs(grid).max() != 0.0:
            vrounder = np.floor(np.log10(abs(grid).max()))
            vmax = np.around(2 * vmax / 10.**vrounder) * 10.**vrounder / 2.
            vmin = np.around(2 * vmin / 10.**vrounder) * 10.**vrounder / 2.
            if vmax == vmin:
                if vmax > 0:
                    vmin = 0
                else:
                    vmax = 0
        else:
            vmax = 1e-15
            vmin = -1e-15
    vmin*=scale
    vmax*=scale
    
    vticks = np.linspace(vmin, vmax, 11, endpoint=True)

    #Plot figure on screen
    fig = plt.figure(figsize=(7.7, 7), dpi=72)
    plt.imshow(grid, extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]], 
               cmap=cmap, norm=plt.Normalize(vmax=vmax, vmin=vmin))
    
    #Make colorbar pretty
    cbar = plt.colorbar(fraction=0.05, pad = 0.05, ticks=vticks)
    cbar.ax.tick_params(labelsize=15)
   
    #Make axis values and title pretty
    plt.xlim(xedges[0], xedges[-1])
    plt.xticks(size=15)
    plt.ylim(yedges[0], yedges[-1])
    plt.yticks(size=15)
    plt.title(propname, size=30)
    return fig

def adddots(x,y,xedges,yedges):
    points = []
    ax = plt.gca()
    syswidth = max([abs(xedges[-1]-xedges[0]), abs(yedges[-1]-yedges[0])])
    linewidth = 60. / syswidth
    for i in xrange(len(x)):
        point = mpatches.Circle((x[i], y[i]), 0.3, ls='solid', lw=linewidth)
        ax.add_artist(point)
        point.set_facecolor('none')
        point.set_edgecolor('k')
        
def a2cplot(sys, value, plotbounds, bins=200, dots=True, czero=True, save=False, show=True):
    
    if save==False and show==False:
        print 'Figure not saved or displayed!'
    
    if sys.atoms[0].get(value) is None:
        raise ValueError('Atom value %s not found' % value)
    
    #Build arrays containing atomic information
    natoms = len(sys.atoms)    
    x = np.zeros(natoms)
    y = np.zeros(natoms)
    v = np.zeros(natoms)
    numv = 0
    for atom in sys.atoms:
        if atom.get('x') > plotbounds[0,0] - 5. and atom.get('x') < plotbounds[0,1] + 5.:
            if atom.get('y') > plotbounds[1,0] - 5. and atom.get('y') < plotbounds[1,1]+5.:
                if atom.get('z') > plotbounds[2,0] and atom.get('z') < plotbounds[2,1]:
                    x[numv] = atom.get('x')
                    y[numv] = atom.get('y')
                    v[numv] = atom.get(value)
                    numv +=1
    x = x[:numv]
    y = y[:numv]
    v = v[:numv]

    box = plotbounds[:2,:2]
    grid, xedges, yedges = grid_interpolate_2d(x, y, v, bins=bins, range=box)

    intsum = np.sum(grid)
    avsum = intsum / (bins-1) / (bins-1)
    intsum = intsum * (plotbounds[0,1]-plotbounds[0,0]) / (bins-1) * (plotbounds[1,1]-plotbounds[1,0]) / (bins-1)
        
    fig = prettygrid(grid, xedges, yedges, propname=value, czero=czero)
    if dots:
        adddots(x, y, xedges, yedges)
    if save:
        plt.savefig(str(value) + '.png', dpi=800)
    if show==False:
        plt.close(fig)
    plt.show() 
 
    return intsum, avsum