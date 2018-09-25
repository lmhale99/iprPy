
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

`Calculations <run/index.rst>`_

Learn about the different components of the iprPy framework and how to
run calculations.

`Calculation Styles <calculation_styles.rst>`_

Describes the implemented calculations and what input parameters the
calculation scripts use.

`Jupyter Demonstration Notebooks <notebook_styles.rst>`_

Provides demonstration Jupyter Notebooks for the implemented
calculations.

`Record Styles <record_styles.rst>`_

Describes the implemented record formats for storing calculation data.

`Database Styles <database_styles.rst>`_

Describes the implemented database types that can be interacted with.

`Extending iprPy <extend/index.rst>`_

This describes the components of iprPy in more detail for those who
want to contribute to the package by adding content.

`iprPy package <iprPy/index.rst>`_

The Python docstring information for the functions and classes of
iprPy.


Package Tutorials
=================

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
* `Calculations <run/index.rst>`_
  * `Run a Jupyter Calculation Notebook <run/notebook.rst>`_
    * `Notebook Overview <run/notebook.rst#notebook-overview>`_
  * `Execute a Calculation Script <run/single.rst>`_
    * `Calculation directories
      <run/single.rst#calculation-directories>`_
    * `Calculation input/template file
      <run/single.rst#calculation-input-template-file>`_
    * `Running the calculation script
      <run/single.rst#running-the-calculation-script>`_
    * `Looking at the results
      <run/single.rst#looking-at-the-results>`_
  * `High-Throughput Calculation Execution <run/htp.rst>`_
    * `Define <run/htp.rst#define>`_
    * `Build <run/htp.rst#build>`_
    * `Prepare <run/htp.rst#prepare>`_
    * `Runner <run/htp.rst#runner>`_
    * `Access <run/htp.rst#access>`_
  * `Command Line Actions <run/inline.rst>`_
    * `Define <run/inline.rst#define>`_
    * `Build <run/inline.rst#build>`_
    * `Prepare <run/inline.rst#prepare>`_
    * `Runner <run/inline.rst#runner>`_
    * `Other <run/inline.rst#other>`_
* `Extending iprPy <extend/index.rst>`_
  * `iprPy Package Overview <extend/overview.rst>`_
    * `Conceptual Components of iprPy
      <extend/overview.rst#conceptual-components-of-iprpy>`_
    * `Modular Components of the iprPy Package
      <extend/overview.rst#modular-components-of-the-iprpy-package>`_
  * `Reference Library <extend/addreference.rst>`_
  * `Records <extend/addrecord.rst>`_
    * `Record directories <extend/addrecord.rst#record-directories>`_
    * `Record format <extend/addrecord.rst#record-format>`_
      * `Reusable types <extend/addrecord.rst#reusable-types>`_
      * `Common components and design
        <extend/addrecord.rst#common-components-and-design>`_
    * `Record Classes <extend/addrecord.rst#record-classes>`_
      * `Common Record properties
        <extend/addrecord.rst#common-record-properties>`_
      * `Common Record methods
        <extend/addrecord.rst#common-record-methods>`_
      * `Defining a new Record class
        <extend/addrecord.rst#defining-a-new-record-class>`_
    * `Record format limitations
      <extend/addrecord.rst#record-format-limitations>`_
      * `Limitations to XML
        <extend/addrecord.rst#limitations-to-xml>`_
      * `Limitations to JSON
        <extend/addrecord.rst#limitations-to-json>`_
      * `Limitations to Python dictionaries
        <extend/addrecord.rst#limitations-to-python-dictionaries>`_
  * `Calculations <extend/addcalculation.rst>`_
    * `Calculation directories
      <extend/addcalculation.rst#calculation-directories>`_
    * `Calculation script
      <extend/addcalculation.rst#calculation-script>`_
      * `Script design <extend/addcalculation.rst#script-design>`_
    * `Calculation input template
      <extend/addcalculation.rst#calculation-input-template>`_
    * `Calculation class
      <extend/addcalculation.rst#calculation-class>`_
      * `Common Calculation properties
        <extend/addcalculation.rst#common-calculation-properties>`_
      * `Common Calculation methods
        <extend/addcalculation.rst#common-calculation-methods>`_
      * `Defining a new Calculation class
        <extend/addcalculation.rst#defining-a-new-calculation-class>`_
  * `Modular functions <extend/addfunctions.rst>`_
    * `iprPy.input.buildcombos
      <extend/addfunctions.rst#iprpy-input-buildcombos>`_
    * `iprPy.input.interpret
      <extend/addfunctions.rst#iprpy-input-interpret>`_
  * `Databases <extend/adddatabase.rst>`_
    * `Database directories
      <extend/adddatabase.rst#database-directories>`_
      * `Database classes <extend/adddatabase.rst#database-classes>`_

Implemented Content
===================

Contents:

