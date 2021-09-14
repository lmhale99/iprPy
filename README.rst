=====
iprPy
=====

Introduction
------------

The iprPy framework provides

- The calculation methodology scripts used by the NIST Interatomic potentials
  Repository for evaluating crystalline and crystal defect materials properties,
- Tools allowing for users to interact with databases and the records contained
  within to easily explore the results of the calculations, and
- Workflow tools that allow for preparing and performing high throughput runs
  of the implemented calculation methods.

The design of the package aims for being user-friendly, open and transparent at
all levels.  To this end

- All code is open source,
- Calculation documentation and the Python code can be easily accessed and
  explored,
- Calculations can be performed individually or *en masse* using the workflow
  tools,
- Command line options allow for runs to be set up and performed with limited
  or no Python knowledge,
- Calculations are modular meaning that new methods can be easily added,
- Calculation methodology is separated from the workflow operations as much as
  possible,
- Implementation of new calculations can be supported by sharing input/output
  terms with existing calculations, and
- The results records are in a format that is both human and machine readable. 


Documentation
-------------

**NOTE: Updated documentation is coming soon!** The current documentation is old
and may not fully reflect the current state of iprPy (version 0.11).  This
section will be updated as the underlying documentation is fixed. For help using
the package, feel free to contact potentials@nist.gov. 

- Documentation can be found in the doc directory or by visiting 
  https://www.ctcms.nist.gov/potentials/iprPy/. **NOTE**: The general principles
  of the package remain true, but specifics are likely different with respect to
  the newest iprPy version.

- The notebook directory contains Jupyter Notebooks that outline how the
  implemented calculation methods work and provides an example run.  **NOTE**:
  The methods described in the Notebooks remain consistent with the current
  version of iprPy. However, some minor lines may differ relating to how the
  package integrates with the calculation.
