import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from . import config as cfg
from .utils import read_data, ensure_dir
import argparse
import os
from .model import Model
import sklearn.ensemble as skl  
simulation_dir="Best/"
output_dir="Figs/"

def proc_commandline():
    global simulation_dir,output_dir
    parser = argparse.ArgumentParser()
    parser.add_argument("fname",help="Input file name")
    parser.add_argument("-o", "--output_dir", 
                        help="Output directory for figure [default: Figs]",
                        default="Figs")
    parser.add_argument("-s", "--simulation_dir", 
                        help="Directory contaning the simulation output files for comparison [default: Best]",
                        default="Best")
    args=parser.parse_args()
    simulation_dir=args.simulation_dir
    output_dir=args.output_dir
    cfg.read_config(args.fname)
    return cfg

def plot_exp(cfg):
    for key,(etime,edata) in cfg.raw_data.items():
        fig,ax = plt.subplots()
        plt.plot(etime,edata,label="exp ")
        stime,sdata = cfg.exp_data[key]
        plt.plot(stime,sdata,label="smoothed")
        plt.xlabel("Time")
        plt.ylabel(key)
        ymin,ymax = ax.get_ylim()
        ax.set_ylim(0,ymax)
        plt.legend()
        ax.grid(True)
        plt.savefig("%s/Exp_%s.pdf" % (output_dir,key),bbox_inches="tight")
        plt.close()
    return

def read_fds_output(cfg):
        data={}
        for key,line in cfg.simulation.items():
             T,F = read_data(**line, cwd=simulation_dir) 
             data[key]=T,F
        return data

def plot_sim(cfg):
    data=read_fds_output(cfg)
    for key,(stime,sdata) in data.items():
        etime,edata = cfg.exp_data[key]
        fig,ax = plt.subplots()
        plt.plot(etime,edata,label="Exp ")
        plt.plot(stime,sdata,label="Sim ")
        plt.xlabel("Time")
        plt.ylabel(key)
        ymin,ymax = ax.get_ylim()
        ax.set_ylim(0,ymax)
        plt.legend()
        ax.grid(True)
        plt.savefig("%s/Sim_%s.pdf" % (output_dir,key),bbox_inches="tight")
        plt.close()       
    return
    
def plot_feature_importance(cfg,result):
    model  =result.models[-1]
    X      =result.Xi
    if not isinstance(model,skl.RandomForestRegressor) or not isinstance(model,skl.ExtraTreesRegressor):
        return

    importances =  model.feature_importances_
    names       =  [name for name,bounds in cfg.params]
    std = np.std([tree.feature_importances_ for tree in model.estimators_],
             axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")

    for f in range(X.shape[1]):
        print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

    # Plot the feature importances of the forest
    fig,ax = plt.subplots()
    ax.title("Feature importances")
    ax.bar(range(X.shape[1]), importances[indices],
           color="r", yerr=std[indices], align="center")
    ax.xticks(range(X.shape[1]), indices)
    ax.xlim([-1, X.shape[1]])
    plt.savefig("%s/feature_importances.pdf" % output_dir,bbox_inches="tight")

def do_plotting(cfg):
    
    for name,line in cfg.plots.items():
        if line['type'] in ("comparison","simulation"):
            fds_data=read_fds_output(cfg)
        fig,ax = plt.subplots()
        nlines = len(line['variables'])
        colors = plt.cm.jet(np.linspace(0,1,nlines))
        for var_num,var in enumerate(line['variables']):
            # plot experimental data if needed
            if line['type'] in ("comparison","experimental"):
                etime,edata = cfg.exp_data[var]
                label  = line['labels'][var_num]
                if line['type']=="comparison":
                    label = label + " (exp)"
                ax.plot(etime,edata,label=label,color=colors[var_num])
            # plot simulation data if needed
            if line['type'] in ("comparison","simulation"):
                if line['type']=="comparison":
                    lty = "--"
                else:
                    lty = "-"
                stime,sdata = fds_data[var]
                label  = line['labels'][var_num]
                if line['type']=="comparison":
                    label = label + " (sim)"
                ax.plot(stime,sdata,label=label,color=colors[var_num],linestyle=lty)

        plt.legend()
        ax.set_xlabel(line["xlabel"])
        ax.set_ylabel(line["ylabel"])
        ax.grid(True)
        print("%s/%s.pdf" % (output_dir,name))
        plt.savefig("%s/%s.pdf" % (output_dir,name),bbox_inches="tight")
        plt.close()   

def dump_data(cfg):
    smooth = []
    raw    = []
    sim    = []
    for key,(etime,edata) in cfg.exp_data.items():
        smooth.append(etime)
        smooth.append(edata)
        print(key,np.mean(edata))
    smooth = np.vstack(smooth)
    np.savetxt("smooth.csv",smooth.T,header=",".join(cfg.exp_data.keys())) 
    try:
        fds_data=read_fds_output(cfg)
    except:
        print("No FDS data available")
        return
    for key,(stime,sdata) in fds_data.items():
        sim.append(stime)
        sim.append(sdata)
        print(key,np.mean(sdata))
    sim = np.vstack(sim)
    np.savetxt("sim.csv",sim.T,header=",".join(fds_data.keys()))
    
    model = Model(exp_data=cfg.exp_data,
                  params=cfg.variables,
                  simulation=cfg.simulation,
                  fds_command=cfg.fds_command,
                  templates=cfg.templates,
                  data_weights=cfg.data_weights)
    print("fit:",model.fitnessfunc(cfg.exp_data,fds_data))
    return           

def main():
    cfg=proc_commandline()
    ensure_dir(os.path.join("./",output_dir))
    #dump_data(cfg)
    plot_exp(cfg)
    do_plotting(cfg)

if __name__=="__main__":
    main()
