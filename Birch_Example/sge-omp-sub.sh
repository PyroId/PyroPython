#!/bin/bash
#$ -S /bin/bash
#$ -cwd -N Optim -pe openmp 36
#$ -q all.q@compute-1-06
##export  OMP_STACKSIZE=64mb
echo Starting pyhton
python /home/tstopi/Pyrolysis_modeling/skopt_pyroplot/skopt_test.py birch_cone.fds
#------------------------------------------------
