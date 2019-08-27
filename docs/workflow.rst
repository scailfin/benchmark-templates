==================
Workflow Templates
==================


**Workflow Templates** are parameterized workflow specifications for the *Reproducible Open Benchmarks for Data Analysis Platform (ROB)*. Workflow templates are motivated by the goal to allow users to run pre-defined data analytics workflows while providing their own input data, parameters, as well as their own code modules. Workflow templates are inspired by, but not limited to, workflow specifications for the `Reproducible Research Data Analysis Platform (REANA)`.



Motivation for Parameterized Workflow Templates
===============================================

Consider the `REANA Hello World Demo <https://github.com/reanahub/reana-demo-helloworld>`_. The demo workflow takes as input a file ``data/names.txt`` containing a list of person names and a timeout parameter ``sleeptime``. For each line in ``data/names.txt`` the workflow writes a line "Hello *name*!" to an output file ``results/greetings.txt``. For each line that is written to the output file program execution is delayed by a number of seconds defined by the `sleeptime` parameter.

Workflow specifications in REANA are serialized in YAML or JSON format. The names of the input and output files as well as the value for the sleep period are currently hard-coded in the workflow specification file ( e.g.  `reana.yaml <https://raw.githubusercontent.com/reanahub/reana-demo-helloworld/master/reana.yaml>`_ ).

.. code-block:: yaml

    inputs:
      files:
        - code/helloworld.py
        - data/names.txt
      parameters:
        helloworld: code/helloworld.py
        inputfile: data/names.txt
        outputfile: results/greetings.txt
        sleeptime: 0
    workflow:
      type: serial
      specification:
        steps:
          - environment: 'python:2.7'
            commands:
              - python "${helloworld}"
                  --inputfile "${inputfile}"
                  --outputfile "${outputfile}"
                  --sleeptime ${sleeptime}
    outputs:
      files:
       - results/greetings.txt

Assume we want to build a system that allows users to run the Hello world demo via a (web-based) interface where they provide a text file with person names and a sleep period value. There are three main parts to such a system. First, we need to display a form where the user can select (upload) a text file and enter a sleep time value. Second, after the user submits their input data, we need to create an update version of the workflow specification as shown above where we replace the value of ``inputfile`` and ``sleeptime`` with the user-provided values. We then pass the modified workflow specification to a REANA instance for execution. There are several way for implementing such a system. Parameterized workflow templates are part of one possible solution.



What are Parameterized Workflow Templates?
==========================================

Similar to REANA workflow specifications, parameterized workflow templates are serialized in YAML or JSON format. Each template has two main elements: ``workflow`` and ``parameters``. The ``workflow`` element is mandatory and the ``parameters`` element is optional.

The ``workflow`` element contains the workflow specification. The structure and syntax of this specification is dependent on the backend (engine) that is used to execute workflows. The workflow engine is for example specified as part of the configuration for the `Reproducible Benchmark Engine <https://github.com/scailfin/benchmark-engine>`_. If the benchmark engine uses the `REANA Workflow Engine <https://github.com/scailfin/benchmark-reana-backend>`_ for example, the workflow specification is expected to follow the the common syntax for REANA workflow specifications.

The ``parameters`` section defines those parts of a workflow that are variable with respect to user inputs. We refer to these are *template parameters*. Template parameters can for example be used to define input and output values for workflow steps or identify Docker container images that contain the code for individual workflow steps. The detailed parameter declarations are intended to be used by front-end tools to render forms that collect user input.

An example template for the **Hello World example** is shown below.

.. code-block:: yaml

    workflow:
        inputs:
          files:
            - code/helloworld.py
            - $[[names]]
          parameters:
            helloworld: code/helloworld.py
            inputfile: $[[names]]
            outputfile: results/greetings.txt
            sleeptime: $[[sleeptime]]
        workflow:
          type: serial
          specification:
            steps:
              - environment: 'python:2.7'
                commands:
                  - python "${helloworld}"
                      --inputfile "${inputfile}"
                      --outputfile "${outputfile}"
                      --sleeptime ${sleeptime}
        outputs:
          files:
           - results/greetings.txt
    parameters:
        - id: names
          name: Person names
          description: Text file containing person names
          datatype: file
        - id: sleeptime
          name: Sleep period
          description: Sleep period in seconds
          datatype: int


In this example, the workflow section is a REANA workflow specification. The main modification to the workflow specification is a simple addition to the syntax in order to allow references to template parameters. Such references are always enclosed in ``$[[...]]``. The parameters section is a list of template parameter declarations. Each parameter declaration has a unique identifier. The identifier is used to reference the parameter from within the workflow specification (e.g., ``$[[sleeptime]]`` to reference the user-provided value for the sleep period). Other elements of the parameter declaration are a human readable short name, a parameter description, and a specification of the data type. Refer to the `Template Parameter Specification <https://github.com/scailfin/benchmark-templates/blob/master/docs/parameters.rst>`_ for a full description of the template parameter syntax.


Usage of Parameterized Workflow Templates
=========================================

Parameter declarations are intended to be used by front-end tools to render forms that collect user input. Given a set of user-provided values for the template parameters, the references to parameters are replaced withing the workflow specification with the given values to generate a valid workflow specification that can be executed by the respective workflow engine.

The definition of workflow templates is intended to be generic to allow usage in a variety of applications. With respect to *Reproducible Open Benchmarks* templates are used to define the benchark wroflow, the variable parts of the benchmark that are provided by the paricipants, and to describe the format of benchmark results that are used to generate the benchmark leaderboard. For this purpose, we define `Benchmark templates <https://github.com/scailfin/benchmark-templates/blob/master/docs/benchmark.rst>`_ that extend the base templates with information about the schema of the benchmark results.
