import tempfile
import os
import numpy as np
import copy
import subprocess
from multiprocessing import Lock
from config import Config
from jinja2 import Template
import sys


class Model:
     def __init__(self,exp_data,params,simulation,fds_command,template,data_weights):
         self.exp_data = exp_data
         self.params = params
         self.simulation = simulation
         self.data_weights = data_weights
         self.num_fitness = 0
         #self.template = Template(template)
         self.template = template
         self.points   = []
         self.fds_command = fds_command
         self.tempdir=os.getcwd()+"/Work/"

     def write_fds_file(self,outname,x):
        f=open(outname,"w")
        template=Template(self.template)
        variables = {self.params[n][0]: var for n,var in enumerate(x)}
        outfile = template.render(**variables)
        f.writelines(outfile)
        f.close() 

     def run_fds(self,x):
        cwd = os.getcwd()
        tempfile.tempdir=self.tempdir
        my_env = os.environ.copy()
        my_env["OMP_NUM_THREADS"] = "1"
        with tempfile.TemporaryDirectory(prefix="Cone_") as pwd:
            os.chdir(pwd)
            self.write_fds_file("cone.fds",x)
            devnull = open(os.devnull, 'w')
            proc = subprocess.Popen([self.fds_command,'cone.fds'],
                                    env = my_env,
                                    stdout=devnull,
                                    stderr=devnull)
            proc.wait()

            devnull.close()
            Time,data = self.read_fds_output()
            os.chdir(cwd)
            return Time,data

     def read_fds_output(self):
        data={}
        Time=np.array([])
        for key,(filename,dname,conversion_factor) in self.simulation.items():
             out = np.genfromtxt(filename,delimiter=",",names=True,skip_header=1)
             data[key]=[out['Time'],out[dname]*conversion_factor]
        return Time,data
         
             
             
     def fitness(self, x):
         fit=0
         x=np.reshape(x,len(self.params))
         T,data = self.run_fds(x)
         Fi={}
         for key,d in data.items():
             T,F = d
             etime,edata = self.exp_data[key] 
             Fi[key]=np.interp(etime,T,F,left=0,right=0)
         fit = self.fitnessfunc(self.exp_data,Fi)
         return fit 

     def fitnessfunc(self,exp_data,sim_data):
        fitness = 0.0
        Nk = len(exp_data)
        for key,(etime,edata) in exp_data.items():
            sdata = sim_data[key]
            weight = self.data_weights[key]
            diff = weight*np.mean((edata-sdata)**2)/np.var(edata)
            fitness += 1.0/Nk * diff
        return fitness

     def get_bounds(self):
         return [tuple(bounds) for name,bounds in self.params]
     


def main():
    return

if __name__ == "__main__":
    main()
    fname=sys.argv[1]
    cfg = Config(fname)
    model = Model(exp_data=cfg.exp_data,
                        params=cfg.variables,
                        simulation=cfg.simulation,
                        fds_command=cfg.fds_command,
                        template=open(cfg.fname,"r").read())
    x=[np.mean(x) for x in model.get_bounds()]
    fit = model.fitness(x)
    print(fit)

