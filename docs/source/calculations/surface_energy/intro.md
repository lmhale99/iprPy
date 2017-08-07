# Introduction

The __surface_energy__ calculation evaluates the formation energy for a free surface by slicing an atomic system along a specific plane.

__Disclaimer #1__: Other atomic configurations at the free surface for certain planar cuts may have lower energies. The atomic relaxation will find a local minimum, which may not be the global minimum. Additionally, the material cut is planar perfect and therefore does not explore the effects of atomic roughness.

__Disclaimer #2__: Currently, the rotation capabilities of atomman limit this calculation such that only cubic prototypes can be rotated. Properties of non-cubic structures can still be explored, as long as the configuration being loaded has the plane of interest perpendicular to one of the three box vectors.