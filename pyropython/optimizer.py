import numpy as np
from functools import partial
import sklearn.ensemble as skl
from distutils.dir_util import copy_tree
from shutil import rmtree
from initial_design import make_initial_design

class Logger:
    """
    Class for recording optimization algorithm progress.
    """

    def __init__(self,
                 params=None,
                 logfile="log.csv"):
        self.x_best = None
        self.f_best = None
        self.xi = None
        self.fi = None
        self.iter = 0
        self.logfile = open(logfile, "w")
        self.points = []
        self.params = params

        # write header to logfile before  first iteration
        header = ",".join(["Iteration"] +
                          [name for name, bounds in self.params] +
                          ["Objective", "Best Objective"])
        self.logfile.write(header+"\n")

    def __enter__(self):
        return self

    def __exit__(self):
        self.logfile.close()

    def __call__(self, x, f, **args):
        """
        This function call signature matches most scipy.optimize callbacks
        """
        self.update(x, f)
        self.print_iteration()
        self.log_iteration()

    def update(self, x, f):
        self.points.append((x, f))
        f_ = list(f)
        x_ = list(x)

        ind = np.argmin(f_)
        self.fi = f_[ind]
        self.xi = x_[ind]

        if self.f_best:
            if self.f_best > self.fi:
                self.f_best = self.fi
                self.x_best = self.xi
        else:
            self.f_best = self.fi
            self.x_best = self.xi
        self.iter += 1

    def print_iteration(self):
        """ prints the solution from current iteration """
        # Print info
        msg = """
                best objective from this iteration:  {cur:.3E}
                best objective found thus far:       {bst:.3E}
                best model:
          """
        print(msg.format(cur=self.fi, bst=self.f_best))
        msg = "       {name} :"
        for n, (name, bounds) in enumerate(self.params):
            print(msg.format(name=name), self.x_best[n])
        print()

    def log_iteration(self):
        """ write iteration info to log file """
        line = (["%d" % (self.iter)] + ["%.3f" % v for v in self.xi] +
                ["%3f" % self.fi, "%3f" % self.f_best])
        self.logfile.write(",".join(line)+"\n")
        pass


def skopt(case, runopts, executor):
    """ optimize case using scikit-optimize
    """
    from skopt import Optimizer
    optimizer = Optimizer(dimensions=case.get_bounds(),
                          **runopts.optimizer_opts)

    x = make_initial_design(name=runopts.initial_design,
                            num_points=runopts.num_initial,
                            bounds=case.get_bounds())
    N_iter = 1
    with  Logger(params=case.params) as log:
        while N_iter<runopts.maxiter:
            # evaluate points (in parallel)
            out = list(executor.map(case.fitness, x))
            y, pwd = zip(*out)
            log(x, y)
            optimizer.tell(x ,y)
            x = optimizer.ask(runopts.num_points)
            N_iter += 1
        return log.x_best, log.f_best, log.points

def penalty_function(x,bounds=[]):
    """
    Implement optimization constraints by penalty function method.
    """
    res = 0
    for n, (minval, maxval) in enumerate(bounds):
        res += 100 * min(0, x[n]-minval)**2 + 100 * max(0, x[n]-maxval)**2

    return res


def basin_hopping(case, runopts, **args):
    """ optimize case using scipy optimize basin hopping algorithm
    """
    from scipy.optimize import basinhopping

    x = make_initial_design(name=runopts.initial_design,
                            num_points=1,
                            bounds=case.get_bounds())

    # Augument case.fitness with penalty function, don't return directory
    def fun(x):
        return (case.fitness(x, return_directory=False) +
                penalty_function(x, case.get_bounds()))

    with Logger(params=case.params) as log:

        opt = basinhopping(fun, x,
                           niter=runopts.max_iter,
                           callback=log)

        return log.x_best, log.f_best, log.points


def multistart(case, runopts, executor):
    """ optimize case using multiple random starts
    """
    x = make_initial_design(name=runopts.initial_design,
                            num_points=runopts.num_initial,
                            bounds=case.get_bounds())

    def fun(x):
        return case.fitness(x) + penalty_function(x,case.get_bounds())

    log = Logger(params=case.params)

    return log.x_best, log.f_best, log.points


optimizers = {"skopt": skopt,
              "basin_hopping": basin_hopping,
              "multistart": multistart}


def get_optimizer(name="skopt"):
    return optimizers.get(name, skopt)
