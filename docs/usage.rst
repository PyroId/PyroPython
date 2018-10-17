Usage
-----

After installing the pyropython package, it can be used from the command line as follows
::

    pyropython config.yml
    plot_pyro config.yml

The first command runs the main parameter identification program and the latter command plots the results.
The config.yml file is a yaml-based configuration file. Below is a minimal
example of a configuration file

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
        MASS20:
            fname: 'birch_tga_1step_20_tga.csv'
            dep_col_name: 'Mass'
            ind_col_name: 'Temp'
        experiment:
        MASS20:
            fname: 'birch_tga_20_exp.csv'
            dep_col_name: 'Mass'
            ind_col_name: 'Temp'
        templates: ["birch_tga_1step_20.fds"]
