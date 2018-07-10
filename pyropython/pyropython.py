# -*- coding: utf-8 -*-

import sklearn.ensemble as skl

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
import numpy as np
import time
import argparse
from pyropython.config import read_config
from pyropython.utils import ensure_dir
from pyropython.initial_design import make_initial_design
from pyropython.optimizer import get_optimizer

def optimize_model(case, run_opts):
    """
    Main optimization loop
    """

    # these can perhaps be changed later to use MPI
    # The executor needs to be *PROCESS*PoolExecutor, not *THREAD*Pool
    # The Model class and associated functions are not thread safe.
    ex = ProcessPoolExecutor(run_opts.num_jobs)

    optimizer = get_optimizer(run_opts.optimizer_name)

    x_best, f_best, Xi,Fi  = optimizer(case,run_opts,ex)


    X = np.vstack(Xi)
    Y = np.hstack(Fi).T
    print(X,Y)
    print("\nOptimization finished. The best result found was:")
    for n, (name, bounds) in enumerate(case.params):
        print("{name} :".format(name=name), x_best[n])

    # Fit a tree model to get variable importance
    forest = skl.ExtraTreesRegressor()
    forest.fit(X, Y)

    importances = forest.feature_importances_
    names = [name for name, bounds in case.params]
    indices = np.argsort(importances)[::-1]
    # Print the feature ranking
    print("\nVariable importance scores:")
    n_features = len(x_best)
    for f in range(n_features):
        print(("{n}.  {var} :" +
               " ({importance:.3f})").format(
                n=f + 1,
                var=names[indices[f]],
                importance=importances[indices[f]])
            )
    return


def proc_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", help="Input file name")
    parser.add_argument("-v", "--verbosity", type=int,
                        help="increase output verbosity")
    parser.add_argument("-n", "--num_jobs", type=int,
                        help="number of concurrent jobs")
    parser.add_argument("-m", "--max_iter", type=int,
                        help="maximum number of iterations")
    parser.add_argument("-i", "--num_initial", type=int,
                        help="number of points in initial design")
    parser.add_argument("-p", "--num_points", type=int,
                        help="number of points per iteration")
    args = parser.parse_args()
    case, run_opts = read_config(args.fname)
    if args.num_jobs:
        run_opts.num_jobs = args.num_jobs
    if args.max_iter:
        run_opts.max_iter = args.max_iter
    if args.num_initial:
        run_opts.num_initial = args.num_initials
    return case, run_opts


def create_dirs():
    ensure_dir("Best/")
    ensure_dir("Work/")
    ensure_dir("Figs/")


def main():
    case, run_opts = proc_commandline()
    create_dirs()
    print("Start Optimization.")
    optimize_model(case, run_opts)
    print("Done")


if __name__ == "__main__":
    freeze_support()
    main()
