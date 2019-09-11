===================================
Repositories for Workflow Templates
===================================

The package contains a default implementation for a repository to maintain workflow templates. The repository stores all the relevant information and files in separate directories on the file system.


Directory Structure
===================

The **Template Repository** is used to maintain copies of workflow templates in a uniform way. All templates are maintained as files on the file system under a base directory. The respective directory structure is as follows:

.. line-block::

    <base-directory>/
        <template-id>/
            static/
            repository.json


Each template is assigned a unique identifier. The identifier is used as the directory name for all information related to to template. For each workflow template static files are stored in a sub-directory ``static``. The template specification is maintained (in Json format) in a file called ``template.json``.

When the template is added to the repository, either a source directory on the file system or the URL of a Git repository is expected. If a repository URL is given, the repository will be cloned into a local source directory. The repository will create a new sub-directory for the template using an automatically generated unique identifier. The repository expects a file containing the template specification in the given source. By default, the repository will look for a file with one of the following names (in this order):

.. line-block::

    benchmark.yml
    benchmark.yaml
    benchmark.json
    template.yml
    template.yaml
    template.json
    workflow.yml
    workflow.yaml
    workflow.json

The first matching file is expected to contain the template specification. The suffix determines the expected file format (``.yml`` and ``.yaml`` for files in Yaml format and ``'json`` for Json format). If a specification file is found, the content is stored as ``repository.json`` in the template folder. All files in the source directory are (recursively) copied to the ``static`` folder.


UML Diagram
===========

The UML diagram for the relevant classes is shown below:

.. figure:: figures/repository.png
   :scale: 50 %
   :alt: UML Diagram for Repositories

UML Diagram of classes that are relevant for workflow template and benchmark repositories.
