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

    git clone https://github.com/PyroId/PyroPython.git  PyroPython

In the download directory type:
::

    python setup.py develop

The above command installs a *development* version of the software. This
means that if you modify the source you just downloaded, you do not need
to install the software again.

Prerequisites
    1. `FDS`_
    2. Python 3
    3. Python packages: Numpy, Scipy, Matplotlib, pandas, yaml, scikit-learn, scikit-optimize, Jinja2


.. _FDS: https://pages.nist.gov/fds-smv/

Probably the easiest way to install the prerequisites

    1. Install Anaconda (or miniconda) [https://www.anaconda.com/download/]
    2. Type:

::

        conda install pandas scikit-learn jinja2
        conda install -c conda-forge scikit-optimize

Matplotlib and numpy should already be included in the download of anaconda, if you downloaded miniconda or otherwise are missing packages:

::

        conda install numpy scipy matplotlib
        pip install pyDOE

pyDOE is needed for lhs sampling. Test installation by typing:

::

     pyropython -h

This should output the following help message

::

    usage: pyropython [-h] [-v VERBOSITY] [-n NUM_JOBS] [-m MAX_ITER]
                  [-i NUM_INITIAL] [-p NUM_POINTS]
                  fname

    positional arguments:
    fname                 Input file name

    optional arguments:
    -h, --help            show this help message and exit
    -v VERBOSITY, --verbosity VERBOSITY
                        increase output verbosity
    -n NUM_JOBS, --num_jobs NUM_JOBS
                        number of concurrent jobs
    -m MAX_ITER, --max_iter MAX_ITER
                        maximum number of iterations
    -i NUM_INITIAL, --num_initial NUM_INITIAL
                        number of points in initial design
    -p NUM_POINTS, --num_points NUM_POINTS
                        number of points per iteration
