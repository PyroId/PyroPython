import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal

dat=pd.read_csv("06110001_red.CSV",header=1,encoding = "latin-1")
dat.columns = [colname.split('(')[0].strip() for colname in dat.columns]
etime = dat["Time"]
A= 283.54 # cm2 =0.01**2 m
A=A*0.01**2 # cm2 => m2
emlr =  dat["Specific MLR"]/1000.0 # g/m2/s -> kg/m2/s
b, a = signal.butter(8, 0.125) # Nyquist = 2 seconds =0.5 Hz = 1 20 seconds = 0.05
emlrbar = signal.filtfilt(b, a, emlr, method="gust")

sim_dat = np.genfromtxt("Temp/cone_devc.csv",delimiter=",",skip_header=1,names=True)
stime = sim_dat["Time"]
smlr = sim_dat["MLR"]

fig,ax = plt.subplots()
plt.plot(etime,emlrbar,label="exp")
plt.plot(stime,smlr,label="sim")
plt.xlabel("Time(s)")
plt.ylabel("MLR (kg/s)")
plt.xlim(0,500)
plt.legend()
ax.grid(True)

plt.savefig("comp.png",bbox_inches="tight")