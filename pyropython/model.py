import tempfile
import os
import numpy as np
import subprocess
from . import config as cfg
from jinja2 import Template
from .utils import read_data
from .objective_functions import get_objective_function
import sys


class Model:
     def __init__(self,exp_data,params,simulation,fds_command,templates,data_weights,var_weights):
         self.exp_data = exp_data
         self.params = params
         self.simulation = simulation
         self.var_weights = var_weights
         self.data_weights = data_weights
         self.num_fitness = 0
         #self.template = Template(template)
         self.templates = templates
         self.points   = []
         self.fds_command = fds_command
         self.tempdir=os.getcwd()+"/Work/"
         self.fitness_function = get_objective_function() 
     def write_fds_file(self,outname,template,x):
        f=open(outname,"tw")
        template=Template(template)
        variables = {self.params[n][0]: var for n,var in enumerate(x)}
        outfile = template.render(**variables)
        f.writelines(outfile)
        f.flush()
        f.close()

     def run_fds(self,x):
        cwd = os.getcwd()
        tempfile.tempdir=self.tempdir
        my_env = os.environ.copy()
        my_env["OMP_NUM_THREADS"] = "1"
        pwd = tempfile.mkdtemp(prefix="Cone_")
        os.chdir(pwd)
        devnull = open(os.devnull, 'w')
        for fname,template in self.templates:
            outname = os.path.join(pwd,fname)
            self.write_fds_file(outname,template,x)
            proc = subprocess.Popen([self.fds_command,fname],
                                    env = my_env,
                                    cwd=pwd,
                                    stderr = devnull,
                                    stdout = devnull)
            proc.wait()
        devnull.close()
        data = self.read_fds_output()
        os.chdir(cwd)
        return data,pwd

     def read_fds_output(self, directory=""):
        data={}
        for key,line in self.simulation.items():
             T,F = read_data(**line) 
             data[key]=T,F
        return data
        
             
     def fitness(self, x):
         fit=0
         x=np.reshape(x,len(self.params))
         data,pwd = self.run_fds(x)
         weight_sum = 0.0
         for key,d in data.items():
             T,F = d
             etime,edata = self.exp_data[key] 
             Fi=np.interp(etime,T,F,left=0,right=0)
             weight = self.data_weights[key]
             weight_sum +=weight
             fit    = weight*self.fitnessfunc(edata,Fi,
                                              self.var_weights[key])
         fit = fit/weight_sum
         return fit,pwd 



     def get_bounds(self):
         return [tuple(bounds) for name,bounds in self.params]
     


def main():
    fname=sys.argv[1]
    cfg.read_config(fname)
    model = Model(exp_data=cfg.exp_data,
                        params=cfg.variables,
                        simulation=cfg.simulation,
                        fds_command=cfg.fds_command,
                        template=open(cfg.fname,"r").read())
    x=[np.mean(x) for x in model.get_bounds()]
    fit = model.fitness(x)
    print(fit)
    return

if __name__ == "__main__":
    main()


