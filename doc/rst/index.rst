
iprPy High-Throughput Computational Framework
*********************************************


Description
===========

The iprPy framework is a collection of tools and resources supporting
the design of scientific calculations that

* are open source with minimum barriers for usage,

* have transparent methodologies supporting knowledge transfer and
  education,

* produce results that are both human and machine readable,

* allow investigations into method and parameter sensitivity,

* and can be integrated into workflows.

The framework was originally created to support the NIST Interatomic
Potential Repository by evaluating basic materials properties across
multiple classical interatomic potentials.  Because of this, many of
the included calculations and tools are designed towards molecular
dynamics simulations.


Documentation Sections
======================

`Introduction to iprPy <intro.rst>`_

A quick introduction describing why you would want to use the iprPy
framework.

`Setup <setup.rst>`_

Describes the basics of iprPy for performing calculations.

`iprPy Basics <basics/index.rst>`_

Learn about the different components of the iprPy framework, how to
run calculations, and how to add your own content.

Jupyter Notebooks

Jupyter Notebooks are provided for all implemented calculations that
fully document the calculation methodologies, contain identical Python
code to the calculations, and demonstrate a single run.

`iprPy <modules/index.rst>`_

The Python docstring information for the functions and classes of
iprPy.


Contents
========

Contents:

* `Introduction to iprPy <intro.rst>`_
  * `Scientific research work process
    <intro.rst#scientific-research-work-process>`_
  * `Complications <intro.rst#complications>`_
  * `It’s all in the design <intro.rst#its-all-in-the-design>`_
  * `How much extra work? <intro.rst#how-much-extra-work>`_
* `Setup <setup.rst>`_
  * `Installing iprPy <setup.rst#installing-iprpy>`_
  * `Updating iprPy <setup.rst#updating-iprpy>`_
  * `Uninstalling iprPy <setup.rst#uninstalling-iprpy>`_
* `iprPy Basics <basics/index.rst>`_
  * `Calculations <basics/calculation.rst>`_
    * `Location of Calculations
      <basics/calculation.rst#location-of-calculations>`_
    * `Run a Calculation <basics/calculation.rst#run-a-calculation>`_
      * `Run the Jupyter Notebook
        <basics/calculation.rst#run-the-jupyter-notebook>`_
      * `Run the calculation script
        <basics/calculation.rst#run-the-calculation-script>`_
      * `Prepare and run in high-throughput
        <basics/calculation.rst#prepare-and-run-in-high-throughput>`_
  * `Input Parameter File <basics/inputfile.rst>`_
    * `Formating rules <basics/inputfile.rst#formating-rules>`_
    * `Formatting example <basics/inputfile.rst#formatting-example>`_
    * `Easy creation <basics/inputfile.rst#easy-creation>`_
  * `XML/JSON Records <basics/recordformat.rst>`_
    * `Reusable types <basics/recordformat.rst#reusable-types>`_
    * `Record identification and hierarchy
      <basics/recordformat.rst#record-identification-and-hierarchy>`_
    * `System families <basics/recordformat.rst#system-families>`_
  * `Reference Library <basics/library.rst>`_
    * `crystal_prototype records
      <basics/library.rst#crystal-prototype-records>`_
    * `potential_LAMMPS records
      <basics/library.rst#potential-lammps-records>`_
    * `Defect records <basics/library.rst#defect-records>`_
* `High-Throughput Tools <highthroughput/index.rst>`_
  * `Quick Start <highthroughput/quickstart.rst>`_
  * `iprPy Classes <highthroughput/classes.rst>`_
    * `Calculation <highthroughput/classes.rst#calculation>`_
    * `Record <highthroughput/classes.rst#record>`_
    * `Database <highthroughput/classes.rst#database>`_
  * `Prepare <highthroughput/prepare.rst>`_
    * `Introduction <highthroughput/prepare.rst#introduction>`_
    * `Notes on run_directory naming
      <highthroughput/prepare.rst#notes-on-run-directory-naming>`_
    * `How to prepare <highthroughput/prepare.rst#how-to-prepare>`_
      * `Inline prepare <highthroughput/prepare.rst#inline-prepare>`_
      * `Running a prepare script
        <highthroughput/prepare.rst#running-a-prepare-script>`_
      * `Calculation.prepare() method
        <highthroughput/prepare.rst#calculation-prepare-method>`_
    * `Prepare parameters
      <highthroughput/prepare.rst#prepare-parameters>`_
  * `Runner <highthroughput/runner.rst>`_
    * `Introduction <highthroughput/runner.rst#introduction>`_
    * `Starting runners <highthroughput/runner.rst#starting-runners>`_
      * `Runner script <highthroughput/runner.rst#runner-script>`_
      * `Inline command <highthroughput/runner.rst#inline-command>`_
      * `Call from Python
        <highthroughput/runner.rst#call-from-python>`_
      * `Submitting to a queue
        <highthroughput/runner.rst#submitting-to-a-queue>`_
    * `Full process <highthroughput/runner.rst#full-process>`_
    * `Runner log files <highthroughput/runner.rst#runner-log-files>`_
  * `Other High-Throughput Tools <highthroughput/inline.rst>`_
    * `build <highthroughput/inline.rst#build>`_
    * `check <highthroughput/inline.rst#check>`_
    * `check_modules <highthroughput/inline.rst#check-modules>`_
    * `clean <highthroughput/inline.rst#clean>`_
    * `copy <highthroughput/inline.rst#copy>`_
    * `destroy <highthroughput/inline.rst#destroy>`_
    * `set <highthroughput/inline.rst#set>`_
    * `unset <highthroughput/inline.rst#unset>`_
  * `Analysis <highthroughput/analysis.rst>`_
    * `Accessing the data
      <highthroughput/analysis.rst#accessing-the-data>`_
    * `Analyzing the data
      <highthroughput/analysis.rst#analyzing-the-data>`_
