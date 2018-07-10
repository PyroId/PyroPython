# -*- coding: utf-8 -*-
from pyropython.utils import read_data
from pyropython.config import _set_data_line_defaults
import numpy as np
import os

tempdir = os.path.join(os.getcwd(), "testDir")

def test_read_data():
    """ Test reading data and gradient calculation
        This function generates a csv file to test reading datafiles
        and various filtersself.
    """
    # generate data and save to a tempfile
    Time = np.linspace(0, 1800, num=1800)
    AltTime = Time
    y2 = 0.5 - 0.5 * np.tanh((Time-600)/100)  # TGA result
    y = y2/y2[0]
    dy = 0.005-0.005 * np.tanh(Time/100 - 6)**2   # exact derivative of former
    ny = y + 0.1*np.random.randn(len(Time))  # noisy
    outdata = np.stack((Time, AltTime, y, dy, y2, ny), axis=1)
    # delete=False is needed so that the tempfile can be written to in  windows
    # create working directory
    fp = open("output.csv",mode="w+t")
    # delete=False so we can close() the file and delete later

    np.savetxt(fp.name, outdata,
               delimiter=",",
               header="Time,AltTime,y,dy,y2,ny",
               comments='')
    fp.close()
    fname = "output.csv"
    # line with only the required fields
    line = {"fname": fname,
            "dep_col_name": "y"}
    # populate rest of the fields
    line = _set_data_line_defaults(line, header=0)
    read_Time, read_y = read_data(**line)

    # Test normalization, gradient calculation and ind_col_name functionality
    line['normalize'] = True
    line['dep_col_name'] = 'y2'
    read_Time, norm_y2 = read_data(**line)

    # Test normalization, gradient calculation and ind_col_name functionality
    line['gradient'] = True
    line['normalize'] = True
    line['ind_col_name'] = 'AltTime'
    line['dep_col_name'] = 'y2'
    read_AltTime, calc_dy = read_data(**line)

    # delete file now that we don't need it anymore
    os.remove(fname)

    assert np.allclose(read_y, y)
    assert np.allclose(norm_y2, y)
    assert np.allclose(read_Time, Time)
    assert np.allclose(read_Time, read_AltTime)
    # rtol = 1e-5 fails
    assert np.allclose(dy, calc_dy, rtol=1e-4)
