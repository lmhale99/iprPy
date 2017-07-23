========
Overview
========

To accomplish the goals outlined in the Introduction, iprPy consists of many components that work together. Not all of these components are code, and in fact some are little more than design guidelines or suggested best practices. This section gives an overview of the different components. More detailed information can be found in the later sections relating to each part of iprPy.

- The calculations themselves consist of Python scripts and any supporting files. Each calculation is designed to be a complete and independent unit of work, which reads all input parameters from a structured input file and produces XML records of the calculation’s metadata and processed data.
- High-throughput scripts are provided for preparing and running multiple instances of each calculation. In this framework, the XML records and raw simulation data are automatically added to a specified database.
- The included iprPy package provides functions and tools supporting rapid design of calculations and high-throughput scripts by allowing for the sharing of common code and parameter definitions. The iprPy package also treats the calculation scripts, XML record formats, and types of databases modularly allowing for new instances of each to be easily added.
- A library of JSON/XML reference data is also included that collects together meaningful parameter sets. For example, the parameters for different crystal prototypes, defect configurations, and the metadata associated with interatomic potentials.
- Primary documentation for the functions and methods of the iprPy package, as well as descriptions of the calculation methods and the meaning of the different parameters is included as Jupyter Notebooks.
The final component is not a direct part of iprPy, but is currently being used for most of the implemented calculations.
- atomman is a Python package designed for supporting MD simulations. In particular, it allows for the creation, and manipulation of atomic systems, and provides a wrapper around the LAMMPS MD software. This makes it possible to design calculations as single Python scripts that setup, perform and analyze one or more LAMMPS simulations. More information can be found at the atomman GitHub page: https://github.com/usnistgov/atomman
