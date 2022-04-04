========================
Adding new subset styles
========================

This page outlines how to add a new calculation subset to iprPy.  Creating a subset allows for multiple calculations to share some of the same input parameters and for those terms to be managed in a consistent manner across the calculations.

1. Class definition
===================

Python files that define a subset should be placed inside the iprPy/calculation_subset folder.  Currently each class definition is contained in a separate Python file named for the calculation subset class.  When defining the class, it should have an informative name and inherit from iprPy.calculation_subset.CalculationSubset.  Once the class is created, it should be imported by iprPy/calculation_subset/\_\_init\_\_.py.

2. Calculation-like methods and attributes
==========================================

As a subset represents a set of inputs for Calculations, most of the method and attribute definitions in a subset correspond closely to how they are defined in the Calculation objects.  See the previous doc page for more details on the related Calculation methods and attributes.

- The class initializer should pass all parameters to the parent class and set default values for the class attributes.
- Class attributes should be defined for all input terms that the subset manages, and optionally any more complicated derived objects.
- **set_values** allows for any subset-specific terms to be set at the same time.
- **templatekeys** provides the names and description of all input parameter terms that the subset manages.
- **load_parameters** reads the subset templatekeys from an calculation input script and sets the subset attributes accordingly.
- **modelroot** is the root data model element name where the subset content is collected.
- **load_model** loads subset attributes from an existing model.
- **build_model** builds the elements of the model associated with the subset.
- **metadata** adds the simple metadata fields for the subset to the calculation's metadata dict.
- **calc_inputs** generates inputs for a calculation function based on the current set values of the subset attributes.

3. Additional subset methods and attributes
===========================================

3.1. _template_init
-------------------

The _template_init() method is used to provide additional information to the calculation's template and templatedoc.  When the template(doc) content is generated, the terms associated with each subset are listed in separate blocks.  The two terms managed by _template_init() provide default values for descriptive pieces related to this subset's block of input terms.

- **templateheader** is a short string that appears as a header above the subset's input terms inside the template and templatedoc files.

- **templatedescription** provides documentation description of the subset's terms that will appear in templatedoc above the description of the subset's template terms.  This allows for general rules related to the subset's inputs to be described.

3.2. preparekeys and interpretkeys
----------------------------------

These list keys in the input_dict that are managed by the prepare and load_parameters operations related to the subset.  Typically, preparekeys extends the templatekeys.keys() to add any additional terms that are only recognized by prepare, such as "_content" terms.  Then, interpretkeys extends preparekeys by also listing any terms that load_parameters adds to the input_dict that contain processed input values.
