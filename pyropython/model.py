# -*- coding: utf-8 -*-
import tempfile
import os
import numpy as np
import subprocess
from pyropython import config as cfg
from jinja2 import Template
from pyropython.utils import read_data
import sys


class Model:
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
                 objective_opts={}):
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

    def write_fds_file(self, outname, template, x):
        f = open(outname, "tw")
        template = Template(template)
        variables = {self.params[n][0]: var for n, var in enumerate(x)}
        outfile = template.render(**variables)
        f.writelines(outfile)
        f.flush()
        f.close()

    def run_fds(self, x):
        cwd = os.getcwd()
        tempfile.tempdir = self.tempdir
        my_env = os.environ.copy()
        my_env["OMP_NUM_THREADS"] = "1"
        pwd = tempfile.mkdtemp(prefix="Cone_")
        os.chdir(pwd)
        devnull = open(os.devnull, 'w')
        for fname, template in self.templates:
            outname = os.path.join(pwd, fname)
            self.write_fds_file(outname, template, x)
            proc = subprocess.Popen([self.command, fname],
                                    env=my_env,
                                    cwd=pwd,
                                    stderr=devnull,
                                    stdout=devnull)
            proc.wait()
        devnull.close()
        data = self.read_fds_output()
        os.chdir(cwd)
        return data, pwd

    def read_fds_output(self, directory=""):
        data = {}
        for key, line in self.simulation.items():
            T, F = read_data(**line)
            data[key] = T, F
        return data

    def fitness(self, x, return_directory=True):
        fit = 0
        x = np.reshape(x, len(self.params))
        data, pwd = self.run_fds(x)
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
        if return_directory:
            return fit, pwd
        else:
            return fit

    def get_bounds(self):
        return [tuple(bounds) for name, bounds in self.params]


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
