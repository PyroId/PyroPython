#!/bin/bash
#$ -S /bin/bash
#$ -cwd -N Optim -pe openmp 36
#$ -q all.q@compute-1-07
##export  OMP_STACKSIZE=64mb
echo Starting pyhton
python /home/tstopi/PyroPython/pyropython.py cone_steel_v5.fds
#------------------------------------------------
