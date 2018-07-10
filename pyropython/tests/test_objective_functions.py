import numpy as np
from pyropython.objective_functions import (
    get_objective_function,
    objective_functions
    )

tol = 1e-2


def test_standardized_moment():
    """
    Test calculation of the standardized moment based objective
        E[(sum_i ( w_i *abs(y_i-yhat_i) )^p]/std(w*y)^p
    Note that the absolute value of the differen is taken. This means that for
    odd values of p the expected result differs from the regular moment. Note
    also that the variance of experimental data should be nonzero
    The first four standardized moments for our case are:
        1. Mean Absolute Deviation
        2. 1
        3. related to skewness
        4. related to kurtosis
    """
    of = get_objective_function("standardized_moment")

    # test the four standardized moments
    n=1000000
    y = np.random.randn(n)
    x = np.zeros(n)
    w = np.ones(n)

    mom1 = of(y, x, w, p=1)
    mom2 = of(y, x, w, p=2)


    assert np.abs(mom1 -  np.sqrt(2/np.pi)) < tol
    assert np.abs(mom2 - 1) < tol


if __name__ == "__main__":
    test_standardized_moment()
