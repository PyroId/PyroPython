# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 09:49:36 2018

@author: tstopi
"""
import sys
import os
import yaml as y
from numpy import float64, interp, ones
import warnings
from collections import namedtuple
from .utils import read_data
from .objective_functions import get_objective_function
from .model import Model

case = None
run_opts = namedtuple('run_opts',
                      ['num_jobs', 'max_iter', 'num_points',
                       'num_initial', 'initial_design',
                       'optimizer_opts'])
run_opts.num_jobs = 1
run_opts.max_iter = 50
run_opts.num_points = 100
run_opts.num_initial = 100
run_opts.initial_design = "rand"
run_opts.optimizer_opts = {"base_estimator":       "ET",
                           "acq_func":             "gp_hedge",
                           "acq_optimizer":        "auto",
                           "n_initial_points":      100,
                           "acq_optimizer_kwargs":
                           {"n_points": 10000,
                            "n_restarts_optimizer": 5,
                            "n_jobs": 1},
                           "acq_func_kwargs":       {"xi": 0.01, "kappa": 1.96}
                           }

def _check_required_fields(dict,req_fields):
    """
    Tries to find fields in a dict.
    Input:
        dict - dictinionary to check
        req_fields - list of required keys
    Returns:
        not_found - list of fields not found.
    """
    not_found=[]
    for field in req_fields:
        if field not in req_fields:
            not_found.append(field)
    return not_found

def _set_data_line_defaults(line,
                            ind_col_name="Time",
                            normalize=False,
                            conversion_factor=1.0,
                            header=1,
                            filter_type="None",
                            filter_opts={},
                            gradient=False):
    """
    This is a convenience function to set the default values for data line
    and check for missing values
    input:
        line - dictionary containing the data line description
    kwargs:
        optional arguments and their default values
    """
    not_found = _check_required_fields(line, ["dep_col_name", "fname"])
    if not_found:
        raise ValueError("required field(s) %s not found." % str(not_found))
    line.setdefault("ind_col_name", ind_col_name)
    line.setdefault("normalize", normalize)
    line.setdefault("conversion_factor", conversion_factor)
    line.setdefault("header", header)
    line.setdefault("filter_type", filter_type)
    line.setdefault("filter_opts", filter_opts)
    line.setdefault("gradient", gradient)
    return line


def read_model(input):
    """
    This function creates a initialized Model object based on the dictionary
    "cfg". The dictionary is assumed to be produced by reading a yaml file
    """
    if isinstance(input, str):
        lines = open(input, "r").read()
        cfg = y.load(lines)
    elif isinstance(input, dict):
        cfg = input
    """
    Check for required fields
    """
    not_found = _check_required_fields(cfg, ["simulation",
                                             "experiment",
                                             "variables",
                                             "templates"])
    if not_found:
        sys.exit("required field(s) %s not found in config." % str(not_found))

    """
     yaml is sometimes unable to correctly convert str to float.
     For example, scientific notation like "1e15" will  fail.
     Here we explicitly attempt to convert numeric input to floats
    """
    variables = list(cfg['variables'].items())
    for n, (name, bounds) in enumerate(variables):
        try:
            variables[n] = (name, float64(bounds))
        except ValueError:
            sys.exit("Bounds for %s need to benumeric (for now)." % name)
    simulation = cfg['simulation']
    experiment = cfg['experiment']

    for key in cfg['simulation']:
        if key not in cfg['experiment']:
            sys.exit("No experimental data for variable %s" % key)
    for key in cfg['experiment']:
        if key not in cfg['simulation']:
            sys.exit("No simulation data for variable %s" % key)

    if len(cfg['templates']) < 1:
        sys.exit("Templates list cannot be empty.")
    templates = []
    for fname in cfg['templates']:
        templates.append((fname, open(fname, 'r').read()))

    # set default values for data lines
    for key, line in simulation.items():
        line = _set_data_line_defaults(line)

    exp_data = {}
    for key, line in experiment.items():
        """
        For experimental data we expect only one header line unless indicates
        otherwise
        """
        line = _set_data_line_defaults(line,
                                       header=0)
        exp_data[key] = read_data(**line)

    """
    Read and process the "objective" dictionary
    """
    obj = cfg.get("objective", {})
    objective_name = obj.get("type", "mse")
    objective_function = get_objective_function(objective_name)
    objective_opts = obj.get("objective_opts", {})
    data_weights = obj.get("data_weights", {})
    var_weights = obj.get("var_weights", {})
    """
     Process weights for each  variable.
     if weights are not given, set weight to 1.0 for all datasets
    """
    if len(var_weights) > 0:
        if set(var_weights) != set(simulation):
            print(
                "If weights are defined for one or more variables they " +
                "should  be defined for all variables in 'experiment'" +
                " and 'simulation':")
            print(set(var_weights).symmetric_difference(set(simulation)))
            sys.exit(0)
    else:
        for key in experiment:
            var_weights[key] = 1.0

    """
    Weights can be read from a file as a list of tuples in the format
     [(x,w),(x,w),(x,w)] where x is the independent variable and
     w is the weight
     weights will be interpolated to coincide with the experimental data
    """
    for key, (etime, edata) in exp_data.items():
        if key in data_weights:
            entry = data_weights[key]
            if isinstance(dict, entry):
                wtime, weights = read_data(**entry)
            elif isinstance(list, entry):
                wtime, weights = zip(*entry)
            else:
                warnings.warn(("Problem with weights for variable %s."
                               "Weigths set to one.") % key)
                wtime = etime
                weights = ones(1, len(etime))
        else:
            wtime = etime
            weights = ones(len(etime))
        weightsi = interp(etime, wtime, weights)
        data_weights[key] = weightsi

    if "fds_command" not in cfg:
        warnings.warn("fds_command not defined. Using 'fds'")
    fds_command = cfg.get("fds_command", "fds")
    tempdir = os.path.join(os.getcwd(), "Work/")
    return Model(exp_data=exp_data,
                 params=variables,
                 simulation=simulation,
                 var_weights=var_weights,
                 data_weights=data_weights,
                 templates=templates,
                 command=fds_command,
                 objective_function=objective_function,
                 tempdir=tempdir,
                 objective_opts=objective_opts)


def read_plots(input):
    """
    This function reads a config file and gathers all data needed for 'plots'
    """
    if isinstance(input, str):
        lines = open(input, "r").read()
        cfg = y.load(lines)
    elif isinstance(input, dict):
        cfg = input

    plot_data = namedtuple('plot_data',
                           ['raw_data',
                            'simulation',
                            'exp_data',
                            'plots'
                            ])
    simulation = cfg.get('simulation',{})
    experiment = cfg.get('experiment',{})
    for key, line in simulation.items():
        line = _set_data_line_defaults(line)
    # set default values for data lines
    plot_data.simulation = simulation
    plot_data.plots = cfg.get('plots',{})
    plot_data.exp_data = {}
    plot_data.raw_data = {}
    for key, line in experiment.items():
        """
        For experimental data we expect only one header line unless indicates
        otherwise
        """
        line = _set_data_line_defaults(line,
                                       header=0)
        plot_data.exp_data[key] = read_data(**line)
        tmp = dict(line)  # create copy
        tmp["filter_type"] = "None"
        plot_data.raw_data[key] = read_data(**tmp)

    return plot_data


def proc_general_options(input):
    if isinstance(input, str):
        lines = open(input, "r").read()
        cfg = y.load(lines)
    elif isinstance(input, dict):
        cfg = input
    run_opts = namedtuple('run_opts',
                          ['num_jobs', 'max_iter', 'num_points',
                           'num_initial', 'initial_design',
                           'optimizer_opts'])
    run_opts.max_iter = cfg.get("max_iter", 1)
    run_opts.num_jobs = cfg.get("num_jobs", 1)
    run_opts.num_points = cfg.get("num_points", 1)
    run_opts.num_initial = cfg.get("num_initial", 1)
    run_opts.initial_design = cfg.get("initial_design", "rand")
    run_opts.optimizer_opts = cfg.get("optimizer", {})
    return run_opts


def read_config(fname):
    """
    Reads and processes pyropython config file
    """
    case = read_model(fname)
    run_opts = proc_general_options(fname)
    return case,run_opts

def main():
    fname = sys.argv[1]
    read_config(fname)
    print(run_opts.num_jobs)
    print(len(case.exp_data))


if __name__ == "__main__":
    main()
