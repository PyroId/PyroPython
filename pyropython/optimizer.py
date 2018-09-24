# -*- coding: utf-8 -*-
import numpy as np
from functools import partial
from pyropython.initial_design import make_initial_design
from multiprocessing import Manager,Queue,Lock
from multiprocessing.managers import BaseManager
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
                 lock=None,
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
        self.lock = Lock()
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

    def __call__(self, *args,**kwargs):
        """When called, cnsume the. queue, print and log iteration.

          This allows one to pass the Logger class as a callback function to
          optimization functuions.
        """
        with self.lock:
            self.consume_queue()
            self.print_iteration()
            self.log_iteration()

    def callback(self, *args,**kwargs):
        """When called, cnsume the. queue, print and log iteration.

          This allows one to pass the Logger class as a callback function to
          optimization functuions.
        """
        with self.lock:
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
        """ write iteration info to log file """
        N = self.Fevals[-1]
        xi = np.array(self.Xi[-1])
        fi = np.array(self.Fi[-1])
        ind = fi.argsort()[::-1]
        fi = fi[ind]
        xi = xi[ind]

        for n in range(0, N):
            line = (["%d" % (self.iter)] + ["%.3f" % v for v in xi[n]] +
                    ["%3f" % fi[n], "%3f" % self.f_best] +
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
    print()
    print("Begin bayesian optimization.")
    print("="*20)
    print("Base estimator:")
    print()
    print(optimizer.base_estimator_)
    print()
    print("Acquisition function: %s" % optimizer.acq_func)
    print("Acquisition function kwargs:")
    print(optimizer.acq_func_kwargs)
    print("Acquisition function optimizer kwargs:")
    print(optimizer.acq_optimizer_kwargs)
    print("Maximum iterations: %d " % runopts.max_iter)
    print("Points per iteration: %d " % runopts.num_points)
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

    class MyManager(BaseManager): pass

    def Manager():
        m = MyManager()
        m.start()
        return m 

    x = make_initial_design(name=runopts.initial_design,
                            num_points=runopts.num_initial,
                            bounds=case.get_bounds())

    N_iter = 0
    # Make a proxy class in order to share the Logger between Processes
    # This is ugly , but I _really_ want to use the Logger class as callback
    # this can only be done if the Logger class is shared between processes
    MyManager.register("Logger",Logger)
    MyManager.register("Lock",Lock)
    MyManager.register("Queue",Queue)
    m= Manager()
    lock = m.Lock()
    queue = m.Queue()
    log = m.Logger(params=case.params,
                queue=queue,
                lock=lock,
                logfile=runopts.logfilename,
                best_dir = runopts.output_dir) 
    fun = partial(case.penalized_fitness, queue=queue)
    print("Evaluating {num:d} random points.".format(num=len(x)),
                  flush=True)
    y = list(executor.map(fun, x))
    indices = np.argsort(y)
    candidates = [x[i] for i in indices]
    if len(candidates) < runopts.max_iter*runopts.num_points :
        N = runopts.max_iter*runopts.num_points - len(candidates) 
        x_new = make_initial_design(name="rand",
                                    num_points=N,
                                    bounds=case.get_bounds())
        candidates.extend(x_new)
    cur = 0
    try:
        while N_iter < runopts.max_iter:
            # evaluate points (in parallel)
            x_eval = candidates[cur:cur+runopts.num_points]
            cur = cur + runopts.num_points
            task = partial(minimize, fun,
                           method="Nelder-Mead",
                           callback = log.callback,
                           options={'ftol': 0.001,
                                    'adaptive': True})
            print("Minimizing {num:d} starting points.".format(num=len(x)),
                  flush=True)
            y = list(executor.map(task, x))
            msg = "Used {N:d} function evaluations. "
            print(msg.format(N=len(log.Fi[-1])))

            N_iter += 1
        return log.x_best, log.f_best, log.Xi, log.Fi
    finally:
            log()

        

def differential_evolution(case, runopts, executor):
    """ optimize case using monte carlo sampling
    """
    files = Manager().Queue()
    fun = partial(case.fitness, queue=files)
    N_iter = 0
    print("Begin differential evolution")
    print("NOTE: parallel evaluation not currently supported. Maybe in future scipy")
    from scipy.optimize import differential_evolution as de
    with Logger(params=case.params,
                queue=files,
                logfile=runopts.logfilename,
                best_dir = runopts.output_dir) as log:
            y = de(fun,bounds=case.get_bounds(),
                   max_iter = runopts.max_iter,
                   callback = log.callback)

    return log.x_best, log.f_best, log.Xi, log.Fi

optimizers = {"skopt": skopt,
              "multistart": multistart,
              "dummy": dummy,
              "de": differential_evolution}


def get_optimizer(name="skopt"):
    return optimizers.get(name, skopt)
