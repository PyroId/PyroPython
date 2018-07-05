from pyropython.filter import filter_types
import numpy as np
import matplotlib.pyplot as plt


def test_filters():
    """ Test filtering of data
        This function loops over the filter_types dictinionary
        defined in filter.py and applies each filter to a noisy signal
    """
    Time = np.linspace(0, 1800, num=1800)
    y = 50 - 50 * np.tanh((Time-600)/100) + 5*np.sin(Time/40)
    ny = y + 5*np.random.randn(len(Time))

    result = {}
    for name,filt in filter_types.items():
        if name is not 'none':
            ybar = filt(Time,ny)
            result[name]=ybar
    # see if the filtered data is close to original. The tolerances are made up
    # almost ceertainly we could use toghter tolerances
    for name in result:
        assert np.allclose(result[name],y,atol=10)
