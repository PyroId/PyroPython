from skopt import Optimizer
from skopt.learning import GaussianProcessRegressor
from distutils.dir_util import copy_tree
from shutil import rmtree
#from sklearn.externals.joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
from multiprocessing import freeze_support
from .model import Model 
from .plotting import plot_feature_importance 
import numpy as np
from pandas import read_csv
from scipy import signal
from itertools import product
import time
import sys
import argparse
from . import config as cfg
import pickle as pkl
from .utils import ensure_dir

def initialize_model(cfg):
    model = Model()
    return model


def dump_result(cfg,optimizer):

    config = {'num_jobs'           : cfg.num_jobs,
              'max_iter'           : cfg.max_iter, 
              'num_points'         : cfg.num_points,  
              'num_initial'        : cfg.num_initial, 
              'variables'          : cfg.variables,   
              'exp_data'           : cfg.exp_data,   
              'raw_data'           : cfg.raw_data, 
              'cfg.raw_data'       : cfg.simulation, 
              'experiments'        : cfg.experiment,
              'plots'              : cfg.plots,      
              'objective_function' : cfg.objective_function,
              'objective_opts'     : cfg.objective_opts,
              'data_weights'       : cfg.data_weights,
              'var_weights'        : cfg.var_weights,
              'fds_command'        : cfg.fds_command, 
              'optimizer_opts'     : cfg.optimizer_opts,
              'templates'          : cfg.templates,
              'tempdir'            : cfg.tempdir}

    with open('result.data', "wb") as f:
        pkl.dump(config   , f)
        pkl.dump(optimizer, f)  

def optimize_model(model,cfg):
    # these can perhaps be changed later
    ex = ProcessPoolExecutor(cfg.num_jobs)
    optimizer = Optimizer(dimensions=model.get_bounds(),
                          **cfg.optimizer_opts)

    # Convenience functions
    def evaluate(x):
        print("Evaluating %d points." % len(x), end='', flush=True)
        t0 = time.perf_counter()
        out =  list(ex.map(model.fitness, x)) # evaluate points in parallel
        t1 = time.perf_counter()
        y,pwd = zip(*out)
        print(" Complete in %.3f seconds" % (t1-t0))
        return y,pwd
    def ask(num_points):
        print("Asking for points.", end='', flush=True)
        t0 = time.perf_counter()
        x = optimizer.ask(n_points=num_points)  # x is a list of n_points points
        t1 = time.perf_counter()
        print(" Complete in %.3f seconds" % (t1-t0))
        return x
    def tell(x,y):
        print("Teaching points.", end='', flush=True)
        t0 = time.perf_counter()
        optimizer.tell(x, y)
        t1 = time.perf_counter()
        print(" Complete in %.3f seconds" % (t1-t0))

    # initial design (random)
    log=open("log.csv","w",buffering=1)
    header = ",".join(["Iteration"]+[name for name,bounds in cfg.variables]+["Objective","Best Objective"])
    log.write(header+"\n")
    print("picking initial points")
    x = ask(cfg.num_initial)
    y,pwd = evaluate(x)
    ind = np.argmin(y)
    yi = y[ind]
    Xi = x[ind]
    line = ["%d" % 0 ] + ["%.3f" % f for f in Xi] + ["%3f" % yi,"%3f" % yi]
    log.write(",".join(line)+"\n")
    # Save the  output files from the best run
    copy_tree(pwd[ind], "Best")
    y_best = yi
    x_best = Xi
    # Explicitly clean up temp direcotries
    for p in pwd:
        rmtree(p)
    # Main iteration loop  
    for i in range(cfg.max_iter): 
        # teach points
        tell(x,y)
        x = ask(cfg.num_points)
        y,pwd = evaluate(x)
        ind = np.argmin(y)
        yi = y[ind]
        Xi = x[ind]

        # Save the  output files from the best run
        if y_best>yi:
            copy_tree(pwd[ind], "Best")
            y_best = yi
            x_best = Xi
        
        # Explicitly clean up temp direcotries
        for p in pwd:
            rmtree(p)

        # Log iteration
        line = ["%d" % (i+1) ] + ["%.3f" % f for f in Xi] + ["%3f" % yi,"%3f" % y_best]
        log.write(",".join(line)+"\n")
    log.close()
    print("\nOptimization finished. The best result found was:")
    for n,(name,bounds) in enumerate(cfg.variables):
        print("{name} :".format(name=name), x_best[n])
        
    # For tree based metamodels, also output variable importance
    if isinstance(model,skl.RandomForestRegressor) or isinstance(model,skl.ExtraTreesRegressor):    
            tree  =result.models[-1]
            X      =result.Xi
            
            importances =  tree.feature_importances_
            names       =  [name for name,bounds in cfg.variables]
            std = np.std([tree.feature_importances_ for tree in model.estimators_],axis=0)
            indices = np.argsort(importances)[::-1]
            # Print the feature ranking
            print("Variable importance scores:")
            n_features = len(X[0])
            for f in range(n_features):
                print("{n}.  {var} : ({importance})".format( n= f + 1, 
                                                         var = names[indices[f]],
                                                         importance=importances[indices[f]]))
    dump_result(cfg,optimizer)
    return
    
def proc_commandline(cfg):
    parser = argparse.ArgumentParser()
    parser.add_argument("fname",help="Input file name")
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
    args=parser.parse_args()
    cfg.read_config(args.fname)
    if args.num_jobs:
        cfg.num_jobs=args.num_jobs
    if args.max_iter:
        cfg.max_iter=args.max_iter
    if args.num_initial:
        cfg.num_initial=args.num_initials
    return cfg

def create_dirs():
    ensure_dir("Best/")
    ensure_dir("Work/")
    ensure_dir("Figs/")
    #ensure_dir("Iterations/")
    
def main():
    proc_commandline(cfg)
    print("initializing")
    create_dirs()
    model = initialize_model(cfg)
    print("optimizing")
    optimize_model(model,cfg)
    print("done")

if __name__ == "__main__":
    freeze_support()
    main()
