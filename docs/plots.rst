.. _Plotting:


========
Plotting
========

Pyropython contains a rudimentary plotting tool to quickly inspect the
experimental data, simulation results and goodness of fit. After runniong pyropython.
You can plot the figures defined in the configuration file by typing

::

    plot_pyro config.yml

at the command line. The plots are defined in the **config.yml** file under the **plots** keyword.


.. code-block:: yaml

    plots:
        plotname: {variables:
                   labels:
                   type:
                   ylabel:
                   xlabel:
                  }

                   
.. py:data:: plots  :noindex:

.. py:attribute:: plotname

            Name of the plotfile. This willcreate a file named "plotname.pdf" in
            Figs/ or CASENAME_Figs/.

            .. py:attribute:: variables  

                    Variables to be plotted. The variable names are the same as
                    those listed under *simulation* and *experiment* keywords
                    :noindex:

            .. py:attribute:: labels

                    LAbels for the legend of the plot. For comparison plots,
                    the labels will be appended with "exp" and "sim" for
                    experimental data and simulation results, respectively

            .. py:attribute:: type

                    Type of plot. Choices are "comparison", "simulation" and
                    "experimental". Comparison plots a comparison of
                    the simulation results in Best/ (or CASENAME/) folder with
                    experimental data. PLot type "simulation" plots only the
                    simulation data. This is useful for checking gradient
                    calculation etc. Plot type "experimental" plots the raw
                    experimental data together with the filtered version. Useful
                    for checking filtering ad other  transformations.

            .. py:attribute:: xlabel

                    Label for the x-axis of the plot.

            .. py:attribute:: ylabel

                    Label for the y-axis of the plot.
