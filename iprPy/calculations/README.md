# Calculation Script Basics

- - -

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2017-03-17

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
- - -

## Introduction

All calculation scripts included with the iprPy Framework are designed such that they can be independently executed as standalone scripts. All calculation scripts are built with certain shared design characteristics. This is to help facilitate the development of new calculations and the associated prepare scripts.

- - -

## Finding the calculation scripts

The calculation scripts can be found in the [iprPy/iprPy/calculations](../../../iprPy/calculations) directory. The calculations are divided into folders with the appropriate names. The calculations are placed here allowing them to be included when the iprPy package is imported in a Python script.

- - -

## Contents of the calculation script folders

With the common design of calculations, the contents of each calculation folder are similar:

- __calc\_[calcname].py__: The Python script for the calculation called calcname.

- __calc\_[calcname].template__: A template version of the input parameter file that the calculation script reads.

- __\_\_init\_\_.py__: The Python file that allows for the calculation to be included when the iprPy package is imported.

- Any other files that the calculation script needs to run properly, such as LAMMPS input script templates. 

- - -

## Running a calculation

Running a single calculation is easy!

1. Copy the calculation folder to another location (this keeps the original folder from becoming cluttered).

2. Create an [input parameter file]() "calc\_[calcname].in" for the calculation script using a text editor.

3. In a terminal, cd to the calculation folder you created, and enter:
        
        python calc_[calcname].py calc_[calcname].in
        
4. When the calculation finishes sucessfully, a "record.json" record file will be created containing the processed results.

- - -

## The input parameter file

Here is a quick explanation of the input parameter files.

### Formating rules

The input parameter files for calculations follow some very simple rules.

1. Each line is read separately, and divided into whitespace delimited terms.

2. Blank lines are allowed.

3. Comments are allowed by starting terms with #. The # term and any subsequent terms on the line are ignored. 

4. The first term in each line is a variable name.

5. All remaining (non-comment) terms are collected together as a complete value that is assigned to that variable name.

6. Any variable names without values are ignored.

