=====
Setup
=====

A key principle of iprPy is to minimize barriers for usage.  As such, the only
requirements for running the framework are Python 2.7, and a few extra (mostly
standard) Python packages.  All of the required packages should be compatible
with any operating system that Python runs on.

Installing iprPy
================

#. Install Python 2.7 and the `scipy`_ family of Python packages.  If you
   don't already have Python, the easiest way to do this is to install
   `Anaconda`_.  The standard Anaconda distribution automatically adds the
   scipy packages.  For miniconda or a new environment of an existing anaconda
   installation, use the conda command to install the scipy packages.

#. Fork and clone, or download iprPy from GitHub.  The repository for the
   stable versions is available at `https://github.com/usnistgov/iprPy`_.
    
#. In a terminal, go into the local iprPy root directory and install the iprPy
   package to Python with the command
    
   .. code-block:: console
    
        python setup.py develop
        
   This should automatically install any other required Python packages.

#. To test if the framework is working, in a terminal go into the iprPy/bin
   directory and enter the command
   
   .. code-block:: console
        
        python iprPy check_modules
        
   If you see a list of included calculation, record, and database styles,
   then it is working!
    
#. The list printed in the last step indicates the iprPy modules that were
   successfully and unsuccessfully loaded.  If a module did not load, then
   either the module has additional package requirements or has not yet been
   fully implemented into iprPy.
    
Updating iprPy
==============

Installing iprPy to Python in develop mode means that any changes made are
recompiled every time the package is imported.  This makes it possible for
users to easily make their own changes and modifications as needed.  However,
it makes updating slightly more complicated.

#. Development of the `atomman`_ Python package is closely aligned to iprPy.
   As such, atomman should be updated using pip whenever iprPy is updated

   .. code-block:: console
   
        pip install -U atomman
    
#. If you forked iprPy from github, you can pull any changes.  Note that any
   changes you personally made would have to be committed and may lead to
   conflicts that need to be resolved.

#. If you downloaded iprPy, you can download a new version.  Then, either
   uninstall the old version and install the new version, or overwrite the
   files in the old version with the new.
    
Uninstalling iprPy
==================

The iprPy code is entirely self-contained and can be completely removed simply
by deleting it.  If you want to keep the files but uninstall the package from
Python, move iprPy to a new directory.
    
.. _Anaconda: https://www.continuum.io/downloads
.. _scipy: https://www.scipy.org/
.. _atomman: https://github.com/usnistgov/atomman/
.. _https://github.com/usnistgov/iprPy: https://github.com/usnistgov/iprPy