=====
Setup
=====

A key principle of iprPy is to minimize barriers for usage.  As such, the only
requirements for running the framework are Python 2.7, and a few extra (mostly
standard) Python packages.  All of the required packages should be compatible
with any operating system that Python runs on.

#. Install Python 2.7.  The `Anaconda`_ distribution is preferred as it
   automatically installs the `scipy`_ family of packages that are required by
   iprPy.
   
#. Add the Python package `xmltodict`_, which can be done using pip

   .. code-block:: console
   
        pip install xmltodict

#. Add the Python package `atomman`_ using pip

   .. code-block:: console
   
        pip install -U atomman
    
   The atomman package should be updated with iprPy as the development of the
   two packages is closely aligned.
    
#. Download or clone iprPy from GitHub.  The repository for the stable 
   versions is available at `https://github.com/usnistgov/iprPy`.
    
#. In a terminal, go into the iprPy root directory and add the iprPy package 
   to Python with the command
    
   .. code-block:: console
    
        python setup.py develop

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
    
.. _Anaconda: https://www.continuum.io/downloads
.. _scipy: https://www.scipy.org/
.. _atomman: https://github.com/usnistgov/atomman/
.. _xmltodict: https://github.com/martinblech/xmltodict
.. _https://github.com/usnistgov/iprPy: https://github.com/usnistgov/iprPy
.. _https://github.com/lmhale99/iprPy: https://github.com/lmhale99/iprPy