import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from . import config as cfg
import argparse

simulation_dir="Best"
output_dir="Figs"

def proc_commandline():
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
        for key,(filename,dname,conversion_factor) in cfg.simulation.items():
             out = np.genfromtxt(simulation_dir+"/"+filename,delimiter=",",names=True,skip_header=1)
             data[key]=[out['Time'],out[dname]*conversion_factor]
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

def main():
    cfg=proc_commandline()
    print(cfg.optimizer_opts)
    plot_exp(cfg)
    plot_sim(cfg)
    print(simulation_dir)

if __name__=="__main__":
    main()
