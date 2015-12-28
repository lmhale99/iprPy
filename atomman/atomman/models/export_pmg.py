try:
    import pymatgen as pmg
    has_pmg = True
except:
    has_pmg = False

def export_pmg(system, elements):
    assert has_pmg is True, 'PyMatGen not installed'
    lat_box = [system.box('avect'), system.box('bvect'), system.box('cvect')]
    latt = pmg.Lattice(lat_box)

    species = []
    sites = []
    properties = {}

    for i in xrange(system.natoms()):
        atype = system.atoms(i, 'atype')
        species.append(elements[atype-1])
        sites.append(system.atoms(i, 'pos', scale=True))
        for prop in system.atoms_prop_list():
            if prop == 'atype' or prop == 'pos':
                pass
            else:
                try:
                    properties[prop].append(system.atoms(i, prop))
                except:
                    properties[prop] = []
                    properties[prop].append(system.atoms(i, prop))

    return pmg.Structure(latt, species, sites, site_properties=properties)

