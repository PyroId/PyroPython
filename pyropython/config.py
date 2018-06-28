# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 09:49:36 2018

@author: tstopi
"""
import sys
import os
import yaml as y
from pandas import read_csv
from numpy import array,float64,interp,ones
from scipy import signal
from .utils import read_data
from .objective_functions import get_objective_function
from collections import namedtuple

num_jobs    = 1
max_iter    = 50
num_points  = 100
num_initial = 100
initial_design = "rand"
exp_data    = {}
raw_data    = {}
simulation  = {}
experiment  = {}
plots       = {}
objective_function = get_objective_function()
objective_opts = {}
data_weights = {}
var_weights  = {}
fds_command = "fds"
optimizer_opts = {"base_estimator":       "ET",
                  "acq_func":             "gp_hedge",
                  "acq_optimizer":        "auto",
                  "n_initial_points":      100,
                  "acq_optimizer_kwargs":  {"n_points": 10000, "n_restarts_optimizer": 5,
                                            "n_jobs": 1},
                  "acq_func_kwargs":       {"xi": 0.01, "kappa": 1.96}
                  };
templates = []
tempdir = os.path.join(os.getcwd(),"Work/")


def _proc_input(cfg):
    global data_weights,raw_data,exp_data,templates,variables
    global experiment,simulation,var_weights

    # yaml is sometimes unable to correctly convert str to float.
    # i.e., scientific notation like "1e15" will cause to fail
    # this would be a good place to convert numeric input to floats
    for n,(name,bounds) in enumerate(variables):
        try:
            variables[n] = (name,float64(bounds))
        except:
            sys.exit("Bounds for %s need to benumeric (for now)." % name)

    for key in simulation:
        if not key in experiment:
            sys.exit("No experimental data for variable %s" % key)
    for key in experiment:
        if not key in simulation:
            sys.exit("No simulation data for variable %s" % key)
    for fname in cfg['templates']:
        templates.append( (fname,open(fname,'r').read()) )

    # set default values for data lines
    for key,line in simulation.items():
        line.setdefault("ind_col_name","Time")
        line.setdefault("normalize",False)
        line.setdefault("conversion_factor",1.0)
        line.setdefault("header",1)
        line.setdefault("filter_type","None")
        line.setdefault("filter_opts",{})
        line.setdefault("gradient",False)

    for key,line in experiment.items():
        line.setdefault("ind_col_name","Time")
        line.setdefault("normalize",False)
        line.setdefault("conversion_factor",1.0)
        line.setdefault("filter_type","none")
        line.setdefault("filter_opts",{})
        line.setdefault("header",0)
        line.setdefault("gradient",False)
        exp_data[key]= read_data(**line)
        tmp = dict(line)
        tmp["filter_type"]="none"
        raw_data[key]= read_data(**tmp)



    # Weights for each  variable
    # if weights are not given, set weight to 1.0 for all datasets
    if len(var_weights)>0:
        if set(var_weights) != set(simulation):
            print("Need to define weights for all variables in 'experiment' and 'simulation':")
            print(set(var_weights).symmetric_difference(set(simulation)))
            sys.exit(0)
    else:
        for key in experiment:
            var_weights[key]=1.0

    # weights can be read from a file or input as a list of tuples in the format
    # [(x,w),(x,w),(x,w)] where x is the independent variable and w is th eweight
    # weights will be interpolated to coincide with the experimental data
    for key,(etime,edata) in exp_data.items():
        if key in data_weights:
            entry = data_weights[key]
            if isinstance(dict,entry):
                wtime,weights=read_data(**entry)
            elif isinstance(list,entry):
                wtime,weights = zip(*entry)
            else:
                print("Problem with weights for variable %s" % key)
                wtime = etime
                weights = ones(1,len(etime))
        else:
            wtime = etime
            weights = ones(len(etime))
        weightsi = interp(etime,wtime,weights)
        data_weights[key]=weightsi



def read_config(fname):
    global max_iter,num_jobs,num_points,num_initial,simulation,experiment,variables
    global optimizer_opts,objective_function,data_weights,fds_command,plots,var_weights
    global data_weights,initial_design
    lines=open(fname,"r").read()
    cfg = y.load(lines)
    # check sanity of input
    if not 'variables' in cfg:
        sys.exit("Need to define independent variables and bounds.")
    if not 'simulation' in cfg:
        sys.exit("Need to define datafiles.")
    if not 'experiment' in cfg:
        sys.exit("Need to define target variables.")
    if not 'templates' in cfg:
        sys.exit("Need to define templates.")
    simulation = cfg['simulation']
    experiment = cfg['experiment']
    plots = cfg['plots']
    variables  = list(cfg['variables'].items())
    max_iter=cfg.get("max_iter",50)
    num_jobs=cfg.get("num_jobs",-1)
    num_points=cfg.get("num_points",1)
    num_initial=cfg.get("num_initial",1)
    initial_design=cfg.get("initial_design","rand")
    optimizer_opts["n_initial_points"]=num_initial
    optimizer_opts["acq_optimizer_kwargs"]["n_jobs"]=1
    optimizer_opts["acq_optimizer_kwargs"]["n_restarts_optimizer"]=num_jobs
    fds_command=cfg.get("fds_command","fds")
    optimizer_opts=cfg.get("optimizer",optimizer_opts)
    obj = cfg.get("objective",None)
    if obj:
        objective_name = obj.get("type","mse")
        objective_function = get_objective_function(objective_name)
        objective_opts = obj.get("objective_opts",{})
        data_weights   = obj.get("data_weights",{})
        var_weights    = obj.get("var_weights",{})
    else:
        objective_name = "mse"
        objective_function = get_objective_function(objective_name)
        objective_opts = {}
        data_weights   = {}
        var_weights    = {}
    _proc_input(cfg)

def main():
    fname=sys.argv[1]
    read_config(fname)
    print(num_jobs)
    print(len(exp_data))

if __name__=="__main__":
    main()
