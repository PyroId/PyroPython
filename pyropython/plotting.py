import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from .utils import read_data, ensure_dir
from .config import read_plots
import argparse
import os
from .model import Model
import sklearn.ensemble as skl
simulation_dir = "Best/"
output_dir = "Figs/"


def proc_commandline():
    global simulation_dir, output_dir
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", help="Input file name")
    parser.add_argument("-o", "--output_dir",
                        help="Output directory for figure [default: Figs]",
                        default="Figs")
    parser.add_argument("-s", "--simulation_dir",
                        help=("Directory contaning the simulation output "
                              "files for comparison [default: Best]"),
                        default="Best")
    args = parser.parse_args()
    simulation_dir = args.simulation_dir
    output_dir = args.output_dir
    cfg = read_plots(args.fname)
    return cfg


def plot_exp(cfg):
    for key, (etime, edata) in cfg.raw_data.items():
        fig, ax = plt.subplots()
        plt.plot(etime, edata, label="exp ")
        stime, sdata = cfg.exp_data[key]
        plt.plot(stime, sdata, label="smoothed")
        plt.xlabel("Time")
        plt.ylabel(key)
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(0, ymax)
        plt.legend()
        ax.grid(True)
        plt.savefig("%s/Exp_%s.pdf" % (output_dir, key), bbox_inches="tight")
        plt.close()
    return


def read_fds_output(cfg):
    data = {}
    for key, line in cfg.simulation.items():
        T, F = read_data(**line, cwd=simulation_dir)
        data[key] = T, F
    return data


def plot_sim(cfg):
    data = read_fds_output(cfg)
    for key, (stime, sdata) in data.items():
        etime, edata = cfg.exp_data[key]
        fig, ax = plt.subplots()
        plt.plot(etime, edata, label="Exp ")
        plt.plot(stime, sdata, label="Sim ")
        plt.xlabel("Time")
        plt.ylabel(key)
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(0, ymax)
        plt.legend()
        ax.grid(True)
        plt.savefig("%s/Sim_%s.pdf" % (output_dir, key), bbox_inches="tight")
        plt.close()
    return


def plot_feature_importance(cfg, result):
    model = result.models[-1]
    X = result.Xi
    if not (isinstance(model, skl.RandomForestRegressor) or
            isinstance(model, skl.ExtraTreesRegressor)):
        return
    importances = model.feature_importances_
    names = [name for name, bounds in cfg.variables]
    std = np.std([tree.feature_importances_ for tree in model.estimators_],
                 axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")
    n_features = len(X[0])
    for f in range(n_features):
        print("{n}.  {var} : ({importance})".format(n=f + 1,
                                                    var=names[indices[f]],
                                                    importance=importances[indices[f]]))
    # Plot the feature importances of the forest
    fig, ax = plt.subplots()
    ax.set_title("Feature importances")
    ax.bar(range(n_features), importances[indices],
           color="r", yerr=std[indices], align="center")
    ax.set_xticks(range(n_features))
    ax.set_xticklabels([names[i] for i in indices])
    ax.set_xlim([-1, n_features])
    ax.set_xlabel("Variable")
    ax.set_ylabel("Importance score")
    plt.savefig("%s/feature_importances.pdf" % output_dir, bbox_inches="tight")


def do_plotting(cfg):

    for name, line in cfg.plots.items():
        if line['type'] in ("comparison", "simulation"):
            fds_data = read_fds_output(cfg)
        fig, ax = plt.subplots()
        nlines = len(line['variables'])
        colors = plt.cm.jet(np.linspace(0, 1, nlines))
        for var_num, var in enumerate(line['variables']):
            # plot experimental data if needed
            if line['type'] in ("comparison", "experimental"):
                etime, edata = cfg.exp_data[var]
                label = line['labels'][var_num]
                if line['type'] == "comparison":
                    label = label + " (exp)"
                ax.plot(etime, edata, label=label, color=colors[var_num])
            # plot simulation data if needed
            if line['type'] in ("comparison", "simulation"):
                if line['type'] == "comparison":
                    lty = "--"
                else:
                    lty = "-"
                stime, sdata = fds_data[var]
                label = line['labels'][var_num]
                if line['type'] == "comparison":
                    label = label + " (sim)"
                ax.plot(stime, sdata, label=label,
                        color=colors[var_num], linestyle=lty)

        plt.legend()
        ax.set_xlabel(line["xlabel"])
        ax.set_ylabel(line["ylabel"])
        ax.grid(True)
        print("%s/%s.pdf" % (output_dir, name))
        plt.savefig("%s/%s.pdf" % (output_dir, name), bbox_inches="tight")
        plt.close()
        #print("Objective: %E" % check_fit(cfg))


def check_fit(cfg):
    fit = 0
    data = read_fds_output(cfg)
    weight_sum = 0.0
    for key, d in data.items():
        T, F = d
        etime, edata = cfg.exp_data[key]
        # interpolate simulation data to experiment
        Fi = np.interp(etime, T, F)
        weight = cfg.var_weights[key]
        weight_sum += weight
        opts = cfg.objective_opts
        fit += weight*cfg.objective_function(edata, Fi,
                                             cfg.data_weights[key], **opts)
        print(key, weight, fit)
    fit = fit/weight_sum
    return fit

def main():
    cfg = proc_commandline()
    ensure_dir(os.path.join("./", output_dir))
    plot_exp(cfg)
    do_plotting(cfg)


if __name__ == "__main__":
    main()
