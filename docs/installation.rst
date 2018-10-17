============
Installation
============

Pyropython is a command line tool written in python.  You will need access to
the command line, a python distribution (e.g. `anaconda`_), `git`_ version control software and a text editor (e.g. `atom`_).

.. _atom: https://atom.io/
.. _anaconda: https://www.anaconda.com/download/
.. _git: https://git-scm.com/

The sources to pyropython are available at https://github.com/PyroId/PyroPython.
Download the sources.
::

    git clone

In the download directory type:
::

    pip install -e .

Note the trailing dot (.). The above command installs a *development* version of the software.
This means that if you modify the source you just downloaded, you do not need to install the software again.

Prerequisites
    1. FDS
    2. Python 3
    3. Python packages: Numpy, Scipy, Matplotlib, pandas, yaml, scikit-learn, scikit-optimize, Jinja2

Probably the easiest way to install the prerequisites

    1. Install Anaconda (or miniconda) [https://www.anaconda.com/download/]
    2. Type:

..

        conda install pandas scikit-learn jinja2
        conda install -c conda-forge scikit-optimize

    Matplotlib and numpy should already be included in the download of anaconda, if you downloaded miniconda or otherwise are missing packages:

..
        conda install numpy scipy matplotlib
        pip install pyDOE

    pyDOE is needed for lhs sampling. Test installation by typing:

..
     pyropython -h
