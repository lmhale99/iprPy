# High throughput workflow management control

Designing and running high throughput calculation workflows can be incredibly complex as it relies not only on performing similar units of work multiple times, but being able to spawn new calculation instances from previous results and pass information down through the workflow.  The design of iprPy focuses on having each individual component fully fleshed out so that it can be executed both in isolation or as part of a larger workflow.  Tools then build on top of this to provide a means of designing and running either custom or pre-defined high throughput workflows.

## Calculations

Calculations themselves provide a "workflow" for performing an isolated unit of work.  For the current calculation methods, this typically involves building/loading an atomic configuration, setting up and running one or more LAMMPS simulations, and processing the simulation results into meaningful values.  More details on the individual calculations and how they are built is described elsewhere.

### Calculation input files

What is important for this documentation is that each calculation can be independently executed with all necessary input parameters specified in a simple key-value text file.  Every calculation has its own set of recognized input parameter terms.  Methods of the Calculation class allow for the automatic generation of empty versions of the input script as well as documentation describing what each term is.  As each calculation is an independent unit of work, each input parameter in the input script is allowed only a single value.

## Preparing calculations

There are two major components that manage the higher-order workflows associated with running calculations in high throughput.

1. Database.prepare() identifies and generates a set of iprPy calculations that are to be executed.
2. Database.runner() finds prepared calculations and executes them one at a time.  Multiple runners can operate simultaneously.


In layman's terms, "high throughput" simply means iteratively performing a calculation or experiment over a variety of input parameters.  To this end, the prepare method generates many instances of a calculation to run based on so-called prepare input terms that largely consist of lists of values for the terms found in the calculation's input file.  Thus, unique calculation input files are generated that each contain only singular values for each included term.

Calculation class definition contains some extra metadata fields that are used by prepare to instruct how to properly generate new calculation instances.

- In the Calculation class definitions, there are "singularkeys" and "multikeys" lists that divide the input terms according to if they are allowed multiple values in the prepare inputs.  The "singularkeys" are the terms that should be the same for all calculation instances, e.g. the path to the LAMMPS executable.  The "multikeys" are the terms that are allowed to have multiple values when preparing, which are then iterated over to build the calculation instances.
- "multikeys" is actually a list of lists, with each embedded list collecting term names into input parameter sets.  When prepare is called, the calculation instances are generated through iterative combinations of all the different multikeys parameter sets.  This allows for many combinations to be explored based on a small number of specified values while also helping to avoid the generation of garbage input combinations.  One aspect of this to note is that when prepare is called, all terms of a specific multikeys parameter set must have the same number of values assigned to it so the script understands how to properly iterate the combinations.
- The Calculation class also defines a compare_terms list and a compare_fterms dict that indicate which values of the inputs are to be compared against existing records in the database to determine which of the newly proposed calculation instances to prepare have already been done.  This helps avoid repeat calculations from being performed.

Additionally, there are a few extra terms that are recognized as prepare input terms that do not directly correspond to the calculation input terms

- "buildcombos" is a special term that indicates that the prepare script calls a pre-defined buildcombos function.  Each buildcombos function is designed to query the database for records of a given style.  Then, based on the retrieved records, generate values for the prepare input terms.  This allows for the automatic generation of a large number of calculation instances that rely on information from either reference records or previously finished calculation records.
- Each buildcombos function defined in a prepare script is given a unique name.  Any input terms that start with that name and an underscore are automatically recognized as parameters to be passed to the associated buildcombos function.  For example, if there is a buildcombos called parent that loads results from a parent calculation, the calculation record style can be specified to the "parent_record_style" parameter.
- There are also some hidden internal prepare terms that advanced users/developers should be aware of.  Essentially, for every "_file" calculation term that tells the calculation to load a file, there is also a corresponding "_content" term that provides the file contents or information about where the contents can be found.  This allows for default values that rely on information in the content to be set, and lets prepare copy any necessary files to the generated calculation instances.

## Master prepare settings

The Database.master_prepare() method provides a slightly higher level interface for managing the preparation of calculation instances.  Use of master_prepare allows for users to prepare calculations in a manner consistent with how the Interatomic Potentials Repository prepares them.  This is accomplished in two components: Calculation.master_prepare_inputs() and Database.master_prepare().

Each Calculation class has a master_prepare_inputs() method that defines the default prepare input terms to use for that calculation based on what the Interatomic Potentials Repository uses.  Multiple sets of default prepare terms can be collected in separate branches allowing for the same calculation to appear in multiple locations of the overall calculation workflow.  Also, any of the default settings can be overridden by specifying new values as kwargs to Calculation.master_prepare_inputs().

Database.master_prepare() reads in a key-value text file and prepares at least one calculation method based on the default prepare terms specified for the calculations' master_prepare_inputs().

The calculations being prepared are grouped into calculation pools indicating a set of calculations that are to be ran using the same runner(s).  A calculation pool can be specified in the master_prepare input file using four terms
- __styles__ is a space-delimited list of calculation styles that are to be prepared according to their master_prepare_inputs() settings.  For calculations with multiple branches, the branch to use can be specified using "calculation_name:branch_name".
- __np_per_runner__ specifies the integer number of processors (cores) that the prepared calculations are intended to use for the LAMMPS simulations.
- __run_directory__ specifies the name of a previously defined run_directory where new calculations of the given style will be prepared.
- __num_pots__ is an integer that indicates how many potentials to try to prepare calculations for at the same time.  The smaller the number, the more times that Database.prepare() will be called, but the less RAM and time each prepare() call will require.

Multiple pools can be defined by repeating the four pool terms in the input script the same number of times.  While this allows for a full workflow to hypothetically be defined in a master_prepare script, it is recommended that Emperor (described below) be used instead as it allows for more control and features.

The master_prepare input file can also include any calculation and prepare terms associated with the included calculation(s).  The values specified will override the default values allowing for modifications of the workflow to alter settings or to limit the input phase space being checked.  In this way, master_prepare() can be much more convenient than prepare() as you only need to specify modifications to the settings rather than all of the settings.

Finally, master_prepare also allows for multiple alternate LAMMPS commands to be specified.  These will replace the default LAMMPS command for certain potential implementations that are known to require an older version of LAMMPS or a LAMMPS build that requires an external potential.

## Workflow emperors

The iprPy.workflow.Emperor class provides the highest level interface for running the full calculation workflow.  This combines pre-defined master_prepare pools with the ability to start runners either directly or through slurm job submissions.

An Emperor is initialized by specifying the database to use and the machine-specific command terms (lammps_command, mpi_command, and the alternate lammps_commands recognized by master_prepare).  Once initialized, calculations can be prepared and ran using prepare_pool() methods that operate on one prepare pool, or using the workflow() method that will call multiple prepare_pools in a row.

