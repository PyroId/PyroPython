.. pyropython documentation master file, created by
   sphinx-quickstart on Wed Jul 11 16:28:42 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyroPython -- Parameter estimation for FDS pyrolysis models written in python
==============================================================================

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

The PyroPython tool is released as open source software and is available from  https://github.com/PyroId/PyroPython.
The documentation can be found at http://pyroid.github.io/ .

Development of PyroPython was financed by state nuclear waste fund in the `SAFIR2018`_
programme and `NKS`_

.. _NKS: http://www.nks.org/
.. _SAFIR2018: http://safir2018.vtt.fi/

..

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    quickstart
    installation
    usage
    configuration
    templates
    plots
    filters
    examples


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
