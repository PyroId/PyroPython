import os
from .filter import * 
from pandas import read_csv
from numpy import array,mean
from numpy import gradient as np_gradient 

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

#reads (and filters) a column from csv file
def read_data(fname=None,            
              dep_col_name=None,      
              ind_col_name=None,      
              conversion_factor=1.0, 
              normalize=False,         
              filter_type="None",       
              filter_opts=None,
              gradient=False,
              header=1,
              cwd="./"):
        tmp=read_csv(os.path.join(cwd,fname),header=header,
                    encoding = "latin-1",
                    index_col=False,
                    comment="#",
                    error_bad_lines=False,
                    warn_bad_lines=True,
                    skip_blank_lines=True)
        # Remove trailing units from column headers
        tmp.columns = [colname.split('(')[0].strip() for colname in tmp.columns]
        tmp=tmp.dropna(axis=1,how='any')
        filter = filter_types.get(filter_type, none_filter)
        x=array(tmp[ind_col_name])
        y=array(tmp[dep_col_name])
        y = filter(x,y)
        if normalize:
          y = y/y[0] #assume TGA
        if gradient:
          y = -1.0*np_gradient(y)/np_gradient(x)
        return x,y*conversion_factor

def main():
    return

if __name__=="__main__":
    main()
