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
      logA:       [4.0,14.0]
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

In addition to the above configuration file, the tamplate file "birch_tga_1step_20.fds" needs to exist in the same directory as the 
config.yml file. The template files are `Jinja2`_ templates that produce input files for FDS (or any other simulator that accepts
text based input.). Below is an example of a configuration file that could be used with the above input.

.. _Jinja2:  http://jinja.pocoo.org/docs/2.10/

::

    &HEAD CHID='birch_tga_1step_20', TITLE='TGA TEST of evaporation' / 

    &MESH IJK=3,1,4, XB=-2,2,-0.5,0.5,0,1 /  

    &TIME T_END=2400., WALL_INCREMENT=1, DT=1.0 /  

    &RADI NUMBER_RADIATION_ANGLES = 20 /
    &REAC FUEL='METHANE', C=1, H=4, CRITICAL_FLAME_TEMPERATURE=2000. /  No gas phase reaction

    &SPEC ID='WATER VAPOR' /

    &VENT XB = -1,1,-0.5,0.5,0.0,0.0, SURF_ID = 'SAMPLE' /

    &SURF ID = 'SAMPLE'
        RGB =200,100,0
        BACKING = 'INSULATED' 
        THICKNESS = 0.00001
        HEAT_TRANSFER_COEFFICIENT = 0.
        TGA_ANALYSIS=.TRUE.
        TGA_HEATING_RATE = 20.
        TGA_FINAL_TEMPERATURE = 800.
        MATL_ID(1,1) = 'BIRCH',
        MATL_ID(1,2) = 'MOISTURE'
        MATL_MASS_FRACTION(1,:) = 0.9875,0.0125/

    &MATL ID = 'MOISTURE'
        EMISSIVITY  = 1.0
        DENSITY     = 1000.
        CONDUCTIVITY    = 0.6
        SPECIFIC_HEAT   = 4.19
        N_REACTIONS     = 1
        A       = 1E13
        E       = 1e5
        N_S             = 1
        SPEC_ID         = 'WATER VAPOR'
        NU_SPEC         = 1.0
        HEAT_OF_REACTION= 2260. /


    &MATL ID = 'BIRCH'
        EMISSIVITY  = 1.0
        DENSITY     = 550.
        CONDUCTIVITY    = 0.20
        SPECIFIC_HEAT   = 1.34 
        N_REACTIONS     = 1
        A               = {{A**logA}}
        E               = {{E}}
        N_S             = 1.0
        SPEC_ID         = 'METHANE'
        NU_SPEC         = 0.835
        MATL_ID         = 'CHAR'
        NU_MATL         = 0.165
        HEAT_OF_REACTION= 218.
        HEAT_OF_COMBUSTION = 40000.0 /

    &MATL ID = 'CHAR'
        EMISSIVITY  = 1.0
        DENSITY     = 140.
        CONDUCTIVITY    = 0.09
        SPECIFIC_HEAT   = 1.1 / 

    &TAIL / 

Note that the pre-exponentiation factor is transformed in to logarithmic scale, by setting {{10**logA}} in the 
input file. The operator "**" stands for power in the Python programming language and the statement "10**logA"
means "10 to the power of logA".