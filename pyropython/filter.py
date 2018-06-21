# -*- coding: utf-8 -*-


"""pyropython.filter: Data filtering functions for smoothing experimental data"""

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern,WhiteKernel,ConstantKernel
import numpy as np
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
  gp.fit(x[:,np.newaxis],y[:,np.newaxis])
  return np.squeeze(gp.predict(x[:,np.newaxis]))

def butterworth_filter(x,y,cutoff=0.0125,width=0.0125,**kwargs):
  """
  Applies a butterworth filter with given cutoff and passband width
  The Scipy 'buttord' and butter filters are used to design a filter with
  40 db attenuation in  the stop band and at most 3 db gain in the passband

  input:
        x: time  (ignored)
        y: the input signal
        cutoff: passband edge frequency
        width: width off passband
    output:
        the smoothed signal

  Note that *cutoff* and *width* are normalized from 0 to 1,
  where 1 is the Nyquist frequency, pi radians/sample.

  """
  N, Wn = signal.buttord(cutoff, cutoff+width, 1, 60)
  b, a = signal.butter(N, Wn)
  return signal.filtfilt(b, a, y,method="gus") # zero phase filtering

def fir_filter(x,y,cutoff=0.0125,width=0.0125,**kwargs):
   numtaps, beta = signal.kaiserord(65, width)
   taps = signal.firwin(numtaps, cutoff, window=('kaiser', beta))
   return signal.filtfilt(taps, 1.0, y) # zero phase filtering

def moving_average_filter(x,y,width=11,window='hanning',**kwargs):
  """
  Copied from scipy cookbook (http://scipy-cookbook.readthedocs.io/items/SignalSmooth.html)
  Smooth signal by convolving with a window function.

  input:
        x: time  (ignored)
        y: the input signal
        width: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.
    output:
        the smoothed signal
  """

  if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
      raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

  if window == 'flat': #moving average
      w=np.ones(width,'d')
  else:
      w=eval('np.'+window+'(width)')
  y=np.convolve(w/w.sum(),y,mode='same')
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
