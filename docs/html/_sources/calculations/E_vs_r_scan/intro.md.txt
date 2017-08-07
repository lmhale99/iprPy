# Introduction

The E_vs_r_scan calculation calculation creates a plot of the cohesive energy vs 
interatomic spacing, ``$r$``, for a given atomic system. The system size is 
uniformly scaled (``$b/a$`` and ``$c/a$`` ratios held fixed) and the energy is 
calculated at a number of sizes without relaxing the system. All box sizes 
corresponding to energy minima are identified. 

This calculation was created as a quick method for scanning the phase space of a
crystal structure with a given potential in order to identify starting guesses 
for further structure refinement calculations.

__Disclaimer #1__: the minima identified by this calculation do not guarantee 
that the associated crystal structure will be stable as no relaxation is 
performed by this calculation. Upon relaxation, the atomic positions and box 
dimensions may transform the system to a different structure

__Disclaimer #2__: it is possible that the calculation may miss an existing 
minima for a crystal structure if it is outside the range of ``$r$`` values scanned,
or has ``$b/a$``, ``$c/a$`` values far from the ideal.