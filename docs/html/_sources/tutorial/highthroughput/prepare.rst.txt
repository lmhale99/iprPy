=================
Prepare functions
=================

The cool thing is that running multiple instances of the calculation is almost as easy as running a single calculation.

1. Set up a database and access parameters for loading it as an iprPy.Database.

2. Create an input parameter file "prepare_[calcname].in" using a text editor.

3. Place (copies of) the prepare_[calcname].py and prepare_[calcname].in in the same directory. This can be anywhere, including the original calculation folder.

4. In a terminal, cd to the directory containing the two prepare files, and enter::
        
        python prepare_[calcname].py prepare_[calcname].in
        
5. When the script finishes, check that there are copies of the calculation in your run_directory, and incomplete calculation records in your database.

6. Start one or more :doc:`runner <runner>` scripts to perform the calculations.

Alternatively, calculations can be prepared either from another Python script using the :any:`Calculation class <classes>`, or in a slightly more streamlined manner using the :any:`command line options <inline>`.