# -*- coding: utf-8 -*-
import numpy as np


def make_initial_design(name="rand",
                        num_points=1,
                        bounds=None):
    """Make initial design of the given type with num_points points

    Args:
        name (:string) Type of initial design. Current choices are "rand" and
        "lhs"
        num_points (:int) Number of points to sample
        bounds (:list)  List of variable bounds. Note: number of dimensions
            is deduced from len(bounds)

    Returns:
        xhat (list): list of num_points parameter vectors
    """
    ndim = len(bounds)
    if name == "rand":
        xhat = _random(num_points, ndim)
    elif name == "lhs":
        xhat = _latin_hypercube(num_points, ndim)

    # scale variables
    for row in xhat:
        for n, point in enumerate(row):
            row[n] = bounds[n][0]+point*(bounds[n][1]-bounds[n][0])
    return xhat.tolist()


def _latin_hypercube(num_points=1, ndim=1):
    """
    Make a latin hypercube sample
    """
    from pyDOE import lhs
    return lhs(ndim,
               samples=num_points,
               criterion="maximin")


def _random(num_points=1, ndim=1):
    """
    Make a uniform random sample
    """
    return np.random.rand(num_points, ndim)