* `Adding Content to iprPy <extend/index.rst>`_
  * `Adding new potentials <extend/add_potential.rst>`_
    * `Assign Potential and Implementation keys and id’s
      <extend/add_potential.rst#assign-potential-and-implementation-keys-and-ids>`_
      * `Potential keys and id’s
        <extend/add_potential.rst#potential-keys-and-ids>`_
      * `Implementation keys and id’s
        <extend/add_potential.rst#implementation-keys-and-ids>`_
      * `Example id’s <extend/add_potential.rst#example-ids>`_
      * `New Potential vs. New Implementation
        <extend/add_potential.rst#new-potential-vs-new-implementation>`_
    * `Creating a potential_LAMMPS record
      <extend/add_potential.rst#creating-a-potential-lammps-record>`_
      * `"potential-LAMMPS"
        <extend/add_potential.rst#potential-lammps>`_
      * `"key" <extend/add_potential.rst#key>`_
      * `"id" <extend/add_potential.rst#id>`_
      * `"potential" <extend/add_potential.rst#potential>`_
      * `"units" <extend/add_potential.rst#units>`_
      * `"atom_style" <extend/add_potential.rst#atom-style>`_
      * `"atom" <extend/add_potential.rst#atom>`_
      * `"pair_style" <extend/add_potential.rst#pair-style>`_
      * `"pair_coeff" <extend/add_potential.rst#pair-coeff>`_
      * `"command" <extend/add_potential.rst#command>`_
      * `"term" <extend/add_potential.rst#term>`_
    * `Examples <extend/add_potential.rst#examples>`_
      * `Simple pair styles
        <extend/add_potential.rst#simple-pair-styles>`_
      * `Original EAM style
        <extend/add_potential.rst#original-eam-style>`_
      * `Many-body potentials
        <extend/add_potential.rst#many-body-potentials>`_
      * `Many-body potentials with library files
        <extend/add_potential.rst#many-body-potentials-with-library-files>`_
      * `hybrid and hybrid/overlay styles
        <extend/add_potential.rst#hybrid-and-hybrid-overlay-styles>`_
  * `Adding new library parameter records
    <extend/add_parameter_record.rst>`_
    * `crystal_prototype record style
      <extend/add_parameter_record.rst#crystal-prototype-record-style>`_
    * `Defect record styles
      <extend/add_parameter_record.rst#defect-record-styles>`_
  * `Creating Calculation Styles <extend/add_calculation_style.rst>`_
    * `Calculation scripts
      <extend/add_calculation_style.rst#calculation-scripts>`_
      * `Requirements
        <extend/add_calculation_style.rst#requirements>`_
      * `Design guidelines
        <extend/add_calculation_style.rst#design-guidelines>`_
    * `Implementing a Calculation Style into iprPy
      <extend/add_calculation_style.rst#implementing-a-calculation-style-into-iprpy>`_
      * `Calculation Documentation
        <extend/add_calculation_style.rst#calculation-documentation>`_
  * `LAMMPS Calculations Using atomman <extend/calc_atomman.rst>`_
    * `Input function design
      <extend/calc_atomman.rst#input-function-design>`_
    * `List of basic atomman-based input functions
      <extend/calc_atomman.rst#list-of-basic-atomman-based-input-functions>`_
  * `Generating a Prepare Script <extend/calc_prepare.rst>`_
    * `Functions of the prepare script
      <extend/calc_prepare.rst#functions-of-the-prepare-script>`_
    * `The prepare() function
      <extend/calc_prepare.rst#the-prepare-function>`_
    * `Functions of iprPy.prepare submodule
      <extend/calc_prepare.rst#functions-of-iprpy-prepare-submodule>`_
  * `Constructing Record Styles <extend/add_record_style.rst>`_
    * `Limitations to XML
      <extend/add_record_style.rst#limitations-to-xml>`_
    * `Limitations to JSON
      <extend/add_record_style.rst#limitations-to-json>`_
    * `Limitations to Python dictionaries
      <extend/add_record_style.rst#limitations-to-python-dictionaries>`_
  * `Constructing Database Styles <extend/add_database_style.rst>`_
