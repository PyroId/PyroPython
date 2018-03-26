# -*- coding: utf-8 -*-
 
 
"""pyropython.filter: Data filtering functions for smoothing experimental data"""

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern,WhiteKernel,RBF
from numpy import array,newaxis,squeeze,median
from scipy.signal import medfilt,firwin,convolve,kaiserord ,lfilter



def gp_filter(x,y,**kwargs):
    kernel =  1.0*Matern(length_scale=20.0, length_scale_bounds=(1e-1, 1000.0),nu=2.5) \
              + WhiteKernel(noise_level=0.0, noise_level_bounds=(1e-1, 1000.0))
    gp = GaussianProcessRegressor(kernel=kernel)
    gp.fit(x[:,newaxis],y[:,newaxis])
    return squeeze(gp.predict(x[:,newaxis]))

def butterworth_filter(x,y,f,**kwargs):
  return y

def fir_filter(x,y,cutoff=0.0125,width=0.0125):
   numtaps, beta = kaiserord(65, width)
   taps = firwin(numtaps, cutoff, window=('kaiser', beta),
                 scale=False)
   return convolve(y,taps,mode="same")

def moving_average_filter(x,y,width=10,window='hanning'):
  return y

def median_filter(x,y,width=10):
  if width % 2 == 0:
    kernel_size = width+1 
  else:
    kernel_size = width
  return medfilt(y,kernel_size=kernel_size)

def none_filter(x,y,**kwargs):
  return y

filter_types = {"GP": gp_filter,
                "median": median_filter,
                "FIR": fir_filter,
                "MA": moving_average_filter,
                "None": none_filter
        };

def get_filter(name):
  if name not in filter_types:
    sys.exit("Warning: unknown filter type %s." %name)
  return filter_types.get(name, none_filter)
                
def main():
    return

if __name__=="__main__":
    main()