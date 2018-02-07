import tempfile
import os
import numpy as np
import copy
import subprocess
from multiprocessing import Lock
from config import Config
import sys


class Model:
     def __init__(self,exp_data,params,simulation,fds_command,template):
         self.exp_data = exp_data
         self.params = params
         self.simulation = simulation
         self.num_fitness = 0
         self.template =template
         self.points   = []
         self.save_fitness  = []
         self.fds_command = fds_command

     def write_fds_file(self,outname,template,x):
        f=open(outname,"w")
        outfile=copy.deepcopy(template)
        for m,line in enumerate(outfile):
            for n,var in enumerate(x):
                varname = "$%s" % (self.params[n][0])
                outfile[m]=outfile[m].replace(varname,str(var))
        f.writelines(outfile)
        f.close() 

     def run_fds(self,x):
        cwd = os.getcwd()
        tempfile.tempdir=cwd
        my_env = os.environ.copy()
        my_env["OMP_NUM_THREADS"] = "1"
        with tempfile.TemporaryDirectory(prefix="Work/Cone_") as pwd:
            os.chdir(pwd)
            self.write_fds_file("cone.fds",self.template,x)
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
         with Lock():
            self.num_fitness += 1
         x=np.reshape(x,len(self.params))
         T,data = self.run_fds(x)
         Fi={}
         for key,d in data.items():
             T,F = d
             etime,edata = self.exp_data[key] 
             Fi[key]=np.interp(etime,T,F,left=0,right=0)
         fit = self.fitnessfunc(self.exp_data,Fi)
         with Lock():
             self.save_fitness.append(fit)
             self.points.append(x)
         return fit 

     def fitnessfunc(self,exp_data,sim_data):
        fitness = 0.0
        Nk = len(exp_data)
        for key,(etime,edata) in exp_data.items():
            sdata = sim_data[key]
            diff = np.sum((edata-sdata)**2/(edata-np.mean(edata))**2)
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
    model = Cone_calorimeter(exp_data=cfg.exp_data,
                        params=cfg.variables,
                        simulation=cfg.simulation,
                        fds_command=cfg.fds_command,
                        template=open(cfg.fname,"r").readlines())
    x=[np.mean(x) for x in model.get_bounds()]
    fit = model.fitness(x)
    print(fit)

