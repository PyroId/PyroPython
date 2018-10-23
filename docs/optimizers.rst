.. _Optimizers:

==========
Optimizers
==========

Pyropython supports a number of methods for solving the optimization problem. The
optimizer is defined in the config.yml file  with the *optimizer_name* keyword. 
Parameters affecting the optimization algorithms are: 

.. code-block:: yaml

	maxiter: # maximum number of iterations.
	num_points: # number of points per iteration
	num_initial: # number of points in the initial design
	initial_design: rand | lhs # type of initial design
	intiial_design_file: # file containing initial design. 
	optimizer_name: dummy | multistart | de | skopt 
	optimizer: # options passed to skopt.optimizer

The first three keywords have slightly different effects depending on the optimizer 
chosen. 

The supported optimizers are.

1. **dummy**  - Random sampling
2. **multistart** - Multiple starts using Nelder-Mead simplex (from `scipy`_)
3. **de** - Differential evolution (also from `scipy`)
4. **skopt** (default) Bayesian Optimization (using `scikit-optimize`)

Initial design
--------------

Initial design is needed for all optimization algorithms except differential
evolution. Differential evolution uses a LHS initial design, but this is handled
internally by the optimizer. 

There are three choices for initial design.

1. **lhs** - Random design using initial hypercubes.
2. **rand** - Random design using uniform random sample.
3. **initial_design file** - Read the initial design from a .csv file.

Latin hypercube sampling is the default, but currently requires the pyDOE package. 
The initial design file is mainly useful for continuing optimization from previous 
results or "polishing" the results of a global algorithm with local algorithm. 
More on "polishing" later. 

Random sampling
---------------

Random sampling is what the name suggests: random sampling. Consider the following
settings in the configuration file:

.. code-block:: yaml

	maxiter: 10
	num_points: 10
	num_initial: 150
	initial_design: lhs
	optimizer_name: dummy  


First, the model is evaluated at 150 points selected with latin hypercube sampling. After 
this the algorithm conitnues for 10 iterations, evaluating the mdoel at 10 points each iteration.
The points in the subsequent iterations are selected by uniform random sampling. Not latin hypercubes.

Multistart
----------

Multistart optimizes the model using a deterministic local optimizer, using multiple starting points.
The starting points are selected in the following fashion:

1. First, model is evaluated at *num_initial* points (or the initial design is loaded from file)
2. Points are ordered in ascending order by their objective value.
3. In each iteration,  numbe rof points indicated by the *num_points* variable are evaluated in the
   order of their fitness.

Consider the following input:     

.. code-block:: yaml

	maxiter: 1
	num_points: 1
	num_initial: 150
	initial_design: lhs
	optimizer_name: multistart

The *intial_design_file* option can be used to "polish" results from another optimizer:

.. code-block:: yaml

	maxiter: 1
	num_points: 1
	initial_design_file: results_from_earlier_optimization.csv
	optimizer_name: multistart


Differential Evolution
----------------------


Differential evolution makes use of the `differential evolution`_ solver in `scipy`_.  The **maxiter** is
the only parameter that has an effect on the differential evolution solver. 

.. code-block:: yaml

	maxiter: 1000 # MAximum number of generations
	num_points: 1 # Ignored
	num_initial: 150 # Ignored
	optimizer_name: de

This instructs pyropython to use differential evolution algorithm 