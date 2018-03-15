# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 09:49:36 2018

@author: tstopi
"""
import sys
import yaml as y
from pandas import read_csv
from numpy import array,newaxis,squeeze
from scipy import signal


num_jobs    = 1
max_iter    = 50 
num_points  = 100
num_initial = 100
raw_data    = {}
exp_data    = {}
simulation  = {}
experiment  = {}
objective_func = "RMSE"
data_weights = None
fds_command = None
optimizer_opts = {"base_estimator":       "ET",
                  "acq_func":             "gp_hedge",
                  "acq_optimizer":        "auto",
                  "n_initial_points":      100,
                  "acq_optimizer_kwargs":  {"n_points": 10000, "n_restarts_optimizer": 5,
                                            "n_jobs": 1},
                  "acq_func_kwargs":       {"xi": 0.01, "kappa": 1.96}
                  };
filtering_options= {}
templates = None

def _proc_input(cfg):
    for key in self.simulation:
        if not key in self.experiment:
            sys.exit("No experimental data for variable %s" % key)
    for key in self.experiment:
        if not key in self.simulation:
            sys.exit("No simulation data for variable %s" % key)
    for fname in cfg['templates']:
        templates.append(open(fname,'r').read())
    for key,(fname,dname,conversion_factor) in self.experiment.items():
        tmp=read_csv(fname,header=1,encoding = "latin-1",index_col=False)
        tmp.columns = [colname.split('(')[0].strip() for colname in tmp.columns]
        tmp=tmp.dropna(axis=1,how='any')
        dat = self.filter(array(tmp['Time']),array(tmp[dname]))
        self.raw_data[key]=(array(tmp['Time']),array(tmp[dname]*conversion_factor))
        self.exp_data[key]=(array(tmp['Time']),array(dat*conversion_factor))
    if self.data_weights:
        if set(self.data_weights) != set(self.simulation):
            print("Need to define weights for all variables in 'experiment' and 'simulation':")
            print(set(self.data_weights).symmetric_difference(set(self.simulation)))
            sys.exit(0)
    if not self.data_weights:
        self.data_weights={}
        for key in self.experiment:
            self.data_weights[key]=1.0


def read_config(fname):
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
    optimizer_opts["n_initial_points"]=self.num_initial
    optimizer_opts["acq_optimizer_kwargs"]["n_jobs"]=1
    optimizer_opts["acq_optimizer_kwargs"]["n_restarts_optimizer"]=self.num_jobs
    fds_command=cfg.get("fds_command","fds") 
    optimizer_opts=cfg.get("optimizer",self.optimizer_opts)
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

