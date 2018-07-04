from skopt import Optimizer
import sklearn.ensemble as skl
from distutils.dir_util import copy_tree
from shutil import rmtree
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
import numpy as np
import time
import argparse
from .config import read_config
import pickle as pkl
from .utils import ensure_dir


def optimize_model(case,run_opts):
    """
    Main optimization loop
    """
    # these can perhaps be changed later to use MPI
    # The executor needs to be *PROCESS*PoolExecutor, not *THREAD*Pool
    # The Model class and associated functions are not thread safe.
    ex = ProcessPoolExecutor(run_opts.num_jobs)
    optimizer = Optimizer(dimensions=case.get_bounds(),
                          **run_opts.optimizer_opts)

    # Convenience functions
    def evaluate(x):
        """
        This function evaluates the model finess at points x
        """
        print("Evaluating %d points." % len(x), end='', flush=True)
        t0 = time.perf_counter()
        out = list(ex.map(case.fitness, x))  # evaluate points in parallel
        t1 = time.perf_counter()
        y, pwd = zip(*out)
        print(" Complete in %.3f seconds" % (t1-t0))
        return y, pwd

    def ask(num_points):
        """
        This function asks the optimizer for more points
        """
        print("Asking for points.", end='', flush=True)
        t0 = time.perf_counter()
        # x is a list of n_points points
        x = optimizer.ask(n_points=num_points)
        t1 = time.perf_counter()
        print(" Complete in %.3f seconds" % (t1-t0))
        return x

    def tell(x, y):
        """
        This function tells the optimizer some new points.
        """
        print("Teaching points.", end='', flush=True)
        t0 = time.perf_counter()
        optimizer.tell(x, y)
        t1 = time.perf_counter()
        print(" Complete in %.3f seconds" % (t1-t0))

    log = open("log.csv", "w", buffering=1)
    header = ",".join(["Iteration"] +
                      [name for name, bounds in case.params] +
                      ["Objective", "Best Objective"])
    log.write(header+"\n")
    print("picking initial points")
    # initial design (random) or lhs
    if run_opts.initial_design == "lhs":
        try:
            from pyDOE import lhs
        except ImportError:
            print("Latin hypercube smapling requires pyDOE.\
                   Using random sampling")
        run_opts.initial_design = "rand"

    if run_opts.initial_design == "lhs":
        ndim = len(case.get_bounds())
        xhat = lhs(run_opts.num_initial, ndim, "maximin").T
        xhat = [list(point) for point in xhat]
        x = xhat
        for i, point in enumerate(x):
            for n, (xmin, xmax) in enumerate(case.get_bounds()):
                # Note that point is reference to element of x
                x[i][n] = xmin+xhat[i][n]*(xmax-xmin)
    else:
        x = ask(run_opts.num_initial)

    y, pwd = evaluate(x)
    ind = np.argmin(y)
    yi = y[ind]
    Xi = x[ind]
    line = ["%d" % 0] + ["%.3f" % f for f in Xi] + ["%3f" % yi, "%3f" % yi]
    log.write(",".join(line)+"\n")
    # Save the  output files from the best run
    copy_tree(pwd[ind], "Best")
    y_best = yi
    x_best = Xi
    # Explicitly clean up temp direcotries
    for p in pwd:
        rmtree(p)
    # Main iteration loop
    for i in range(run_opts.max_iter):
        print("Iteration {i}/{N}:".format(i=i, N=run_opts.max_iter))
        # teach points
        tell(x, y)
        x = ask(run_opts.num_points)
        y, pwd = evaluate(x)
        ind = np.argmin(y)
        yi = y[ind]
        Xi = x[ind]

        # Save the  output files from the best run
        if y_best > yi:
            copy_tree(pwd[ind], "Best")
            y_best = yi
            x_best = Xi

        # Explicitly clean up temp direcotries
        for p in pwd:
            rmtree(p)

        # Log iteration
        line = ["%d" % (i+1)] + ["%.3f" % f for f in Xi] + \
               ["%3f" % yi, "%3f" % y_best]
        log.write(",".join(line)+"\n")

        # Print info
        print()
        print(
            "   best objective from this iteration:  {obj:.3E}".format(obj=yi))
        print(
            "   best objective found thus far:       {obj:.3E}".format(obj=y_best))
        print("   best model:")
        for n, (name, bounds) in enumerate(case.params):
            print("       {name} :".format(name=name), x_best[n])
        print()
    log.close()
    print("\nOptimization finished. The best result found was:")
    for n, (name, bounds) in enumerate(case.params):
        print("{name} :".format(name=name), x_best[n])

    # For tree based metamodels, also output variable importance
    forest = optimizer.models[-1]
    if(isinstance(forest, skl.RandomForestRegressor) or
       isinstance(forest, skl.ExtraTreesRegressor)):
        X = optimizer.Xi
        importances = forest.feature_importances_
        names = [name for name, bounds in case.params]
        indices = np.argsort(importances)[::-1]
        # Print the feature ranking
        print("\nVariable importance scores:")
        n_features = len(X[0])
        for f in range(n_features):
            print("{n}.  {var} : ({importance:.3f})".format(n=f + 1,
                                                            var=names[indices[f]],
                                                            importance=importances[indices[f]]))
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
