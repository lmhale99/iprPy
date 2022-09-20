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

- Documentation can be found in the doc directory or by visiting 
  https://www.ctcms.nist.gov/potentials/iprPy/. 

- The notebook directory contains Jupyter Notebooks that outline how the
  implemented calculation methods work and provides an example run.

- For help using the package, feel free to contact potentials@nist.gov or
  submit an issue or pull request to the https://github.com/lmhale99/iprPy
  github repository. 
