# -*- coding: utf-8 -*-
 
 
"""pyropython.filter: Data filtering functions for smoothing experimental data"""

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern,WhiteKernel,ConstantKernel
from numpy import array,newaxis,squeeze,median
import scipy.signal as signal 



def gp_filter(x,y,
              nu=2.5,
              length_scale=1.0, 
              length_scale_bounds=(1e-05, 100000.0),
              noise_level=1.0,
              noise_level_bounds=(1e-05, 100000.0),
              **kwargs):

  """
  This 'filter' fits a GaussianProcessRegressor with added white noise kernel to the data.
  The smoothed value is obtained as predictions from the fitted model. 
  Advantages:  Handles uneaqually sampled data, automatically adjusts parameters
  Disadvantages: Slow, automatic. 
  """
  kernel = ConstantKernel()*Matern(length_scale=length_scale,length_scale_bounds=length_scale_bounds,nu=2.5) +\
           WhiteKernel(noise_level=noise_level,noise_level_bounds=noise_level_bounds)
  gp = GaussianProcessRegressor(kernel=kernel,normalize_y=True)
  gp.fit(x[:,newaxis],y[:,newaxis])
  return squeeze(gp.predict(x[:,newaxis]))

def butterworth_filter(x,y,cutoff=0.0125,width=0.0125,**kwargs):
  """
  Applies a butterworth filter with given cutoff and passband width
  The Scipy 'buttord' and butter filters are used to design a filter with
  40 db attenuation in  the stop band and at most 3 db gain in the passband
  """ 
  N, Wn = signal.buttord(cutoff, cutoff+width, 1, 60)
  b, a = signal.butter(N, Wn)
  return signal.filtfilt(b, a, y)

def fir_filter(x,y,cutoff=0.0125,width=0.0125,**kwargs):
   numtaps, beta = signal.kaiserord(65, width)
   taps = signal.firwin(numtaps, cutoff, window=('kaiser', beta))
   return signal.filtfilt(taps, 1.0, y)

def moving_average_filter(x,y,width=10,window='hanning',**kwargs):
  return y

def median_filter(x,y,width=10,**kwargs):
  if width % 2 == 0:
    kernel_size = width+1 
  else:
    kernel_size = width
  return signal.medfilt(y,kernel_size=kernel_size)

def none_filter(x,y,**kwargs):
  return y

filter_types = {"gp": gp_filter,
                "median": median_filter,
                "butter": butterworth_filter,
                "fir": fir_filter,
                "ma": moving_average_filter,
                "none": none_filter
        };

def get_filter(name):
  if name.lower() not in filter_types:
    sys.exit("Warning: unknown filter type %s." % name.lower())
  return filter_types.get(name.lower(), none_filter)
                
def main():
    return

if __name__=="__main__":
    main()