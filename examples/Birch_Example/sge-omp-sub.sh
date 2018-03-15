#!/bin/bash
#$ -S /bin/bash
#$ -cwd -N Optim -pe openmp 36
#$ -q all.q@compute-1-06
##export  OMP_STACKSIZE=64mb
echo Starting pyhton
python /home/tstopi/PyroPython/pyropython.py birch_cone.fds
#------------------------------------------------
