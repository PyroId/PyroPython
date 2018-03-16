# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 09:49:36 2018

@author: tstopi
"""
import sys
import yaml as y
from pandas import read_csv
from numpy import array
from scipy import signal
from .filter import gp_filter

num_jobs    = 1
max_iter    = 50 
num_points  = 100
num_initial = 100
raw_data    = {}
exp_data    = {}
simulation  = {}
experiment  = {}
objective_func = "RMSE"
data_weights = {}
fds_command = "fds"
optimizer_opts = {"base_estimator":       "ET",
                  "acq_func":             "gp_hedge",
                  "acq_optimizer":        "auto",
                  "n_initial_points":      100,
                  "acq_optimizer_kwargs":  {"n_points": 10000, "n_restarts_optimizer": 5,
                                            "n_jobs": 1},
                  "acq_func_kwargs":       {"xi": 0.01, "kappa": 1.96}
                  };
filtering_options= {"filter": "GP"}
templates = []

def _proc_input(cfg):
    global data_weights,raw_data,exp_data,templates
    for key in simulation:
        if not key in experiment:
            sys.exit("No experimental data for variable %s" % key)
    for key in experiment:
        if not key in simulation:
            sys.exit("No simulation data for variable %s" % key)
    for fname in cfg['templates']:
        templates.append( (fname,open(fname,'r').read()) )
    for key,(fname,dname,conversion_factor) in experiment.items():
        tmp=read_csv(fname,header=1,
                    encoding = "latin-1",
                    index_col=False,
                    comment="#",
                    error_bad_lines=False,
                    warn_bad_lines=True,
                    skip_blank_lines=True)
        tmp.columns = [colname.split('(')[0].strip() for colname in tmp.columns]
        tmp=tmp.dropna(axis=1,how='any')
        dat = gp_filter(array(tmp['Time']),array(tmp[dname]))
        raw_data[key]=(array(tmp['Time']),array(tmp[dname]*conversion_factor))
        exp_data[key]=(array(tmp['Time']),array(dat*conversion_factor))
    if len(data_weights)>0:
        if set(data_weights) != set(simulation):
            print("Need to define weights for all variables in 'experiment' and 'simulation':")
            print(set(data_weights).symmetric_difference(set(simulation)))
            sys.exit(0)
    else:
        for key in experiment:
            data_weights[key]=1.0


def read_config(fname):
    global max_iter,num_jobs,num_points,num_initial,simulation,experiment,variables
    global optimizer_opts,objective_func,data_weights,fds_command
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
    variables  = list(cfg['variables'].items())
    max_iter=cfg.get("max_iter",50)
    num_jobs=cfg.get("num_jobs",-1)
    num_points=cfg.get("num_points",1)
    num_initial=cfg.get("num_initial",1) 
    optimizer_opts["n_initial_points"]=num_initial
    optimizer_opts["acq_optimizer_kwargs"]["n_jobs"]=1
    optimizer_opts["acq_optimizer_kwargs"]["n_restarts_optimizer"]=num_jobs
    fds_command=cfg.get("fds_command","fds") 
    optimizer_opts=cfg.get("optimizer",optimizer_opts)
    obj = cfg.get("objective",None)
    if obj:
        objective_func = obj.get("objective_func","RMSE")
        data_weights   = obj.get("data_weights",None)
    _proc_input(cfg)


if __name__=="__main__":
    fname=sys.argv[1]
    read_config(fname)
    print(num_jobs)
    print(len(exp_data))

