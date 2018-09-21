# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 15:02:16 2018

@author: tstopi
"""

from numpy import mean, abs, var, percentile, maximum, finfo


def mse(edata, sdata, weights, **kwargs):
    """ standardized mean squared error

        the value of the standardized moment with p=2
            E[(sum_i ( w_i *(y_i-yhat_i) )^2]/std(w*y)^2
    """
    return standardized_moment(edata, sdata, weights, p=2)


def abs_dev(edata, sdata, weights, **kwargs):
    """ standardized absollute deviation
        the value of the standardized moment
    """
    return standardized_moment(edata, sdata, weights, p=1)


def standardized_moment(edata, sdata, weights, p=1):
    """
    Measure based on p-norm/standrdized moment:
        E[(sum_i ( w_i *abs(y_i-yhat_i) )^p]/std(w*y)^p
    where:
       edata  : y_i   , experimental data
       sdata  : yhat_i, simulation
       weights: w_i   , data weights
    All inputs are assumed to be one dimensional arrays
    of equal lengths. Important cases:
        p=1 gives the mean absolute deviation
        p=2 gives the mean squared error

    Returns:
        the value of the standardized moment
    """

    dev = (weights*abs(edata-sdata))**p
    return mean(dev)/var(weights*edata)**(p/2.0)

def relative_error(edata, sdata, weights, eps=0.001):
    """
    Measure based relative error:
        E[ w_i *abs(y_i-yhat_i)/y_i ]
    where:
       edata  : y_i   , experimental data
       sdata  : yhat_i, simulation
       weights: w_i   , data weights
    All inputs are assumed to be one dimensional arrays
    of equal lengths. Important cases:
        p=1 gives the mean absolute deviation
        p=2 gives the mean squared error

    Returns:
        the value of the standardized moment
    """
    minval = eps*mean(abs(edata))
    denumer = maximum(abs(edata),minval) 
    dev = weights*abs(edata-sdata)/denumer
    return mean(dev)

def gpyro(edata, sdata, weights,eps=0.01,p=1):
    """
    This objective function is negative of the fitness used by GPYRO:
        mean [ w_i*( y_i / (abs(y_i-yhat_i) + eps * y_i)^p ]
    """
    dev = abs(edata/(abs(edata-sdata) + eps*edata))
    return -1*mean(weights*dev**p)

objective_functions = {"standardized_moment": standardized_moment,
                       "mse": mse,
                       "abs-dev": abs_dev,
                       "rel-err": relative_error,
                       "gpyro": gpyro}


def get_objective_function(name="mse"):
    """
    Returns the objective function with the given name
    """
    if name in objective_functions:
        func = objective_functions[name.lower()]
    else:
        raise ValueError("Unkonwn objective function %s" % name)
    return func