* `Calculation Styles <calculation_styles.rst>`_
  * `E_vs_r_scan <calculations/E_vs_r_scan/index.rst>`_
    * `Introduction <calculations/E_vs_r_scan/intro.rst>`_
    * `Method and Theory <calculations/E_vs_r_scan/theory.rst>`_
    * `calc_E_vs_r_scan.py <calculations/E_vs_r_scan/calc.rst>`_
      * `Calculation script functions
        <calculations/E_vs_r_scan/calc.rst#module-iprPy.calculations.E_vs_r_scan.calc_E_vs_r_scan>`_
  * `LAMMPS_ELASTIC <calculations/LAMMPS_ELASTIC/index.rst>`_
    * `Introduction <calculations/LAMMPS_ELASTIC/intro.rst>`_
    * `Method and Theory <calculations/LAMMPS_ELASTIC/theory.rst>`_
    * `calc_LAMMPS_ELASTIC.py <calculations/LAMMPS_ELASTIC/calc.rst>`_
      * `Calculation script functions
        <calculations/LAMMPS_ELASTIC/calc.rst#module-iprPy.calculations.LAMMPS_ELASTIC.calc_LAMMPS_ELASTIC>`_
  * `dislocation_monopole
    <calculations/dislocation_monopole/index.rst>`_
    * `Introduction <calculations/dislocation_monopole/intro.rst>`_
    * `Method and Theory
      <calculations/dislocation_monopole/theory.rst>`_
    * `calc_dislocation_monopole.py
      <calculations/dislocation_monopole/calc.rst>`_
      * `Calculation script functions
        <calculations/dislocation_monopole/calc.rst#module-iprPy.calculations.dislocation_monopole.calc_dislocation_monopole>`_
  * `dynamic_relax <calculations/dynamic_relax/index.rst>`_
    * `Introduction <calculations/dynamic_relax/intro.rst>`_
    * `Method and Theory <calculations/dynamic_relax/theory.rst>`_
    * `calc_dynamic_relax.py <calculations/dynamic_relax/calc.rst>`_
      * `Calculation script functions
        <calculations/dynamic_relax/calc.rst#module-iprPy.calculations.dynamic_relax.calc_dynamic_relax>`_
  * `point_defect_diffusion
    <calculations/point_defect_diffusion/index.rst>`_
    * `Introduction <calculations/point_defect_diffusion/intro.rst>`_
    * `Method and Theory
      <calculations/point_defect_diffusion/theory.rst>`_
    * `calc_point_defect_diffusion.py
      <calculations/point_defect_diffusion/calc.rst>`_
      * `Calculation script functions
        <calculations/point_defect_diffusion/calc.rst#module-iprPy.calculations.point_defect_diffusion.calc_point_defect_diffusion>`_
  * `point_defect_static
    <calculations/point_defect_static/index.rst>`_
    * `Introduction <calculations/point_defect_static/intro.rst>`_
    * `Method and Theory
      <calculations/point_defect_static/theory.rst>`_
    * `calc_point_defect_static.py
      <calculations/point_defect_static/calc.rst>`_
      * `Calculation script functions
        <calculations/point_defect_static/calc.rst#module-iprPy.calculations.point_defect_static.calc_point_defect_static>`_
  * `refine_structure <calculations/refine_structure/index.rst>`_
    * `Introduction <calculations/refine_structure/intro.rst>`_
    * `Method and Theory <calculations/refine_structure/theory.rst>`_
    * `calc_refine_structure.py
      <calculations/refine_structure/calc.rst>`_
      * `Calculation script functions
        <calculations/refine_structure/calc.rst#module-iprPy.calculations.refine_structure.calc_refine_structure>`_
  * `stacking_fault <calculations/stacking_fault/index.rst>`_
    * `Introduction <calculations/stacking_fault/intro.rst>`_
    * `Method and Theory <calculations/stacking_fault/theory.rst>`_
    * `calc_stacking_fault.py <calculations/stacking_fault/calc.rst>`_
      * `Calculation script functions
        <calculations/stacking_fault/calc.rst#module-iprPy.calculations.stacking_fault.calc_stacking_fault>`_
  * `stacking_fault_multi
    <calculations/stacking_fault_multi/index.rst>`_
    * `Introduction <calculations/stacking_fault_multi/intro.rst>`_
    * `Method and Theory
      <calculations/stacking_fault_multi/theory.rst>`_
    * `calc_stacking_fault_multi.py
      <calculations/stacking_fault_multi/calc.rst>`_
      * `Calculation script functions
        <calculations/stacking_fault_multi/calc.rst#module-iprPy.calculations.stacking_fault_multi.calc_stacking_fault_multi>`_
  * `surface_energy <calculations/surface_energy/index.rst>`_
    * `Introduction <calculations/surface_energy/intro.rst>`_
    * `Method and Theory <calculations/surface_energy/theory.rst>`_
    * `calc_surface_energy.py <calculations/surface_energy/calc.rst>`_
      * `Calculation script functions
        <calculations/surface_energy/calc.rst#module-iprPy.calculations.surface_energy.calc_surface_energy>`_
