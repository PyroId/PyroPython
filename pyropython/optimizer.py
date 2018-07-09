import numpy as np

def skopt(case, runopts, executor):
    pass


def basin_hopping(case, runopts, executor):
    pass


def multistart(case, runopts, executor):
    pass


def bfgs(case, runopts, executor):
    pass


optimizers = {"skopt": skopt,
              "basin_hopping": basin_hopping,
              "multistart": multistart,
              "bfgs": bfgs}


def get_optimizer(name="skopt"):
    return optimizers.get(name, skopt)
