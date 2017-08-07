Contents
--------

The contents of each calculation folder are similar:

- README.md: A Markdown formatted text file that describes what the 
  calculation does and outlines all of the input parameters recognized by the 
  calc_[calcname].py and the prepare_[calcname].py scripts.

- calc_[calcname].py: The Python script for the calculation.

- calc_[calcname].template: A template version of the calculation input 
  parameter file. 

- prepare_[calcname].py: The Python script for high-throughput preparing 
  of the calculation.

- __init__.py: Tells the iprPy package to load the calculation folder 
  as a submodule, and defines the necessary functions for the iprPy.Calculation
  class.

- Any other files that the calculation script needs in order to run properly, 
  such as LAMMPS input script templates. 

For the calculations with corresponding demonstration notebooks, the 
docs/calculation-demonstration directory contains:
  
- calc_[calcname].ipynb: The Jupyter Notebook demonstration version of the
  calculation. This is where to look if you want to understand a calculation's 
  methodology.
  
- calc_[calcname]: Subdirectory for the files used or created by the 
  calculation Notebook.