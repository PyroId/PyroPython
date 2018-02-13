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

class Config:
    num_jobs    = 1
    max_iter    = 50 
    num_points  = 100
    num_initial = 100
    exp_data    = {}
    simulation  = {}
    experiment  = {}
    fname       = None
    fds_command = None
    optimizer_opts = {"base_estimator":       "ET",
                      "acq_func":             "gp_hedge",
                      "acq_optimizer":        "auto",
                      "n_initial_points":      100,
                      "acq_optimizer_kwargs":  {"n_points": 10000, "n_restarts_optimizer": 5,
                                              "n_jobs": 1},
                      "acq_func_kwargs":       {"xi": 0.05, "kappa": 1.96}
                      };
    filtering_options= {}

    def  __init__(self, fname):
        self.parse_input(fname)
        self.proc_input()
        self.fname = fname
        


    def parse_input(self,fname):
        lines=open(fname,"r").read()
        # extract config block
        # bloc starts with #start_config
        # and ends with #end_config
        try:
            start = lines.index("#start_config")
            end = lines.index("#end_config")
        except: 
            sys.exit("Error reading config.")
        config = y.load(lines[start:end])
        # check sanity of input
        if not 'variables' in config:
            sys.exit("Need to define independent variables and bounds.")
        if not 'simulation' in config:
            sys.exit("Need to define datafiles.") 
        if not 'experiment' in config:
            sys.exit("Need to define target variables.") 
        self.simulation = config['simulation']
        self.experiment = config['experiment']
        self.variables  = list(config['variables'].items())
        self.max_iter=config.get("max_iter",50)
        self.num_jobs=config.get("num_jobs",-1)
        self.num_points=config.get("num_points",1)
        self.num_initial=config.get("num_initial",1) 
        self.optimizer_opts["n_initial_points"]=self.num_initial
        self.optimizer_opts["acq_optimizer_kwargs"]["n_jobs"]=1
        self.optimizer_opts["acq_optimizer_kwargs"]["n_restarts_optimizer"]=self.num_jobs
        self.fds_command=config.get("fds_command","fds") 
        self.optimizer_opts=config.get("optimizer",self.optimizer_opts)


    def proc_input(self):
        for key in self.simulation:
            if not key in self.experiment:
                sys.exit("No experimental data for variable %s" % key)
        for key in self.experiment:
            if not key in self.simulation:
                sys.exit("No simulation data for variable %s" % key)
        for key,(fname,dname,conversion_factor) in self.experiment.items():
            tmp=read_csv(fname,header=1,encoding = "latin-1",index_col=False)
            tmp.columns = [colname.split('(')[0].strip() for colname in tmp.columns]
            tmp=tmp.dropna(axis=1,how='any')
            b, a = signal.butter(8, 0.125) # Nyquist = 2 seconds =0.5 Hz = 1 20 seconds = 0.05
            dat = signal.filtfilt(b, a, tmp[dname], method="gust")
            self.exp_data[key]=(array(tmp['Time']),dat*conversion_factor)
            
if __name__=="__main__":
    fname=sys.argv[1]
    cfg = Config(fname)
    print(cfg.num_jobs)
    print(len(cfg.exp_data))

