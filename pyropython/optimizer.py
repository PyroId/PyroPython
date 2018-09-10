# -*- coding: utf-8 -*-
import numpy as np
from functools import partial
from pyropython.initial_design import make_initial_design
from multiprocessing import Manager
from shutil import rmtree, copytree
from traceback import print_exception


class Logger:
    """
    Class for recording optimization algorithm progress.

    This class is supposed to consume the queue created by model.fitness()
    """

    def __init__(self,
                 params=None,
                 logfile="log.csv",
                 evalfile="evals_log.csv",
                 queue=None,
                 best_dir="Best/"):
        self.x_best = None
        self.f_best = None
        self.xi = None
        self.fi = None
        self.iter = 0
        self.logfile = logfile
        self.Xi = []
        self.Fi = []
        self.Fevals = []
        self.params = params
        self.queue = queue
        self.best_dir = best_dir

        logfile = open(self.logfile, 'w+')
        # write header to logfile before  first iteration
        header = ",".join(["Iteration"] +
                          [name for name, bounds in self.params] +
                          ["Objective", "Best Objective", "Fevals"])
        logfile.write(header+"\n")
        logfile.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.consume_queue()
        if exc_type is not None:
            print_exception(exc_type, exc_value, tb)

    def __call__(self, **args):
        """When called, cnsume the. queue, print and log iteration.

          This allows one to pass the Logger class as a callback function to
          optimization functuions.
        """
        self.consume_queue()
        self.print_iteration()
        self.log_iteration()

    def consume_queue(self, queue=None):
        """ Consume items in the queue.
        """
        if not queue:
            queue = self.queue
        f_ = []
        x_ = []
        while not queue.empty():
            fi, xi, pwd = queue.get()
            f_.append(fi)
            x_.append(xi)
            # record best value seen
            if self.f_best:
                if self.f_best > fi:
                    self.f_best = fi
                    self.x_best = xi
            else:
                self.f_best = fi
                self.x_best = xi
            # save output of the best run
            if fi <= self.f_best:
                rmtree(self.best_dir)
                copytree(pwd, self.best_dir)
            # delete files when done
            rmtree(pwd)

        # record the best form this iteration
        self.iter += 1
        self.Fevals.append(len(f_))
        if len(f_) > 0:
            ind = np.argmin(f_)
            self.fi = f_[ind]
            self.xi = x_[ind]
            self.Xi.append(x_)
            self.Fi.append(f_)

    def print_iteration(self):
        """ prints the solution from current iteration """
        # Print info
        msg = """
            Iteration: {it:d}
                best objective from this iteration:  {cur:.3E}
                best objective found thus far:       {bst:.3E}
                best model:
              """
        print(msg.format(it=self.iter, cur=self.fi, bst=self.f_best))
        msg = "       {name} :"
        for n, (name, bounds) in enumerate(self.params):
            print(msg.format(name=name), self.x_best[n])
        print(flush=True)

    def log_iteration(self):
        """ write iteration info to log file

            'iteration' in this context refers to what was read from the queue
            last time that consume_queue was called.
        """
        logfile = open(self.logfile, 'a+')
        xi = self.Xi[-1]
        fi = np.array(self.Fi[-1])
        ind = fi.argsort()[::-1]
        for i in ind:
            line = (["%d" % (self.iter)] + ["%.3f" % v for v in xi[i]] +
                    ["%3f" % fi[i], "%3f" % self.f_best] +
                    ["%d" % self.Fevals[-1]])
            logfile.write(",".join(line)+"\n")
        logfile.close()
        pass


def dummy(case, runopts, executor):
    """ optimize case using monte carlo sampling
    """
    files = Manager().Queue()
    fun = partial(case.fitness, queue=files)
    x = make_initial_design(name=runopts.initial_design,
                            num_points=runopts.num_initial,
                            bounds=case.get_bounds())
    N_iter = 0
    print("Begin random optimization.")
    with Logger(params=case.params,
                queue=files,
                logfile=runopts.logfilename,
                best_dir = runopts.output_dir) as log:
        while N_iter < runopts.max_iter:
            # evaluate points (in parallel)
            print("Evaluating {num:d} points.".format(num=len(x)),
                  flush=True)
            y = list(executor.map(fun, x))
            log()
            if N_iter < runopts.max_iter:
                x = make_initial_design(name="rand",
                                        num_points=runopts.num_points,
                                        bounds=case.get_bounds())
            N_iter += 1
        return log.x_best, log.f_best, log.Xi, log.Fi


def skopt(case, runopts, executor):
    """ optimize case using scikit-optimize
    """
    from skopt import Optimizer
    optimizer = Optimizer(dimensions=case.get_bounds(),
                          **runopts.optimizer_opts)
    files = Manager().Queue()
    fun = partial(case.fitness, queue=files)
    x = make_initial_design(name=runopts.initial_design,
                            num_points=runopts.num_initial,
                            bounds=case.get_bounds())
    N_iter = 0
    print("Begin bayesian optimization.")
    with Logger(params=case.params,
                queue=files,
                logfile=runopts.logfilename,
                best_dir = runopts.output_dir) as log:
        while N_iter < runopts.max_iter:
            # evaluate points (in parallel)
            print("Evaluating {num:d} points.".format(num=len(x)))
            y = list(executor.map(fun, x))
            log()
            print("Updating metamodel and asking for points",flush=True)
            optimizer.tell(x, y)
            if N_iter < runopts.max_iter:
                x = optimizer.ask(runopts.num_points)
            N_iter += 1
        return log.x_best, log.f_best, log.Xi, log.Fi


def multistart(case, runopts, executor):
    """ optimize case using multiple random starts and scipy.minimize
    """
    from scipy.optimize import minimize
    x = make_initial_design(name=runopts.initial_design,
                            num_points=runopts.num_initial,
                            bounds=case.get_bounds())

    N_iter = 0
    queue = Manager().Queue()
    fun = partial(case.penalized_fitness, queue=queue)
    with Logger(params=case.params,
                queue=queue,
                logfile=runopts.logfilename,
                best_dir = runopts.output_dir) as log:
        while N_iter < runopts.max_iter:
            # evaluate points (in parallel)
            task = partial(minimize, fun,
                           method="powell",
                           options={'ftol': 0.001})
            print("Minimizing {num:d} starting points.".format(num=len(x)),
                  flush=True)
            y = list(executor.map(task, x))
            log()
            msg = "Used {N:d} function evaluations. "
            print(msg.format(N=len(log.Fi[-1])))
            if N_iter < runopts.max_iter:
                x = make_initial_design(name="rand",
                                        num_points=runopts.num_points,
                                        bounds=case.get_bounds())
            N_iter += 1
        return log.x_best, log.f_best, log.Xi, log.Fi


optimizers = {"skopt": skopt,
              "multistart": multistart,
              "dummy": dummy}


def get_optimizer(name="skopt"):
    return optimizers.get(name, skopt)
