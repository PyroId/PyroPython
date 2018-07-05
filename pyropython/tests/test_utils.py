# -*- coding: utf-8 -*-

from pyropython.utils import read_data
from pyropython.config import _set_data_line_defaults
import numpy as np
import tempfile
import os


def test_read_data():
    """ Test reading data, filtering data and gradient calculation
        This function generates a csv file to test reading datafiles
        and various filtersself.
    """
    # generate data and save to a tempfile
    Time = np.linspace(0, 1800)
    AltTime = Time
    y = 0.5-0.5*np.tanh((Time-600)/100)  # TGA result
    dy = -0.05/np.cosh(6-Time/100)**2  # exact derivative of former
    ny = y + 0.1*np.random.randn(len(Time))  # noisy
    outdata = np.stack((Time, AltTime, y, dy, ny), axis=1)
    fp = tempfile.NamedTemporaryFile(mode="w+t", delete=False)
    np.savetxt(fp.name, outdata,
               delimiter=",",
               header="Time,AltTime,y,dy,ny",
               comments='')
    fp.close()
    fname = fp.name
    lines= open(fname,"rt").readlines()
    # line with only the required fields
    line = {"fname": fname,
            "dep_col_name": "y"}
    line = _set_data_line_defaults(line,header=0)
    # Now lets get ready to read it
    read_Time, read_y = read_data(**line)
    #
    assert np.allclose(read_y, y)
    assert np.allclose(read_Time, Time)
    os.remove(fname)
