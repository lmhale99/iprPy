
High-Throughput Tools
*********************

Designing the calculations to be independent units of work that read
standard input files makes performing the calculations in
high-throughput incredibly simple.  All you have to do is execute the
same calculation scripts with different input files.  And with the
calculation results being reported in XML/JSON, the accumulated data
can automatically be uploaded into a database.

With iprPy, performing calculations in high-throughput is a two-step
process.

1. You `prepared <prepare.rst>`_ a calculation.  This creates multiple
   instances of the calculation within a specified "run_directory".
   Each instance is a folder containing a copy of the calculation's
   script, a unique input parameter file, and any other files required
   to perform the calculation.  Additionally, an incomplete record
   associated with each calculation instance is added to a database.

2. You start one or more `runners <runner.rst>`_.  Each runner
   operates on a single "run_directory" systematically performing one
   prepared calculation instance after another.  When each calculation
   finishes, successfully or unsuccessfully, the corresponding record
   in the database is updated and the calculation instance’s folder is
   archived and added to the database.

Contents:

* `Quick Start <quickstart.rst>`_
* `iprPy Classes <classes.rst>`_
  * `Calculation <classes.rst#calculation>`_
  * `Record <classes.rst#record>`_
  * `Database <classes.rst#database>`_
* `Prepare <prepare.rst>`_
  * `Introduction <prepare.rst#introduction>`_
  * `Notes on run_directory naming
    <prepare.rst#notes-on-run-directory-naming>`_
  * `How to prepare <prepare.rst#how-to-prepare>`_
  * `Prepare parameters <prepare.rst#prepare-parameters>`_
* `Runner <runner.rst>`_
  * `Introduction <runner.rst#introduction>`_
  * `Starting runners <runner.rst#starting-runners>`_
  * `Full process <runner.rst#full-process>`_
  * `Runner log files <runner.rst#runner-log-files>`_
* `Other High-Throughput Tools <inline.rst>`_
  * `build <inline.rst#build>`_
  * `check <inline.rst#check>`_
  * `check_modules <inline.rst#check-modules>`_
  * `clean <inline.rst#clean>`_
  * `copy <inline.rst#copy>`_
  * `destroy <inline.rst#destroy>`_
  * `set <inline.rst#set>`_
  * `unset <inline.rst#unset>`_
* `Analysis <analysis.rst>`_
  * `Accessing the data <analysis.rst#accessing-the-data>`_
  * `Analyzing the data <analysis.rst#analyzing-the-data>`_