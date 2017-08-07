# Introduction

The refine_structure calculation refines the lattice parameters of an orthogonal system (crystal structure) by calculating the elastic constants, ``$C_{ij}$``, using small strains, and then iterating the box dimensions towards a given pressure. In refining the lattice parameter values, the box dimensions are allowed to relax, but the relative positions of the atoms within the box are held fixed. 

This calculations provides a quick tool for obtaining both the lattice and elastic constants for a given structure.

__Disclaimer #1__: With this method there is no guarantee that the resulting parameters are for a stable structure. Allowing internal relaxations may result in different values for some structures. Additionally, some transformation paths may be restricted from occurring due to symmetry, i.e. initially cubic structures may remain cubic instead of relaxing to a non-cubic structure.

__Disclaimer #2__: The elastic constants are estimated using small strains. Depending on the potential, the values for the elastic constants may vary with the size of the strain. This can come about either if the strain exceeds the linear elastic regime, or if the potential energy is not continuous to the fourth derivative. 
