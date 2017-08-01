===========
Quick Start
===========

This is a quick guide to setting up iprPy for performing high-throughput
calculations.  For simplicity, a local style database will be used as it
doesn’t have any additional requirements. See the remaining high-throughput
documentation for more details on the steps involved.

1. Decide on a *run_directory* and a database *host*.
    
    a. A *run_directory* is a local directory where calculations are prepared
       and performed. This directory should be empty or not yet created as
       extra files or folders in it can interfere with the runners.
    b. With a local style database, all records and completed calculation
       archives are placed within a local directory. The database *host* is
       simply the full path to that directory.
       
2. In a terminal, cd to iprPy’s bin directory. Within it is a file called
   iprPy.  Change permissions on the file so that it is recognized as an
   executable::
   
    $ chmod 755 iprPy

3. Define a database with the console command::
    
    $ ./iprPy set database <databasename> 

   Where <databasename> is a name to assign to the database. Pick something
   short and simple that you can remember, like “local”, “dbase”, or
   “library”. Prompts will appear asking for more information. For the
   database’s style, enter “local” (without the quotes). For the database’s
   host, enter the *host* directory path that you picked. When it asks for
   additional parameters simply hit enter without typing anything else.
   
   A visual example::
   
    $ ./iprPy set database localdb
    Enter the database’s style: local
    Enter the database’s host: /users/me/iprPy/dbase/
    Enter any other database parameters as key, value
    Exit by leaving key blank
    Key:
    
    $
    
4. Define a run_directory with the console command::

    $ ./iprPy set run_directory <runname>
    
   Where <runname> is the name to assign to the run_directory.  Pick something
   related to the database name, like if you called the database "local" then
   call the run_directory "local1". Enter the *run_directory* path when
   prompted.
   
   A visual example::
   
    $ ./iprPy set run_directory localdb1
    Enter the run_directory's path: /users/me/iprPy/torun/

    $
   
5. Build the database with the console command::

    $ ./iprPy build <databasename>
    
   This will copy all records stored in iprPy's library/ directory into the
   database *host* directory.  You can verify this by looking at the contents
   of *host*.  You're now ready to prepare calculations!
   
6. The first calculation to prepare is E_vs_r_scan.  An example input
   parameter script for preparing that calculation is located at 
   bin/prepare/E_vs_r_scan.in.  Open this file in a text editor.  
    
    a. First, you must specify a lammps_command in the *Commands* section.  The
       lammps_command is the local LAMMPS executable that you want the
       calculations to use.  Make certain that all other lammps_command lines
       are '#' commented out, valueless, or deleted.
    b. Next, look for the potential_name line in the *Potential Limiters*
       section.  Replace it with::
         
         potential_name             1987--Ackland-G-J--Ag
         
       This indicates to prepare the calculation for only the 
       1987--Ackland-G-J--Ag potential.  If you don't do this and leave the
       potential_name valueless or commented out then calculation instances
       will be prepared for ALL potentials!
    c. Save and close the file.
    
7. In a terminal working in iprPy's bin/ directory, enter::

    $ ./iprPy prepare <databasename> <runname> prepare/E_vs_r_scan.in
    
   When it finishes, there should be multiple folders in the *run_directory*
   and corresponding XML files in the calculation_cohesive_energy_relation
   subdirectory of the database.
   
8. Start a runner with::

    $ ./iprPy runner <databasename> <runname>
    
   If you want to speed things up, you can activate multiple runners at once
   by entering this command in more than one console terminal.  The runners
   will stop themselves when there are no more calculation instances in the
   run_directory.
   
9. Check out :any:`analysis` for tools to access the results from the 
   database.