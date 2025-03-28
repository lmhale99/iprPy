# melting_temperature calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The melting_temperature calculation style attempts to determine the melting temperature for an element by constructing a two-phase system consisting of half solid and half liquid, then relaxing the system with an nph simulation.  If the initial guess temperature is close to the melting temperature, then it is expected that the system will equilibrate towards the melting temperature as one phase transforms into the other.  Good direct estimates for the melting temperature are obtained when the final configuration retains substantial amounts of both phases.

### Version notes

- 0.11.4: calculation method added.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

- Good estimates require the existence of both phases at the end of the simulation in substantial amounts.  This typically requires iterating the simulation multiple times where the input guess temperature is updated until the fraction of both phases falls within some target range.  Note that there is only a loose correspondence between the guess temperature and the equilibrium temperature, so iterations need to be based on phase amounts not output temperatures!

- The calculation method uses polyhedral template matching (ptm) to provide an automatic estimate of the solid phase amount.  The ptm method requires specifying which crystal structure(s) are expected and estimates are based on that.  For crystal structures not currently supported by ptm, you will need to estimate the phases yourself using the generated dump files.

- The melting temperature is sensitive to the choice of the solid phase and multiple estimates can be possible if multiple solid phases are (meta)stable at high temperatures.

- This method is designed for estimating the melting temperature for single element systems.