7. Each variable name can appear at most one time. (Note that this is different from the [prepare scripts' input parameter files]().)

### Formatting example

Script:
    
    #This is a comment and will be ignored
    
    firstvariable    singleterm
    
    secondvariable   multiple terms   using    spaces
    thirdvariable    term #with comments
    
    fourthvariable
    
Gets interpreted as a Python dictionary:
    
    {'firstvariable':  'singleterm',
     'secondvariable': 'multiple terms using spaces',
     'thirdvariable':  'term'}
     
### Creating an input parameter file

While you can create an input parameter file from scratch, I find that it is easier to modify a copy of the "calc\_[calcname].template" file. The template files list all of the variable names accepted by the calculation and divided into meaningful categories. Each non-comment line looks something like

    parametername     <parametername>
    
Simply replace &lt;parametername&gt; with the value for parametername (or delete it to use the calculation's default value) for every line in the file. The meaning and usage of some common parameters is desribed below, and all parameters for a given calculation can be found in the corresponding Notebook in the same directory as this one.

### Some common calculation input parameters

#### Commands

Provides the external commands for running LAMMPS and MPI.

- __lammps_command__: the path to the executable for running LAMMPS on your system. Required for calculations that use LAMMPS. Don't include command line options as these are handled by the code.

- __mpi_command__: the path to the MPI executable and any command line options to use for calling LAMMPS to run in parallel on your system. Default value is None (run serially).

#### Potential

Provides the information associated with an interatomic potential implemented for LAMMPS.

- __potential_file__: the path to the LAMMPS-potential data model used by atomman to generate the proper LAMMPS commands for an interatomic potential. 
 
- __potential_dir__: the path to the directory containing any potential artifacts (eg. eam setfl files) that are used. If not given, then the files are expected to be in the calculation's working directory.

#### System Load

Provides the information associated with loading an atomic configuration.

- __load__: the style and path to the initial configuration file being read in. The style can be any file type supported by [atomman.load](https://github.com/usnistgov/atomman/blob/master/docs/reference/atomman.load.ipynb).
 
- __load_options__: a list of key-value pairs for the optional style-dependent arguments used by [atomman.load](https://github.com/usnistgov/atomman/blob/master/docs/reference/atomman.load.ipynb).
 
- __symbols__: a space-delimited list of atom-model symbols corresponding to the atom types and potential. If not given, the element/symbol information in the loaded file will be used. 
 
- __box_parameters__: box parameters to scale the loaded system to. Can be given either as a list of three or six numbers. Either format can be appended with an extra term specifying the length unit for the box parameters.  If not given, the box parameters of the loaded file are used. 
    
    - a b c: allows for the definintion of orthorhombic box parameters (length units).
    
    - a b c alpha beta gamma: allows for the definition of triclinic box parameters (in length units) and angles (in degrees).
    
#### System Manipulations

Performs manipulations on the loaded system. 

- __x_axis, y_axis, z_axis__: transformation axes for rotating the system. Each vector is given by three space-delimited numbers. The vectors must be orthogonal to each other. If the loaded system is cubic, these vectors are taken as hkl crystallographic directions and the rotated system is transformed into an orthorhombic box with dimensions given by a\*sqrt(h<sup>2</sup>+k<sup>2</sup>+l<sup>2</sup>) for each axis. 

- __atomshift__: a vector positional shift to apply to all atoms. The shift is relative to the size of the system after rotating, but before supersizing. This allows for the same relative shift regardless of box_parameters and sizemults.

- __sizemults__: parameters for supersizing the system. This may either be a list of three or six integer numbers.

    - ma mb mc: multipliers for each box axis. Values can be positive or negative indicating the direction relative to the original box's origin for shifting/multiplying the system.  
    
    - na pa nb pb nc pc: negative, positive multiplier pairs for each box axis. The n terms must be less than or equal to zero, and the p terms greater than or equal to zero. This allows for expanding the system in both directions relative to the original box's origin.  
    
#### Units

Specifies the units for various physical quantities to use in reading/writing values.

- __length_unit__: defines the unit of length for results, and input parameters if not specified. Default is 'angstrom'.

- __energy_unit__: defines the unit of energy for results, and input parameters if not specified. Default is 'eV'.

- __pressure_unit__: defines the unit of pressure for results, and input parameters if not specified. Default is 'GPa'.

- __force_unit__: defines the unit of pressure for results, and input parameters if not specified. Default is 'eV/angstrom'.

- - -

## Calculation script design structure

This section is for anyone wanting to peer under the hood and are interested in creating their own calculation scripts. If you want to understand the methodology of how a particular calculation is performed, I suggest looking in [docs/methodology]() for the corresponding calculation. 

### Common functions

#### main(\*args, pool=None)

This is the script's primary function which is automatically called when the script is executed from the command line. args is the list of command line terms given after the calculation script. 

The function arguments:

- __args[0]__: input parameter script name.

- __args[1]__: calculation key (UUID) to use. If not given, a random one will be automatically generated.
   
- __pool__: multiprocessing pool object used by some calculation scripts for distributing subcalculations to.

The main() functions for all calculations follow the same flow:

1. The input parameters file is read in by calling read_input().

2. The parameters are passed to the interpret_input() function which handles basic setup.

3. Any calculation specific functions are executed.

4. A data model record is created by data_model() using the input parameters and processed results.

#### read_input(f, UUID=None)

Reads in the input parameter file, and assigns calculation-specific default values to any parameters necessary. Methods supporting common reading and interpreting of the input parameters can be found in the iprPy.input module.

The function arguments:

- __f__: file-like object for the input parameter file

- __UUID__: calculation key (UUID) to use. If not given, a random one will be automatically generated.

Returns all input parameters in the form of a dictionary, input_dict.

#### process_input(input_dict)

Interprets the input parameter values for generating input parameters as directly used by the calculation functions. For example, generates an initial atomman.System object based on the loaded configuration and system manipulation parameters. Methods supporting common reading and interpreting of the input parameters can be found in the iprPy.input module.

The function arguments:

- __input_dict__: dictionary of input parameter values.

Nothing is returned as the generated parameters are added into input_dict.

#### data_model(input_dict, results_dict=None) 

Generates a data model record for the calculation. 

The function arguments:

- __input_dict__: dictionary of input parameter values.

- __results_dict__: dictionary of processed results. If not given, then an incomplete record is created. 

Returns a DataModelDict representation of the record.     