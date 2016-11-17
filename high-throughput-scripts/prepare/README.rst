Prepare scripts
===============

This directory contains the prepare scripts associated with the different 
calculations. 

NOTE #1: The current prepare scripts have not been designed to check if a 
particular calculation has already been calculated. This means that identical 
duplicate calculations can be created. This feature was removed for the time 
being as the old methods were too slow.

NOTE #2: The current prepare scripts do not support preparing dependent 
calculations without the required parent calculations having been finished. 
Because of this, all calculations of a particular type should be prepared and 
executed before preparing a dependent calculation. This is planned to be fixed
soon.

NOTE #3: These scripts currently interact with a local record library 
directory. Plans are for adapting to automatically connecting with a MDCS 
server for saving and retrieving records.
 

Workflow
--------

The current workflow in design is:

1) E_vs_r_scan - Performs an energy vs. ideal r (nearest neighbor distance) 
   scan for a particular crystal structure and interatomic potential. 
   Identifies low energy configurations along the scan.

2) refine_structre or LAMMPS_ELASTIC - Both take the low energy configurations 
   identified by E_vs_r_scan, relax the system dimensions and evaluate the 
   elastic constants using small strains. 
   
   a) refine_structure - The system cell size is relaxed to the specified 
      pressure without relaxing local atomic configurations. The elastic 
      constants are taken by comparing the pressure at the +- strain values.
      
   b) LAMMPS_ELASTIC - Uses the ELASTIC denomstration script distributed with
      LAMMPS. Systems are refined with a minimization and box_relax. The 
      elastic constants algorithm averages values calculated for 0 to + and 0 
      to - the specified strain states.
      
3) The records produced by #2 provide crystal structures and elastic constants
   that are used by other calculations for constructing systems for evaluating 
   other properties. This includes the construction of defect containing 
   systems.
   
4) Defect systems created by one calculation can then be further analyzed and 
   changed by subsequent calculations. This is currently limited, as a routine
   is needed for directly loading systems from the calc.tar.gz archives.