* `Record Styles <record_styles.rst>`_
  * `calculation_cohesive_energy_relation
    <records/calculation_cohesive_energy_relation/index.rst>`_
    * `Introduction
      <records/calculation_cohesive_energy_relation/intro.rst>`_
  * `calculation_dislocation_monopole
    <records/calculation_dislocation_monopole/index.rst>`_
    * `Introduction
      <records/calculation_dislocation_monopole/intro.rst>`_
  * `calculation_dynamic_relax
    <records/calculation_dynamic_relax/index.rst>`_
    * `Introduction <records/calculation_dynamic_relax/intro.rst>`_
  * `calculation_generalized_stacking_fault
    <records/calculation_generalized_stacking_fault/index.rst>`_
    * `Introduction
      <records/calculation_generalized_stacking_fault/intro.rst>`_
  * `calculation_point_defect_diffusion
    <records/calculation_point_defect_diffusion/index.rst>`_
    * `Introduction
      <records/calculation_point_defect_diffusion/intro.rst>`_
  * `calculation_point_defect_formation
    <records/calculation_point_defect_formation/index.rst>`_
    * `Introduction
      <records/calculation_point_defect_formation/intro.rst>`_
  * `calculation_stacking_fault
    <records/calculation_stacking_fault/index.rst>`_
    * `Introduction <records/calculation_stacking_fault/intro.rst>`_
  * `calculation_surface_energy
    <records/calculation_surface_energy/index.rst>`_
    * `Introduction <records/calculation_surface_energy/intro.rst>`_
  * `calculation_system_relax
    <records/calculation_system_relax/index.rst>`_
    * `Introduction <records/calculation_system_relax/intro.rst>`_
  * `crystal_prototype <records/crystal_prototype/index.rst>`_
    * `Introduction <records/crystal_prototype/intro.rst>`_
  * `dislocation_monopole <records/dislocation_monopole/index.rst>`_
    * `Introduction <records/dislocation_monopole/intro.rst>`_
  * `free_surface <records/free_surface/index.rst>`_
    * `Introduction <records/free_surface/intro.rst>`_
  * `point_defect <records/point_defect/index.rst>`_
    * `Introduction <records/point_defect/intro.rst>`_
  * `potential_LAMMPS <records/potential_LAMMPS/index.rst>`_
    * `Introduction <records/potential_LAMMPS/intro.rst>`_
  * `stacking_fault <records/stacking_fault/index.rst>`_
    * `Introduction <records/stacking_fault/intro.rst>`_
* `Database Styles <database_styles.rst>`_
  * `curator <databases/curator/index.rst>`_
    * `Introduction <databases/curator/intro.rst>`_
      * `Style requirements
        <databases/curator/intro.rst#style-requirements>`_
      * `Initialization arguments:
        <databases/curator/intro.rst#initialization-arguments>`_
      * `Additional notes:
        <databases/curator/intro.rst#additional-notes>`_
  * `local <databases/local/index.rst>`_
    * `Introduction <databases/local/intro.rst>`_
      * `Style requirements
        <databases/local/intro.rst#style-requirements>`_
      * `Initialization arguments:
        <databases/local/intro.rst#initialization-arguments>`_
      * `Additional notes:
        <databases/local/intro.rst#additional-notes>`_
* `iprPy <modules/index.rst>`_
  * `iprPy package <modules/iprPy.rst>`_
    * `Subpackages <modules/iprPy.rst#subpackages>`_
      * `iprPy.calculations package <modules/iprPy.calculations.rst>`_
      * `iprPy.databases package <modules/iprPy.databases.rst>`_
      * `iprPy.highthroughput package
        <modules/iprPy.highthroughput.rst>`_
      * `iprPy.input package <modules/iprPy.input.rst>`_
      * `iprPy.prepare package <modules/iprPy.prepare.rst>`_
      * `iprPy.records package <modules/iprPy.records.rst>`_
      * `iprPy.tools package <modules/iprPy.tools.rst>`_
    * `Module contents <modules/iprPy.rst#module-iprPy>`_

Indices and tables
==================

* `Index <genindex.rst>`_

* `Module Index <py-modindex.rst>`_

* `Search Page <search.rst>`_