* `Calculation Styles <calculation_styles.rst>`_
  * `E_vs_r_scan <calculation/E_vs_r_scan/index.rst>`_
  * `crystal_space_group <calculation/crystal_space_group/index.rst>`_
  * `dislocation_SDVPN <calculation/dislocation_SDVPN/index.rst>`_
  * `dislocation_monopole
    <calculation/dislocation_monopole/index.rst>`_
  * `elastic_constants_static
    <calculation/elastic_constants_static/index.rst>`_
  * `point_defect_diffusion
    <calculation/point_defect_diffusion/index.rst>`_
  * `point_defect_static <calculation/point_defect_static/index.rst>`_
  * `relax_box <calculation/relax_box/index.rst>`_
  * `relax_dynamic <calculation/relax_dynamic/index.rst>`_
  * `relax_static <calculation/relax_static/index.rst>`_
  * `stacking_fault_map_2D
    <calculation/stacking_fault_map_2D/index.rst>`_
  * `stacking_fault_static
    <calculation/stacking_fault_static/index.rst>`_
  * `surface_energy_static
    <calculation/surface_energy_static/index.rst>`_
* `Jupyter Demonstration Notebooks <notebook_styles.rst>`_
  * `E_vs_r_scan Calculation <notebook/E_vs_r_scan.rst>`_
  * `crystal_space_group Calculation
    <notebook/crystal_space_group.rst>`_
  * `dislocation_SDVPN Calculation <notebook/dislocation_SDVPN.rst>`_
  * `dislocation_monopole Calculation
    <notebook/dislocation_monopole.rst>`_
  * `elastic_constants_static Calculation
    <notebook/elastic_constants_static.rst>`_
  * `point_defect_diffusion Calculation
    <notebook/point_defect_diffusion.rst>`_
  * `point_defect_static Calculation
    <notebook/point_defect_static.rst>`_
  * `relax_box Calculation <notebook/relax_box.rst>`_
  * `relax_dynamic Calculation <notebook/relax_dynamic.rst>`_
  * `relax_static Calculation <notebook/relax_static.rst>`_
  * `stacking_fault_map_2D Calculation
    <notebook/stacking_fault_map_2D.rst>`_
  * `stacking_fault_static Calculation
    <notebook/stacking_fault_static.rst>`_
  * `surface_energy Calculation <notebook/surface_energy_static.rst>`_
* `Record Styles <record_styles.rst>`_
  * `calculation_E_vs_r_scan
    <record/calculation_E_vs_r_scan/index.rst>`_
  * `calculation_crystal_space_group
    <record/calculation_crystal_space_group/index.rst>`_
  * `calculation_dislocation_SDVPN
    <record/calculation_dislocation_SDVPN/index.rst>`_
  * `calculation_dislocation_monopole
    <record/calculation_dislocation_monopole/index.rst>`_
  * `calculation_elastic_constants_static
    <record/calculation_elastic_constants_static/index.rst>`_
  * `calculation_point_defect_diffusion
    <record/calculation_point_defect_diffusion/index.rst>`_
  * `calculation_point_defect_static
    <record/calculation_point_defect_static/index.rst>`_
  * `calculation_relax_box <record/calculation_relax_box/index.rst>`_
  * `calculation_relax_dynamic
    <record/calculation_relax_dynamic/index.rst>`_
  * `calculation_relax_static
    <record/calculation_relax_static/index.rst>`_
  * `calculation_stacking_fault_map_2D
    <record/calculation_stacking_fault_map_2D/index.rst>`_
  * `calculation_stacking_fault_static
    <record/calculation_stacking_fault_static/index.rst>`_
  * `calculation_surface_energy_static
    <record/calculation_surface_energy_static/index.rst>`_
  * `crystal_prototype <record/crystal_prototype/index.rst>`_
  * `dislocation_monopole <record/dislocation_monopole/index.rst>`_
  * `free_surface <record/free_surface/index.rst>`_
  * `per_potential_properties
    <record/per_potential_properties/index.rst>`_
  * `point_defect <record/point_defect/index.rst>`_
  * `potential_LAMMPS <record/potential_LAMMPS/index.rst>`_
  * `potential_openKIM_LAMMPS
    <record/potential_openKIM_LAMMPS/index.rst>`_
  * `stacking_fault <record/stacking_fault/index.rst>`_
* `Database Styles <database_styles.rst>`_
  * `curator <database/curator/index.rst>`_
  * `local <database/local/index.rst>`_

Code Documentation
==================

* `iprPy package <iprPy/index.rst>`_
  * `Subpackages <iprPy/index.rst#subpackages>`_
    * `iprPy.calculation package <iprPy/calculation.rst>`_
    * `iprPy.compatibility package <iprPy/compatibility.rst>`_
    * `iprPy.database package <iprPy/database.rst>`_
    * `iprPy.input package <iprPy/input.rst>`_
    * `iprPy.record package <iprPy/record.rst>`_
    * `iprPy.tools package <iprPy/tools.rst>`_
  * `Module contents <iprPy/index.rst#module-iprPy>`_

Indices and tables
==================

* `Index <genindex.rst>`_

* `Module Index <py-modindex.rst>`_

* `Search Page <search.rst>`_
