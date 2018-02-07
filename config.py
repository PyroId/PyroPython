# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 09:49:36 2018

@author: tstopi
"""
import sys
import yaml as y
from pandas import read_csv
from numpy import array

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

    def  __init__(self, fname):
        self.parse_input(fname)
        self.proc_input()
        self.fname = fname
        
    def get_value(self,key,config,default=None):
        if key in config:
            return config[key]
        else:
            if not default:
                sys.exit("%s not defined in config" % key)
            else:
                return default

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
        self.max_iter=self.get_value("max_iter",config,50)
        self.num_jobs=self.get_value("num_jobs",config,-1)
        self.num_points=self.get_value("num_points",config,1)
        self.num_initial=self.get_value("num_initial",config,1)    
        self.fds_command=self.get_value("fds_command",config,"fds") 
    
    def proc_input(self):
        for key in self.simulation:
            if not key in self.experiment:
                sys.exit("No experimental data for variable %s" % key)
        for key in self.experiment:
            if not key in self.simulation:
                sys.exit("No simulation data for variable %s" % key)
        for key,(fname,dname,conversion_factor) in self.experiment.items():
            tmp=read_csv(fname,header=1,encoding = "latin-1")
            tmp.columns = [colname.split('(')[0].strip() for colname in tmp.columns]
            tmp=tmp.dropna(axis=1,how='any')
            self.exp_data[key]=(array(tmp['Time']),array(tmp[dname])*conversion_factor)
            
if __name__=="__main__":
    fname=sys.argv[1]
    cfg = Config(fname)
    print(cfg.num_jobs)
    print(len(cfg.exp_data))

