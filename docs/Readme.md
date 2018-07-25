# PyroPython -- Parameter estimation for FDS pyrolysis models in python

This is simple parameter identification  tool  for FDS.  Currently the program uses scikit optimize [https://github.com/scikit-optimize/scikit-optimize] to optimize the model. Scikit-optimize uses sequential model-based optimization (also known as Bayesian Optimization).  The optimization uses a response surface fitted to the model evaluations to guide the optimization. TODO: add GAs such as shuffled-complex-evolution. (possibly using SPOTPY [http://fb09-pasig.umwelt.uni-giessen.de/spotpy/])

## Prerequisites

1. FDS
2. Python 3
3. Python packages: Numpy, Scipy, Matplotlib, pandas, yaml, scikit-learn, scikit-optimize, Jinja2

Easiest way to install the prerequisites

1. Install Anaconda (or miniconda) [https://www.anaconda.com/download/#linux]
2. Type:
```
 conda install pandas scikit-learn jinja2
 conda install -c conda-forge scikit-optimize
```
Matplotlib and numpy should already be included in the download of anaconda, if you downloaded miniconda or otherwise are missing packages:
```
 conda install numpy scipy matplotlib
 pip install pyDOE
```
pyDOE is needed for lhs sampling
## Usage

Test installation by typing:

```
 python run_pyropython.py -h

```

You may also want to install the package by typing
```
 pip install -e .

```
The "-e" flag stands for "editable". This is needed since this package is very much work in progress.

This should output the following help text

```
usage: pyropython.py [-h] [-v VERBOSITY] [-n NUM_JOBS] [-m MAX_ITER]
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
```

## input files

The input files are standard FDS input files with following additions

1. The configuration is given in YAML format file  [https://en.wikipedia.org/wiki/YAML]. The configuration is given as a command line parameter

```
python /path/to/run_pyropython.py config.yml
```
or, if you installed the package:
```
pyropython config.yml
```

In additon to the configuration file, template file(s) are also needed. These should be valid Jinja2 [http://jinja.pocoo.org/docs/2.10/] templates that produce FDS files.  

2. The Variables that are to be optimized shall be replaced with {{variable name}} (e.g. the variable name surrounded by double curly brackets).  For example, variables are defined in the yaml file as:

```
...
variables:
          VAR1: [ 0.1, 0.5]
...
```
The variable is
```
...

&MATL ID="ACME STUFF"
      DENSITY=100
      CONDUCTIVITY = {{VAR1}}
      SPECIFIC_HEAT=1
      ...

```

The input file is actually a Jinja2 template ([http://jinja.pocoo.org/]). This allows one to create various constructs such as create ramps from parametrized curves:
config.yml:
```
...
variables:
          a: [ 0.1, 0.5]
          b: [ 0.1, 0.5]
...
```
template.fds:
```
...

$MATL ID="test"
    CONDUCTIVITY = {{conductivity}}
/

{% for number in range(0,600,100) %}
  &RAMP ID="CP" , T={{number}} F={{a*number**2+b}}/
{% endfor %}
```
The for loop at the bottom of the previous example will create a "RAMP from 0 to 600 with step size 100 using with the ramp values calculated from second degree polynomial with parameters a and b. For example, with parameters a=0.01 and b=2 the ramp resulting file will contain:
```
...

        &RAMP ID="CP" , T=0 F=2.0/
        &RAMP ID="CP" , T=100 F=102.0/
        &RAMP ID="CP" , T=200 F=402.0/
        &RAMP ID="CP" , T=300 F=902.0/
        &RAMP ID="CP" , T=400 F=1602.0/
        &RAMP ID="CP" , T=500 F=2502.0/
...

```

The jinja2 templates can also contain logic blocks etc.

## configuration
The configuration file consists of optional and required fields. In this section we go over the configuration file from examples/Birch_TGA_example

### Job options
These options control the execution of th eprogram
```
num_jobs: 8 # number of parallel jobs
max_iter: 50 # maximum number of iterations
num_points: 8  # How many points explored per iteration
num_initial: 100 # Number of points in initial design
initial_design: lhs
# full path to fds executable
fds_command: /home/tstopi/Firemodels/fds/Build/mpi_intel_linux_64/fds_mpi_intel_linux_64
```

- **num_jobs**: How many parallel jobs to run when evaluating the objective function. (i.e. how many processors available for running FDS)
- **max_iter**: How many iterations to run after the initial design.
- **num_points**: How many points should be explored during each iteration. Probably makes sense to have **num_points** = **num_jobs**.
- **num_initial**: How many points to randomly sample before fitting the regression model
- **fds_command**: Give **full path** to the FDS executable that should be used.
- **initial_design**: How should the **num_initial** points be picked? Choices are "rand" or "lhs". Default is "rand".

Currently, the basic algorithm works as follows

1. Pick **num_initial points** randomly
2. Evaluate the objective function at these points using **num_jobs** processes (i.e. run FDS).
3. Begin iteration: Fit a regression model F(x) to the  points (x,f(x)), where x is a parameter vector and f(x) is the objective function.
4. Based on f(x), ask for **num_points** new points to explore.
5. Evaluate the the objective function f(x) at the new points.
6. If current iteration is not equal to or greater than **max_iter** go to 3.

If evolutionary algorithms are implemented they will follow the same basic structure, with the regression function replaced with whatever evolutionary mechanism one wishes to use.

## Configuration options

### **variables**

The variables (or parameters) to identify in the optimization. The variables are ginven as a list of tuples
```
 KEY: [lower bound, upperbound]
```
The KEY value is used to replace values in the FDS input template. The tuple in the brackets gives the lower and upper bound within which the variables may vary. Categorical values are not yet supported (TODO). For example, in the Birch_TGA_example, the reaction parameters are defined as:

```
variables:
  A:       [4.0,14.0]
  E:       [100000.0, 500000.0]
```
The corresponding entries in the template file are:
```
A       = {{'%.4E' % (10**A)}}
E       = {{E}}
```
Note that since *A* is logarithmic, with the optimization variable referring to the exponent, the term **{10**A}** appears in the template. This is "10 to the power of A" in python programming language. The other part, '%.4E' is number formatting in python (Exponential notation with four decimal places).

### Files and variables **simulation** and **experiment**

These two lists describe the data files,f rom  where the variables to be compared can be read. The data files are expected to be typical cone calorimeter output files with one header row and the column names in format "**col_name** (units)". The simulation data files are assumed to be standard FDS output files, with two header rows. The first header row, containing unit information, is skipped.
Each file description is given in format similar to a python dictionary with optional and required fields

KEY:
:  **fname**: Filename to be read. Assummed to be a comma delimited text file with one (experimental files) or two (simulation output files) header rows **required**
:  **ind_col_name**: Name of the *independent* variable columns, default (Time)
:  **dep_col_name**: Name of the column holding the *dependent* variable (e.g. MLR) **required**
:  **conversion_factor**: conversion factor for converting from e.g. g to kg (i.e, c in  y=c*x)
:  **filter_type**: filter used for smoothing the data. Choices "gp","ma". Default None.
:  **gradient**: numerical gradient of the variable will be used for optimization
:  **normalize**: TGA normalization, i.e. y=y/y[0].        }

Note that the program attempts to strip possible unit information from column name. This means that "MLR (kg/s)" becomes just "MLR".  

For example, in the Birch_TGA_example:
```
simulation:
    MASS2: {fname: 'birch_tga_1step_2_tga.csv',
            dep_col_name: 'Mass',ind_col_name: 'Temp',
            conversion_factor: 1.0}
experiment:
    MASS2: {fname: 'birch_tga_2_exp.csv',
            dep_col_name: 'Mass',
            ind_col_name: 'Temp',
            conversion_factor: 1.0,
            normalize: True,
            filter_type: 'gp'}
    # dm/dt = dT/dt * dM/dT = 20/60 K/s * dm / dT  
    # or  10/60 K/s * dm / dT etc...
    GMASS2: {fname: 'birch_tga_2_exp.csv',
             dep_col_name: 'Mass',
             ind_col_name: 'Temp',
             conversion_factor: 0.0333,
             normalize: True,gradient: True,
             filter_type: 'gp'}
```

In addition, the template file(s) must be defined. These are given on the **templates** line as a list of template files:
```
templates: ["birch_tga_1step_2.fds",...,"birch_tga_1step_10.fds"]
```
Pyropython will render each of these templates and run FDS on every input file before evaluating the results. Note that the template files are assumed to be in the same working directory as the config.yml file.

### Objective function options

Currently all objective functions are based on standardized moment:
```
     E[(sum_i ( w_i * (y_i-yhat_i) )^p]/std(w * y)^p
where:
        y_i   , experimental data
        yhat_i, simulation
        w_i   , data weights.
```
Note that the program automatically interpolates the simulatioin result to coincide with the experimental data.

The keywords under the **objective** key are:
    1. **type**: objective function type. Choices are: "standardized_moment" (need to define p), "mse" (p=2) and "abs-dev" (p=1). The default is "mse" (mean squared error).
    2. **var_weights** Weight given to each  variable. By default each variable has equal weight.
    3. **data_weights** Weights for individual observations.  Weights can be read from a file (entries like in 'simulation' or 'experiment') or input as a list of tuples in the format [(x,w),(x,w),(x,w)] where x is the independent variable and w is the weight. Weights will be interpolated to coincide with the experimental data
    4. **objective_opts**: options passed to the objective function. Only useful if type is "standardzed moment". In this case "p" can be defined.
```
obejctive:
    type: "mse"
    var_weights: {'MASS2': 1.0, 'MASS20': 1.0,'MASS5': 1.0, 'MASS10': 1.0,
                  'GMASS20',1.0,'GMASS2',1.0,'GMASS10',1.0,'GMASS5',1.0}
    data_weights:
      MASS2: [(0.0,1000.0),(190,1000.0),(191,1.0),(400,1.0),(800,1.0)]
      ....
```

### Plotting
Pyropython contains a rudimentary plotting tool to quickly inspect the experimental data, simulation results and goodness of fit.
If you installed the package using *pip*, you can get the plots by typing
```
plot_pyro config.yml
```
Otherwise, you may use
```
python /path/to/pyropython/plot_comp.py  config.yml
```

Figures can then be found in the Figs directory.

The figures to be drawn are defined in the *config.yml* file as follows:
```
plots:
    PLOTNAME1: {variables:, labels:, type:,....}
    PLOTNAME2: {variables:, labels:, type:,....}  
```

Meanings  of the keywords are:

:  **PLOTNAME**: name of output file (the file will be called PLOTNAME.pdf)
:  **variables**: ["VAR1","VAR2" ....] - variables to be plotted in the figure. Use KEYs defined in the *simulation* and *experiment* sections
:  **labels**: ["VAR1 label","VAR2 label" , ...]
:  **type**: "experimental", "simulation" or "comparison"
:  **ylabel**: "label for y-axis"
:  **xlabel**: "label for x-axis"
: The *type* argument options are:
    1. *experiment*: Useful for investigating the effects of the data filters. Plots the raw data and corresponding smoothed data
    2. *simulation*: Useful for investigating the effects of the data filters amd reading output.
    3. *comparison*: Useful for investigating goodness of fit.  

For example, in the Birch_TGA_Eample:
```
plots:
    expMASS: {variables: ["MASS2","MASS5","MASS10","MASS20"],labels: ["2 K/min","5 K/min","10 K/min","20 K/min"],type: "experimental", ylabel: "Mass (-)", xlabel: "Temp (C)"}

    simGMASS: {variables: ["GMASS2","GMASS20"],labels: ["2K/min","20 K/min"],type: "simulation", ylabel: "dM/dT (-/s)", xlabel: "Temp (C)"}

    cmpGMASS: {variables: ["GMASS2","GMASS5","GMASS10","GMASS20"],labels: ["2 K/min","5 K/min","10 K/min","20 K/min"],type: "comparison", ylabel: "dM/dT (-/s)", xlabel: "Temp (C)"}
```
These will create plots expMASS.pdf, simGMASS.pdf and cmpGMASS.pdf in the Figs directory.


### Optimizer options
These options are passed to the optimizer. This keyword can be omitted.
```
optimizer:
         base_estimator:        'ET'
         acq_func:              'EI'
         acq_optimizer:         'auto'
         n_initial_points:      1
         acq_optimizer_kwargs:  {n_points: 100000, n_restarts_optimizer": 100,n_jobs: 1}
         acq_func_kwargs:       {xi: 0.01, kappa: 1.96}
```

## Running

The directory *Birch_Example* contains an example input for PyroPython
