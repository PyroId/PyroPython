from skopt import Optimizer,dump
from skopt.learning import GaussianProcessRegressor
from skopt.space import Real
#from sklearn.externals.joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor
# example objective taken from skopt
from skopt.benchmarks import branin
from model import Model
import numpy as np
from pandas import read_csv
from scipy import signal
from itertools import product
import time
import sys
import argparse
from config import Config
import pickle
from utils import ensure_dir

def initialize_model(cfg):
    model = Model(exp_data=cfg.exp_data,
                  params=cfg.variables,
                  simulation=cfg.simulation,
                  fds_command=cfg.fds_command,
                  template=open(cfg.fname,"r").read(),
                  data_weights=cfg.data_weights)
    return model

def evaluate_model(model,x):
    return list(ex.map(model.fitness, x))

def ask_()

def optimize_model(model,cfg):
    ex = ProcessPoolExecutor(cfg.num_jobs)
    optimizer = Optimizer(dimensions=model.get_bounds(),
                          **cfg.optimizer_opts)
    # initial design (random)
    log=open("log.csv","w",buffering=1)
    header = ",".join(["Iteration"]+[name for name,bounds in cfg.variables]+["Objective"])
    log.write(header+"\n")
    print("picking initial points")
    x = optimizer.ask(n_points=cfg.num_initial)
    print("Evaluating %d initial points." % len(x), end='', flush=True)
    t0 = time.perf_counter()
    y =   # evaluate points in parallel
    t1 = time.perf_counter()
    print(" Complete in %.3f seconds" % (t1-t0))
    print("Teaching initial points.", end='', flush=True)
    t0 = time.perf_counter()
    optimizer.tell(x, y)
    t1 = time.perf_counter()
    print(" Complete in %.3f seconds" % (t1-t0))
    ind = np.argmin(y)
    yi = y[ind]
    Xi = x[ind]
    line = ["%d" % 0 ] + ["%.3f" % f for f in Xi] + ["%3f" % yi]
    log.write(",".join(line)+"\n")
    outname = "Iterations/best%d.fds" % 0
    model.write_fds_file(outname,Xi)
    for i in range(cfg.max_iter): 
        print("Asking for points.", end='', flush=True)
        t0 = time.perf_counter()
        x = optimizer.ask(n_points=cfg.num_points)  # x is a list of n_points points
        t1 = time.perf_counter()
        print(" Complete in %.3f seconds" % (t1-t0))
        print("Evaluating %d  points." % len(x), end='', flush=True)
        t0 = time.perf_counter()
        y = list(ex.map(model.fitness, x))  # evaluate points in parallel  
        t1 = time.perf_counter()
        print(" Complete in %.3f seconds" % (t1-t0))
        print("Teaching points.", end='', flush=True)
        t0 = time.perf_counter()
        optimizer.tell(x, y)
        t1 = time.perf_counter()
        print(" Complete in %.3f seconds" % (t1-t0))
        ind = np.argmin(y)
        yi = y[ind]
        Xi = x[ind]
        line = ["%d" % (i+1) ] + ["%.3f" % f for f in Xi] + ["%3f" % yi]
        log.write(",".join(line)+"\n")
        outname = "Iterations/best%d.fds" % (i+1)
        model.write_fds_file(outname,Xi)

    log.close
    ind = np.argmin(optimizer.yi)
    outname = "best.fds"
    model.write_fds_file(outname,optimizer.Xi[ind])
    print(optimizer.Xi[ind],optimizer.yi[ind])  # print the best objective found 
    dump(optimizer, 'result.gz', compress=9)
    return
    
def proc_commandline():
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
    cfg = Config(args.fname)
    if args.num_jobs:
        cfg.num_jobs=args.num_jobs
    if args.max_iter:
        cfg.max_iter=args.max_iter
    if args.num_initial:
        cfg.num_initial=args.num_initials
    return cfg

def create_dirs():
    ensure_dir("Best")
    ensure_dir("Work")
    ensure_dir("Iterations")
    
def main():
    cfg = proc_commandline()
    print("initializing")
    create_dirs()
    model = initialize_model(cfg)
    print("optimizing")
    optimize_model(model,cfg)
    print("done")






if __name__ == "__main__":
    main()
