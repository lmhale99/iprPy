## Method and Theory

An initial system (and corresponding unit cell system) is supplied. The ``$r/a$`` ratio is identified from the unit cell. The system is then uniformly scaled to all ``$r_i$`` values in the range to be explored and the energy for each is evaluated using LAMMPS and "run 0" command. 

In identifying energy minima along the curve, only the explored values are used without interpolation. In this way, the possible energy minima structures are identified for ``$r_i$`` where ``$E(r_i) < E(r_{i-1})$`` and ``$E(r_i) < E(r_{i+1})$``.