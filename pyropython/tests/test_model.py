# -*- coding: utf-8 -*-
import os
import shutil
import numpy as np
from pyropython.config import _set_data_line_defaults
from pyropython.objective_functions import get_objective_function
"""This module tetsts the pyropython.model moduleself.

   For testing purposes we don't use FDS since this would require knowledge
   of the FDS installation. Instead, since this is a Python program, we use
   python and python script that outputs certain csv file
"""
template = """
import numpy as np

x = np.linspace(0, 1800)
y = {{10**logA1}}*np.exp(-(x-{{mu1}})**2/({{s1}}**2))+{{10**logA2}}*np.exp(-(x-{{mu2}})**2/({{s2}}**2))

f=open("output.csv","w")
f.write("s,-\\n")
f.write("Time,Y\\n")
for n,x in enumerate(x):
    f.write("%d,%.4f\\n" % (x,y[n]))
f.close()
"""

tol = 1e-3
tempdir = os.path.join(os.getcwd(), "testDir/")


class TestClass:

    def setUp(self):
        # create working directory
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        # correct answer
        x = np.linspace(0, 1800)
        y = (10000 * np.exp(-(x-500)**2 / (200**2)) +
             30000 * np.exp(-(x-1100)**2 / (300**2)))

        # parameters and bounds
        params = [("mu1", [0, 1000]),
                  ("mu2", [1000, 1800]),
                  ("s1", [0, 1000]),
                  ("s2", [0, 1000]),
                  ("logA1", [0, 6]),
                  ("logA2", [0, 6])]

        experiment = {"Y": (x, y)}
        simulation = {"Y": {"fname": "output.csv",
                            "dep_col_name": "Y"}}
        simulation["Y"] = _set_data_line_defaults(simulation["Y"])
        var_weights = {"Y": 1}
        data_weights = {"Y": np.ones_like(y)}
        objective_function = get_objective_function("mse")
        from pyropython.model import Model
        self.case = Model(exp_data=experiment,
                          params=params,
                          simulation=simulation,
                          var_weights=var_weights,
                          data_weights=data_weights,
                          templates=[("test.py", template)],
                          command="python",
                          tempdir=tempdir,
                          objective_function=objective_function
                          )

    def test_fitness(self):
        """ test model.fitness()
        """
        # test with the known right answer
        x = [500,  # mu1
             1100,  # mu2
             200,  # s1
             300,  # s2
             np.log10(10000),  # logA1
             np.log10(30000)]  # logA2

        res, pwd = self.case.fitness(x, return_directory=False)
        assert np.abs(res) < tol

    def test_optimization(self):
        from functools import partial
        from scipy.optimize import minimize

        f = partial(self.case.fitness, return_directory=False)

        bounds = []
        x0=[]
        for name, bound in self.case.params:
            bounds.append(bound)
            x0.append(np.mean(bound))

        res = minimize(f, x0, bounds=bounds)

        print(res.x)
        assert res.success

    def tearDown(self):
        if os.path.exists(tempdir):
                shutil.rmtree(tempdir, ignore_errors=True)
                pass
