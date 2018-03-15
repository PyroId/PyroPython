# -*- coding: utf-8 -*-
 
 
"""pyropython.filter: Data filtering functions for smoothing experimental data"""

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern,WhiteKernel,RBF
from numpy import array,newaxis,squeeze

def gp_filter(x,y):
    kernel =  1.0*Matern(length_scale=20.0, length_scale_bounds=(1e-1, 1000.0),nu=2.5) \
              + WhiteKernel(noise_level=5.0, noise_level_bounds=(1e-1, 1000.0))
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=0,alpha=0.0)
    gp.fit(x[:,newaxis],y[:,newaxis])
    return squeeze(gp.predict(x[:,newaxis]))

def butterworth_filter(x,y):
	return

def moving_average_filter(x,y):
	return