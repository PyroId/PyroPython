=======================
Plotting with plot_pyro
=======================
Pyropython contains a rudimentary plotting tool to quickly inspect the
experimental data, simulation results and goodness of fit. If you installed
the package using **pip**, you can get the plots by typing

::

    plot_pyro config.yml

The plots are defined in the **config.yml** file under the **plots** keyword.


.. code-block:: yaml

    plots:
        plotname: {variables:
                   labels:
                   type:
                   ylabel:
                   xlabel:
                  }

.. py:module:: plots

.. py:data:: plotname

            Name of the plotfile. This willcreate a file named "plotname.pdf" in
            Figs/ or CASENAME_Figs/.

            .. py:data:: variables

                    Variables to be plotted. The variable names are the same as
                    those listed under *simulation* and *experiment* keywords

            .. py:data:: labels

                    LAbels for the legend of the plot. For comparison plots,
                    the labels will be appended with "exp" and "sim" for
                    experimental data and simulation results, respectively

            .. py:data:: type

                    Type of plot. Choices are "comparison", "simulation" and
                    "experimental". Comparison plots a comparison of
                    the simulation results in Best/ (or CASENAME/) folder with
                    experimental data. PLot type "simulation" plots only the
                    simulation data. This is useful for checking gradient
                    calculation etc. Plot type "experimental" plots the raw
                    experimental data together with the filtered version. Useful
                    for checking filtering ad other  transformations.

            .. py:data:: xlabel

                    Label for the x-axis of the plot.

            .. py:data:: ylabel

                    Label for the y-axis of the plot.
