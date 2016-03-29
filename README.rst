=====
iprPy
=====

This is the homepage for the Python tools used in calculating material 
properties as predicted by classical atomistic models for the NIST 
Interatomic Potential Repository.

The project is divided into three major components:

1. `Demonstration Calculations`_

2. `Reference Library`_

3. `High-Throughput Calculation Tools`_

Demonstration Calculations 
==========================

The `demo-Notebooks`_ folder contains demonstration versions of all of the 
calculations in the form of Jupyter Notebooks.  This format was selected as it 
allows for a combination of the relevant Python code with formatted 
descriptions. As hosted on GitHub, the pages render clearly as HTML, and can be
easily downloaded where they can then be ran and modified by any who have 
Jupyter.  

Ideally, the implementation of the code in the Notebooks would directly 
correspond to the purely Python versions hosted with the high-throughput tools.
However, we have found that it is more practical to have the Notebook 
representations simplified by breaking calculation steps into smaller 
components. In this way, all functions and algorithms used are directly 
identical between the two formats, but the code for setting up and outputting 
the results does differ.

The implemented calculation Notebooks are:

- `calc_structure_static_1_E_vs_r`_

- `calc_structure_static_2_quick_a_Cij`_

- `calc_point_defect_formation`_

.. _demo-Notebooks: https://github.com/usnistgov/iprPy/tree/master/demo-Notebooks
.. _calc_structure_static_1_E_vs_r: https://github.com/usnistgov/iprPy/blob/master/demo-Notebooks/calc_structure_static_1_E_vs_r.ipynb
.. _calc_structure_static_2_quick_a_Cij: https://github.com/usnistgov/iprPy/blob/master/demo-Notebooks/calc_structure_static_2_quick_a_Cij.ipynb
.. _calc_point_defect_formation: https://github.com/usnistgov/iprPy/blob/master/demo-Notebooks/calc_point_defect_formation.ipynb

Reference Library
=================

The `reference-libraries`_ folder holds a collection of reference JSON data files 
and other files used in running the calculations.  The files are collected 
into folders according to what they represent:

- `potentials`_ contains JSON data files associated with LAMMPS implemented 
  atomic potentials, as well as a collection of potential parameter files. All 
  of the potentials collected in this folder are hosted on the Interatomic 
  Potential Repository. The JSON data files are used to generate 
  atomman.lammps.Potential objects that assist in running simulations by 
  dynamically constructing pair_style, pair_coeff LAMMPS commands, as well as 
  collecting other potential-specific parameters. 
  
- `prototypes`_ contains JSON data files associated with different crystal 
  prototype structures.  Each file contains metadata for the crystal prototype,
  as well as the necessary parameters for generating a system based on the 
  prototype.  These files can be read using atomman.models.crystal().

.. `point`_ contains JSON data files associated with different types of point 
  defects. Each file contains metadata for the defect, as well as the parameter 
  sets used by atomman.defects.point() for adding the defect to a system.  The 
  files are collected into folders named after the crystal prototypes that the 
  defects are for.

.. _reference-libraries: https://github.com/usnistgov/iprPy/tree/master/reference-libraries
.. _potentials: https://github.com/usnistgov/iprPy/tree/master/reference-libraries/potentials
.. _prototypes: https://github.com/usnistgov/iprPy/tree/master/reference-libraries/prototypes
.. _point: https://github.com/usnistgov/iprPy/tree/master/reference-libraries/point
  
  
High-Throughput Calculation Tools
=================================

**NOTE: the high-throughput tools are in active development. As such, there 
may be substantial changes made to how they operate and what they produce. 
Feel free to test the tools, but know that things may rapidly change and that 
for now there is no guarantee that the changes will be entirely additive (i.e
some features, steps, etc. may be removed).**

The `iprPy-tools`_ folder collects everything for performing the calculations
in a high-throughput manner.  This includes Python scripts associated with the
various calculations, as well as Python scripts for setting up the 
calculations, systematically running them, and processing their results.

Documentation related to the high-throughput tools can be found in the 
`README`_ file contained in the iprPy-tools directory.

.. _iprPy-tools: https://github.com/usnistgov/iprPy/tree/master/iprPy-tools
.. _README: https://github.com/usnistgov/iprPy/tree/master/iprPy-tools/README.rst