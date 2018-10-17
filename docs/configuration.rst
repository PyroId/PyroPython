===================
Configuration files
===================

Preliminaries
-------------
The configuration files used by the PyroPython command line tools are `yaml`_ files.
They are plain text files that consists of key - value pairs. Below is an example
of a valid *yaml* input (_not_ a valid PyroPython input!)

.. _yaml: http://yaml.org/

.. code-block:: yaml

    key: value
    person:
        age: 100
        name: NA

In the above example, the keyword "age" is tied to a single value (100) while the
keyword person is tied to a *dictionary*.  The dicitonary of a person can also
be written

.. code-block:: yaml

    person: {age: 100, name: NA}

This should look familiar to everyone familiar with the Python programming language.

Configuration file structure
----------------------------

PyroPython configuration file consists of a number of keywords some of which are
optional. A minimal configuration file looks like this:

.. code-block:: yaml

    num_jobs: 1 # number of parallel jobs
    max_iter: 10 # maximum number of iterations
    num_points: 1  # How many points explored per iteration
    num_initial: 10 # Number of points in initial design (here 100*ndim)
    fds_command:
    variables: # VAR_NAME: [LOWER,UPPER]
        var1: [0, 1]
        var2: [0, 2]
    simulation:
        MASS2: {fname: 'birch_tga_gronli_2_tga.csv',dep_col_name: 'Mass',ind_col_name: 'Temp'}
        GMASS2: {fname: 'birch_tga_gronli_2_tga.csv',dep_col_name: 'MLR',ind_col_name: 'Temp'}
    experiment:
        MASS2: {fname: 'birch_tga_2_exp.csv',dep_col_name: 'Mass',ind_col_name: 'Temp',normalize: True}
        GMASS2: {fname: 'birch_tga_2_exp.csv',dep_col_name: 'Mass',ind_col_name: 'Temp',conversion_factor: 0.0333,normalize: True,gradient: True}
    templates: ["birch_tga_gronli_2.fds"]

This configuration file instructs PyroPython to match the

Configuration file keywords
----------------------------

.. py:data:: num_jobs

    Number of parallel jobs used. (default: 1)

.. py:data:: max_iter

    Maximum number of iterations. Meaning of this parameter depends on the
    algorithm used

.. py:data:: num_points

    Maximum number of points explored per iteration.  BEhaviour depends on the
    optimization algortihm. Default (num_point = num_jobs)

.. py:data:: num_initial

    Number of points chosen randomly in the beginning. Also known as initial design.

.. py:data:: initial_design (optional, default: lhs)

    Type of initial design. Choices are "rand" and "lhs" for uniform random and
    latin hypercube sampling

.. py:data:: initial_design_file (optional)

    A comma separated text file containing a initial design. The file should
    contain one header line and a column for each variable being optimized and
    optionally objective value.  Overrides  *initial_design* and  *num_initial*
    options.

.. py:data:: casename (optional)

    Casename used for naming log file and output directories. By default
    Pyropython creates the following files and directories:

    ::

        Work/
        Best/
        Figs/
        log.csv

    If the casename is set to 'CASE',  the followin g files and directories
    will be created:

    ::

        Work/
        CASE_Best/
        CASE_Figs/
        CASE.csv

    This is useful if you want to several cases in the same folder.

.. py:data:: fds_command

    Full path to the executable, including the executable. For example, if you
    installed FDS from the official distribution on Windows, this line would most
    likely read:

    .. code-block:: yaml

        fds_command: C:\Program Files\firemodels\FDS6\bin\fds.exe

.. py:data:: variables

    A list of variables and corresponding bounds in format:

    ..
        var_name: [lower bound, upper bound]

    For example:

    .. code-block:: yaml

        variables:
            var1: [0,1]
            var2: [-1,1]

    The above block defines two variables named "var1" and "var2". Variable "var1"
    has lower bound 0 and upper bound 1.

.. py:data:: simulation

    A list of variables to be read from the simulation output. Each variable is
    given in format:

    .. py:data:: varname: {fname dep_col_name: ind_col_name header,normalize,gradient,filter}




.. py:data:: experiment


.. py:data:: obejctive:
.. py:data:: plots
.. py:data:: optimizer_name
.. py:data:: optimizer
