Installation
------------
Download the sources.

::
    git clone

In the download directory
::
    pip install -e .

Prerequisites
    1. FDS
    2. Python 3
    3. Python packages: Numpy, Scipy, Matplotlib, pandas, yaml, scikit-learn, scikit-optimize, Jinja2


Probably the easiest way to install the prerequisites

    1. Install Anaconda (or miniconda) [https://www.anaconda.com/download/#linux]
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



Basic usage
-----------

::

    pyropython config.yml

The config.yml file is a yaml-based configuration file. Below is a minimal
example of a configuration file

.. code-block:: yaml

    num_jobs: 2 # number of parallel jobs
    max_iter: 1 # maximum number of iterations
    num_points: 2  # How many points explored per iteration
    num_initial: 10 # Number of points in initial design
    initial_design: lhs
    # lines startting with hash (#) are comments
    fds_command: path/to/executable
    variables:
      A:       [4.0,14.0]
      E:       [100000.0, 500000.0]
    simulation:
        MASS20: {fname: 'birch_tga_1step_20_tga.csv',dep_col_name: 'Mass',ind_col_name: 'Temp'}
        experiment:
        MASS20: {fname: 'birch_tga_20_exp.csv',dep_col_name: 'Mass',ind_col_name: 'Temp'}
        templates: ["birch_tga_1step_20.fds"]
