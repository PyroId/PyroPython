# -*- coding: utf-8 -*-
import tempfile
import os
import shutil
import numpy as np
import subprocess
from jinja2 import Environment,FileSystemLoader
from pyropython import config as cfg
from pyropython.utils import read_data
import sys


class Model:
    """ Class for evaluating simulation models

    This class provides methods to create input files, execute simulator and
    process output files. The class was originally written to be used in
    parameter estimation for the solid pyrolysis model in Fire Dynamics
    Simulator. However the class can be used with any executable that accepts
    text file inputs and outputs .csv files.
    """

    def __init__(self,
                 exp_data={},
                 params={},
                 simulation={},
                 var_weights={},
                 data_weights={},
                 templates=[],
                 command="",
                 objective_function=None,
                 tempdir=None,
                 objective_opts={},
                 ):
        """ Initialize model

        Args:
            exp_data (:dict): Experimental data in format {key: (T, F) ...},
                where T is the independent variable and F dependent variable
            params (:list): Parameter names and bounds in format
                [(name,(minval,maxval))]
            simulation (:dict):  Data lines for pyropython.utils.read_data
                function. Keys should mach those in exp_data.
            var_weights (:dict): Weights for each of the variables (keys)
                defined in the exp_data and simulation dictionaries. The
                weights are given in format:  {key: W}, where "key" is the key
                in exp_data and W is a weight.
            data_weights (:dict): data_weights for individual data points.
                Given in format: {key: W}, where W is a weight vector.
                NOTE: W should be equal length with corresponding exp_data.
        """
        self.exp_data = exp_data
        self.params = params
        self.simulation = simulation
        self.var_weights = var_weights
        self.data_weights = data_weights
        self.templates = templates
        self.command = command
        self.tempdir = tempdir
        self.objective_function = objective_function
        self.objective_opts = objective_opts

    def render_template(self, outname, template, x):
        """ Renders templates.

        Args:
            outname (:string): Name of the output file
            template (:string): Jinja2 template to be rendered
            x (list like): parameter vector. The values in x will be used to
                fill the variables in the templates. Values in x should be
                given in the same order as the keys in self.params.
        """
        f = open(outname, "tw")
        variables = {self.params[n][0]: var for n, var in enumerate(x)}
        outfile = template.render(**variables)
        f.writelines(outfile)
        f.flush()
        f.close()

    def run_simulator(self, x):
        """ Renders templates, runs simulator and reads output
         Args:
            x (list like): parameter vector. The values in x will be used to
                fill the variables in the templates. Values in x should be
                given in the same order as the keys in self.params.
        Returns:
            data (:dict): Dictionary, with entries key: (T,F) where "key" is a
                key from the simulation dict, T is the indpendent variable
                and F is the dependent variable
            pwd (:string): Working directory, where the simulation was run.
        """
        cwd = os.getcwd()
        tempfile.tempdir = self.tempdir
        my_env = os.environ.copy()
        my_env["OMP_NUM_THREADS"] = "1"
        pwd = tempfile.mkdtemp(prefix="Cone_")
        """ Jinja2 environments/templates cannot be pickled, so the Environments
            need to be created here.
        """
        env = Environment(loader=FileSystemLoader(cwd))
        os.chdir(pwd)
        devnull = open(os.devnull, 'w')
        for fname in self.templates:
            outname = os.path.join(pwd, fname)
            template = env.get_template(fname)
            self.render_template(outname, template, x)
            with  open("%s_stdout.txt" % fname,"wb") as out:
                proc = subprocess.Popen([self.command, fname],
                                         env=my_env,
                                         cwd=pwd,
                                         stderr=out,
                                         stdout=out)
            proc.wait()
        devnull.close()
        data = self.read_output()
        os.chdir(cwd)
        return data, pwd

    def read_output(self):
        """ Reads output as defined in Model.simulation dict and returns a
            dictionary.

        Returns:
            data: Dictionary, with entries key: (T,F) where "key" is the key
            from the Model.simulation dict, T is the indpendent variable and
            F is the dependent variable
        """
        data = {}
        for key, line in self.simulation.items():
            T, F = read_data(**line)
            data[key] = T, F
        return data

    def fitness(self, x, queue=None):
        """Runs model, reads ouput and evalutes objective function.

        Args:
            x (list like): parameter vector. Values for use in the
                Model.template(s). The values are given in the same order as
                variables in Model.params.
            queue (a Queue, optional): Queue for saving results. Defaults to
                None. If provided,a tuple (xi,fi,pwd) is put() on the queue.
                The valueas xi, fi and pwd are the paramater vector, fitness
                value and working directory (string), respectively. The user is
                responsible for cleaning up the working directories.

        Returns:
            fit (:float): Fitness value.
        """
        fit = 0
        x = np.reshape(x, len(self.params))
        data, pwd = self.run_simulator(x)
        weight_sum = 0.0
        for key, d in data.items():
            T, F = d
            etime, edata = self.exp_data[key]
            # interpolate simulation data to experiment
            Fi = np.interp(etime, T, F)
            weight = self.var_weights[key]
            weight_sum += weight
            opts = self.objective_opts
            fit += weight*self.objective_function(edata, Fi,
                                                  self.data_weights[key],
                                                  **opts)
        fit = fit/weight_sum
        # possibly save the results.
        if queue:
            queue.put((fit, x, pwd))
        else:
            shutil.rmtree(pwd)
        return fit

    def penalized_fitness(self, x, c=100, queue=None):
        """Penalty function version of fitness(), for use with unconstrained
        optimization algorithms. Calls fitness and adds a penaltu term. For
        values far aoutside the bounds, the fitness function is not called.

        Args:
            x (list like): parameter vector. Values for use in the
                Model.template(s). The values are given in the same order as
                variables in Model.params. Passed on to fitness()
            c (float): coefficient fot the penalty function:
                p(x) = c * min(0,x-x_min)**2 + c * max(0,x-x_max)**2

        Returns:
            res (float): fitness faluye with the penalty term added
        """
        res = 0
        for n, (minval, maxval) in enumerate(self.get_bounds()):
            res += c * min(0, x[n]-minval)**2 + c * max(0, x[n]-maxval)**2
        # Don't evaluate fitness for very wrong inputs
        if res <= 1:
            res += self.fitness(x, queue)
        elif queue:
             queue.put((res, x, None))
        return res

    def get_bounds(self):
        """Returns bounds for Model.params

        Returns:
            bounds (list): list of tuples in format  [(minval,maxval)]
        """
        return [tuple(bounds) for name, bounds in self.params]


    def print_info(self):
        """ Print model info
        """
        print("Model information")
        print("="*30)
        print("Parameters:")
        print()
        for name,(minval,maxval) in  self.params:
            print("%30s: [%.3e,%.3e]" % (name,minval,maxval))
        
        print("Variable weights:")
        print()
        for name,weight in  self.var_weights.items():
            print("%30s: %.3e" % (name,weight))

        print("Data weights:")
        print()          
        for name, weights in  self.data_weights.items():
            print("%30s: mean: %.3e min: %.3e max: %.3e" % (name,np.mean(weights),np.min(weights),np.max(weights)))
        
        print("Templates:")
        print()  
        for name in self.templates:
            print(name)
        print()
        print("Command: %s" % self.command) 
        print("Temp dir: %s" % self.tempdir) 
        print("Objective function: %s " % self.objective_function.__name__) 
        print("Objective options") 
        print(self.objective_opts)

def main():
    fname = sys.argv[1]
    cfg.read_config(fname)
    model = Model(cfg.case)
    x = [np.mean(x) for x in model.get_bounds()]
    fit = model.fitness(x)
    print(fit)
    return


if __name__ == "__main__":
    main()
