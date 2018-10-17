============
Introduction
============

Pyropython is a python library and set of command-line tools.  The motivation for creating this tool has
been to support the Fire Modeling efforts at `VTT Technical Research Centre of Finland`_. These tools are
best suited for identification of pyrolysis parameters for the Fire Dynamics Simulator (`FDS`_).

.. _FDS: https://pages.nist.gov/fds-smv/

Despite this background, the python library and commandline tools  can be used to identify
parameters for any simulator that outputs data in csv format  with text headers.

.. _VTT Technical Research Centre of Finland: https://www.vtt.fi/

Pyropython is a wrapper around existing optimizatioon libraries and is written in
a fashion that allows easy addition of new algorithms. Currently supported algorithms
are:
    1. Random sampling
    2. Nelder-Mead simplex (from `scipy`_)
    3. Differential evolution (also from `scipy`)
    4. Bayesian Optimization (using `scikit-optimize`)

.. _scipy: https://www.scipy.org/
.. _scikit-optimize: https://scikit-optimize.github.io/
