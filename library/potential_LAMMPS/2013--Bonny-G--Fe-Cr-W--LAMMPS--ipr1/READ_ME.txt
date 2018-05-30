The potentials in LAMMPS are read by the following three commands:

pair_style hybrid/overlay eam/alloy eam/fs
pair_coeff * * eam/alloy FeCr_d.eam.alloy Fe Cr
pair_coeff * * eam/fs FeCr_s.eam.fs Fe Cr