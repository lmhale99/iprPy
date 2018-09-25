# elastic_constants_static Calculation

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2018-06-24

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

## Introduction

The elastic_constants_static calculation computes the elastic constants, $C_{ij}$, for a system by applying small strains and performing static energy minimizations of the initial and strained configurations.  Three estimates of the elastic constants are returned: one for applying positive strains, one for applying negative strains, and a normalized estimate that averages the &pm; strains and the symmetric components of the $C_{ij}$ tensor.

__Version notes__: This calculation and relax_static replace the previous LAMMPS_ELASTIC calculation style.

__Disclaimer #1__: Unlike the previous LAMMPS_ELASTIC calculation, this calculation does *not* perform a box relaxation on the system prior to evaluating the elastic constants.  This allows for the static elastic constants to be evaluated for systems that are relaxed to different pressures.

__Disclaimer #2__: The elastic constants are estimated using small strains.  Depending on the potential, the values for the elastic constants may vary with the size of the strain.  This can come about either if the strain exceeds the linear elastic regime.

__Disclaimer #3__: Some classical interatomic potentials have discontinuities in the fourth derivative of the energy function with respect to position.  If the strained states straddle one of these discontinuities the resulting static elastic constants values will be nonsense.