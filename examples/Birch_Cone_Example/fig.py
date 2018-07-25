# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 13:39:05 2018

@author: tstopi
"""

import numpy as np
import matplotlib.pyplot as plt

kW = "50"

exp = np.genfromtxt("Experimental_Data/Birch_%skW.csv"  % kW, 
                    delimiter =",",
                    skip_header=1,
                    names=True)

fds = np.genfromtxt("Best/birch_cone_%s_hrr.csv"  % kW, 
                    delimiter =",",
                    skip_header=1,
                    names=True)



plt.plot(exp["Time"],exp["MLR"])
plt.plot(fds["Time"],fds["MLR_TOTAL"]*1000)
