import os
from pyropython.filter import get_filter
from pandas import read_csv
from numpy import array,genfromtxt
from numpy import gradient as np_gradient
import numpy as np


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def read_initial_design(filename,param_names):
    """Read initial design from a csv file.
    
    This function takes a csv file that has a column for eatch param_name.
    For example, you can rea in the log.csv output by a previous optimization 
    and continue from where you left off
    This is especially useful for continuing optimization were you left off.
    
    Args:
      filename` [string or `pathlib.Path`]:
          The path of the file from which to load the initial design.
      param_names` [string or `pathlib.Path`]:
          The path of the file from which to load the initial design.

    Returns
      Xi ['list']: list of points whwre function was evaluated
      yi ['list']: list of objective values
    """
    tmp = genfromtxt(filename,delimiter=",",names=True)
    yi =tmp['Objective']
    # extract columns containing param_names
    ind = [ tmp.dtype.names.index(pname) for pname in param_names]
    Xi = array(tmp.tolist())
    Xi = Xi[:,ind]
    # reorder columns
    return Xi.tolist(),list(yi)
    

def read_data(fname=None,
              dep_col_name=None,
              ind_col_name=None,
              conversion_factor=1.0,
              normalize=False,
              filter_type="None",
              filter_opts={},
              gradient=False,
              header=1,
              cwd="./"):
    """
    This function reads a csv datafile and applies filters. 

    Args:
        fname (:string): Filename,
        dep_col_name (:string): Name of the dependent variable column
        ind_col_name (:string): Name of the indepedent variable column
        conversion_factor (:float): Number used to  scale the dependent 
          variable, i.e  yconv = y*conversion_factor
        normalize (:boolean):  If True, the dependent variable will be normalized
          by its first value, i.e ynorm = y/y[0], where y i s the dependent variable
        filter_type (:string): filter to be applied to the dependent variable. See 
          pyropython.filter.filter_type for available filters
        filter_opts (:dict): dictionary of options to be passed to the filter
        gradient (:boolean): If true, the gradient of the dependent variable is returned.
          The gradient is calculated in relation to the independent variable.
        header (:int): How many header lines before the line containing the column names.
        cwd (:string): Working directory (default "./")
    Returns:
            data (:dict): Dictionary, with entries key: (T,F) where "key" is a
                key from the simulation dict, T is the indpendent variable
                and F is the dependent variable
            pwd (:string): Working directory, where the simulation was run.
    """
    tmp = read_csv(os.path.join(cwd, fname),
                   header=header,
                   encoding="latin-1",
                   index_col=False,
                   comment="#",
                   error_bad_lines=False,
                   warn_bad_lines=True,
                   skip_blank_lines=True,
                   na_values="NaN")
    # Remove trailing units from column headers
    tmp.columns = [colname.split('(')[0].strip() for colname in tmp.columns]
    tmp = tmp.dropna(axis=1, how='any')
    filter = get_filter(filter_type)
    try:
        x = array(tmp[ind_col_name])
        y = array(tmp[dep_col_name])
    except KeyError as KeyErr:
        msg = ("Column named '%s' in file '%s' not found." % (KeyErr, fname) +
               "Column names: \n %s" % (','.join(tmp.columns.values)))
        raise KeyError(msg)

    y = filter(x, y, **filter_opts)
    if normalize:
        y = y/y[0]  # assume TGA
    if gradient:
        y = -1.0*np_gradient(y)/np_gradient(x)
    try:
        y = y*conversion_factor
    except TypeError:
        y = np.array([np.float(s.strip()) for s in y])
        print(y)
    return x, y


def main():
    return


if __name__ == "__main__":
    main()
