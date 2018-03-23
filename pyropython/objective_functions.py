# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 15:02:16 2018

@author: tstopi
"""

from numpy import mean,abs,var
import sys

def get_objective_function(name="standardized_moment",**kwargs):
    if name in objective_functions:
        func = objective_functions[name]
    else:
        sys.exit("Unkonwn objective function %s" % name)
    return lambda x,y,w: func(x,y,w,**kwargs)

def standardized_moment(self,edata,sdata,weights,p=2):
    """
    Measure based on standardized moment: 
        E[(sum_i ( w_i *(y-y_hat) )^p]/std(weights*y)^p
    """
    dev = (weights*abs(edata-sdata))**p
    return mean(dev)/var(weights*edata)**(p/2.0)

objective_functions={"standardized_moment": standardized_moment}