iprPy runner
============

Setup
-----

The runner script only needs to know two things:

- A path to an accessible directory containing prepared calculations.

- Information for accessing the database containing records for the prepared 
  calculations.

This information is collected into an input file (examples are given in the 
files in this directory).
  
Directly executing runner.py
----------------------------

The runner.py script can be executed directly using

    ./runner.py <your-runner-input>
    
or 

    python runner.py <your-runner-input>
    
where <your-runner-input> is the path to your input file described in setup.

Submitting runner.py to a queue
-------------------------------

An example bash script for submitting runner.py to a queue is also contained in
this directory. With it, you can submit a runner using

    <submit-command> iprPy_runner <your-runner-input>

where <submit-command> is whatever queue submission command to use for your 
cluster and <your-runner-input> is the path to your input file described in 
setup.

Running on multiple processors
------------------------------

Note that runner.py itself runs in serial and that parallel processing only 
comes into play by the calculation scripts runner.py executes, or by the 
underlying simulations that are called by the calculation scripts. These 
subprocesses 