import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from pandas import read_csv
from scipy import signal
from sklearn.gaussian_process import GaussianProcessRegressor


#!python
def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    from math import factorial

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError as msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

dat=read_csv("09090043_red.CSV",header=1,encoding = "latin-1",index_col=False)
dat.columns = [colname.split('(')[0].strip() for colname in dat.columns]
etime = dat["Time"]

gp=GaussianProcessRegressor()

A=0.01**2 # cm2 => m2
emlr =  dat["Specific MLR"] # g/m2/s -> kg/m2/s
samp_rate=1
cuttoff_freq = 1.0/40.0
norm_pass = cuttoff_freq/(samp_rate/2)
norm_stop = 1.5*norm_pass
(N, Wn) = signal.buttord(wp=norm_pass, ws=norm_stop, gpass=2, gstop=30, analog=0)
(b, a) = signal.butter(N, Wn, btype='low', analog=0, output='ba')
print(Wn)
#b, a = signal.butter(8, 0.125) # Nyquist = 2 seconds =0.5 Hz = 1 20 seconds = 0.05
emlrbar = signal.filtfilt(b, a, emlr, method="gust")
emlrbar2 = savitzky_golay(np.array(emlr), window_size=61, order=3)
sim_dat = np.genfromtxt("Temp/cone_hrr.csv",delimiter=",",skip_header=1,names=True)
stime = sim_dat["Time"]
smlr = sim_dat["MLR_TOTAL"]*100000

fig,ax = plt.subplots()
plt.plot(etime,emlr,label="exp")
plt.plot(etime,emlrbar,label="exp (filt)")
plt.plot(etime,emlrbar2,label="exp (golay)")
plt.plot(stime,smlr,label="sim")
plt.xlabel("Time(s)")
plt.ylabel("MLR (g/m2/s)")
ymin,ymax = ax.get_ylim()
ax.set_ylim(0,ymax)
plt.legend()
ax.grid(True)

plt.savefig("comp.png",bbox_inches="tight")
