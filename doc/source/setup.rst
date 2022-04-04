=====
Setup
=====

A key principle of iprPy is to minimize barriers for usage.  As such, the only
requirements for running the framework are Python 3.7+, and a few extra (mostly
standard) Python packages.  All of the required packages should be compatible
with any operating system that Python runs on.

Installing Python
=================

The iprPy framework is based on Python and therefore requires that Python be
installed.  Luckily, Python is free and compatible with Linux, MacOS and
Windows.  You can download Python from `python.org`_, although it is highly
recommended to obtain a Python distribution from `Anaconda`_.  The Anaconda
distributions support multiple Python environments, which can greatly help
avoid possible versioning conflicts that may arise between different
Python-based programs.  Additionally, the Anaconda distributions come with
the `scipy`_ family of packages already installed, which iprPy heavily relies on.

Installing iprPy
================

If you wish to use iprPy simply to access and run the existing calculations,
then you can easily install it with pip or with conda-forge if you have a
conda distribution of Python

.. code-block:: console

      pip install iprPy

or 

.. code-block:: console

      conda install iprPy -c conda-forge

Alternatively, if you have an interest in developing new calculations or
modifying the existing ones, you can download the code from github.  The github
repositories also contain the Jupyter Notebook versions of the calculations for
anyone to download and use.

- `https://github.com/usnistgov/iprPy`_ always coincides with the latest
  release of iprPy, i.e. it will be consistent with the pip and conda-forge
  packaged downloads.  This allows users to download the most recent stable
  version of iprPy.

- `https://github.com/lmhale99/iprPy`_ is the development repo of iprPy.  It
  may contain new calculation methods or other updates that are in the works
  but not yet included in the calculation release.  Ideally, any user pull
  requests should be submitted here.

Once you download a github repository, you can install it to your Python
environment in editable/development mode by changing the directory to the
repository's root directory and

.. code-block:: console
    
    pip install -e
 
Testing the install
===================

Installing iprPy *should* install an iprPy command line option to the Python
environment.  To test if iprPy is working, enter the following command in a
terminal

.. code-block:: console

      python iprPy check_modules

If everything installed properly, this should print informative statements
about the modules that make up iprPy.  In particular, there should be a list of
modules, including calculation methods, that properly loaded or failed to load.
Those that failed to load should display messages that either state that the
modules are not supported by the current version of iprPy or that those modules
require additional Python packages to be installed in order to work.  Should
you wish to use those modules, be sure to add the necessary Python packages.

If it displays an error that the iprPy command cannot be found, then the
installer failed to add the executable script to the proper location.  The
executable script can be found in the iprPy repository at iprPy/bin/iprPy.
Ideally, you should then copy/download this file to the associated Python
environment's Scripts directory.  Alternatively, you can place the script
file in any other directory and call it directly or "install" it by adding it
to any directory listed in your system's PATH environment variable.

For any other issues, feel free to email potentials@nist.gov for support.

Updating iprPy
==============

For packaged installs, ipyPy can be updated using pip or conda update options.
This should update not only iprPy's version but also the versions of any
required packages.

For editable/development installs, the code can be updated by doing a pull
request from the github repository.  Note, however, that this will not update
required packages.  Check the requirements.txt file for any new version
updates, most notably for the related packages "potentials" and "atomman".  If
needed, updating atomman should fix any requirement issues.

.. _Anaconda: https://www.anaconda.com/
.. _python.org: https://www.python.org/
.. _scipy: https://www.scipy.org/
.. _https://github.com/usnistgov/iprPy: https://github.com/usnistgov/iprPy
.. _https://github.com/lmhale99/iprPy: https://github.com/lmhale99/iprPy