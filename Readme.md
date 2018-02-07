# PyroPython -- Parameter estimation for FDS pyrolysis models in python

This is simple python script that attempts to indentify pyrolysis parameters for FDS. The program si divided into three parts:

model.py - this file containse the claa Model. Contains functions for reading datafiles, fitness evaluation and running FDS and postprocessing FDS outputs
config.py - provides configuration management
pyropython.py - main executable 

currently all these files need to be in the same directory. TODO: more sensible packaging

As it is now, the program uses scikit optimize [https://github.com/scikit-optimize/scikit-optimize] to optimize the model. Scikit-optimize uses sequential model-based optimization (also known as Bayesian Optimization).  The optimization uses a response surface fitted to the model evaluations to guide the optimization. TODO: add GAs such as shuffled-complex-evolution. (possibly using SPOTPY [http://fb09-pasig.umwelt.uni-giessen.de/spotpy/])

## Prerequisites

-FDS 
-Python 3
-Python packages: Numpy, Scipy, Matplotlib, pandas, yaml, scikit-optimize

Esiest way to install the prerequiaites

1. Install Anaconda (or miniconda) [https://www.anaconda.com/download/#linux]
2. Type: 
```
 conda install pandas scikit-learn
 conda install -c conda-forge scikit-optimize
```
Matplotlib and numpy should already be included in the download of anaconda, if you downloaded miniconda or otherwise are missing packages:
```
 conda install numpy scipy matploltib 
```

## Usage

Test installation by typing:

```
 python pyropython.py -h

```

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

1. Theres should be a configuration block somewhere in the .fds file. The configuration is given in YAML format [https://en.wikipedia.org/wiki/YAML]. The configuration is placed between #config_start and #config_end blocks as follows 
```
#config_start

... configuration goes here

#config_end
```
2. The Variables that are to be optimized shall be replaced with $var_name (e.g. dollar sign followed by the variable name). For example:
```
#config_start
...
variables:
          VAR1: [ 0.1, 0.5]
...
#config_end

...

&MATL ID="ACME STUFF"
      DENSITY=100
      CONDUCTIVITY = $VAR1
      SPECIFIC_HEAT=1
      ...

```

## configuration
The configuration block consists of optional and required fields:

```
#start_config
# number of parallel jobs (optional, default 1)
num_jobs: 36 
# maximum number of iterations  (optional, default 50)
max_iter: 50
# How many points explored per iteration  (optional, default 1)
num_points: 100  
# Number of points in initial design  (optional, default 1)
num_initial: 100 
#location of fds executable (absolute path).  (required)
fds_command: /home/tstopi/Firemodels/fds/Build/mpi_intel_linux_64/fds_mpi_intel_linux_64  #
# Variables to be identified (required) 
# Format is  VARNAME: [min max]
# VARNAME is used to identify the variable in the fds in put ($VARNAME). The *min* and *max* give the bounds for the variable
variables:         
          KS300: [ 0.1, 0.5]  
          KS600: [ 0.5,  2]
          CS600: [ 200,   400]
          RHOC : [ 100,300]
          KC   : [ 0.01, 0.5]
#simulation - simulation outputfiles
#entries in format:
#   Var_name: output_file, col name, conversion factor
#Var_name is used to match the simulation output and experimental data
#output_file gives the fiel where this output is located int
#col name gives the column name in output file
#conversion factor  factor for converting from e.g. g to kg (i.e, c in  y=c*x)
#experiment - experimental data in same format
#   Var_name: data_file, col name, conversion factor
simulation:
    MLR: ['cone_hrr.csv','MLR_TOTAL',100000]
experiment:
    MLR: ['06110001_red.CSV','Specific MLR',1.0]
#end_config
```

## Running

The directory *Birch_Example* contains an exaple input for pyropython
