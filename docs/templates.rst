==============
Template files
==============

In additon to the configuration file, template file(s) are also needed.
These should be valid `Jinja2`_  templates that produce FDS files.

.. _Jinja2:  http://jinja.pocoo.org/docs/2.10/

The Variables that are to be optimized shall be replaced with {{variable name}}
(i.e. the variable name surrounded by double curly brackets). For example, it the
variables are defined in the yaml file as:

.. code-block:: yaml

    variables:
              VAR1: [ 0.1, 0.5]


The variable is entered into the template in the following manner::


    &MATL ID="ACME STUFF"
          DENSITY=100
          CONDUCTIVITY = {{VAR1}}
          SPECIFIC_HEAT=1


The input file is actually a Jinja2 template ([http://jinja.pocoo.org/]).
This allows one to create various constructs such as create ramps from parametrized
curves as follows

 config.yml:

.. code-block:: yaml

    variables:
              a: [ 0.1, 0.5]
              b: [ 0.1, 0.5]


template.fds::

    {% for number in range(0,600,100) %}
      &RAMP ID="CP" , T={{number}} F={{a*number**2+b}}/
    {% endfor %}


The for loop above  generates a RAMP from 0 to 600 with step size 100 using
ramp values calculated from second degree polynomial with parameters a and b.
For example, with parameters a=0.01 and b=2 the ramp resulting file will contain::


        &RAMP ID="CP" , T=0 F=2.0/
        &RAMP ID="CP" , T=100 F=102.0/
        &RAMP ID="CP" , T=200 F=402.0/
        &RAMP ID="CP" , T=300 F=902.0/
        &RAMP ID="CP" , T=400 F=1602.0/
        &RAMP ID="CP" , T=500 F=2502.0/


The jinja2 templates can also contain logic blocks etc. Read more form `Jinja2`_
documentation. And see the `examples <https://github.com/PyroId/PyroPython/tree/master/examples>`_ directory for examples.
