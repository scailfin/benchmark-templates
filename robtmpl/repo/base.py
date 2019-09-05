# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Base classes and interfaces for template repositories. Contains the abstract
repository interface and the template handle that represents entries in a
repository.
"""

from abc import abstractmethod

import robtmpl.core.util as util


""" "Default value for max. attempts parameters."""
DEFAULT_MAX_ATTEMPTS = 100


class TemplateHandle(object):
    """The template handle represents workflow templates that are maintained in
    a template repository. With each entry in the repository a set of additional
    information is stored.

    The basic information for repository entries contains the unique template
    identifier, a unique name, an optional short description, and an optional
    set of instructions. Both, the identifier and the name of a template are
    expected to be unique. The name is used to identify the template in listings
    that are visible to the user.

    The workflow template itself may be loaded on demand to avoid having to
    read all information when listing all entries in a repository, for example.
    """
    def __init__(
        self, identifier, name, description=None, instructions=None,
        template=None, store=None
    ):
        """Initialize the handle properties and the reference to the workflow
        template.

        Raises a ValueError if both, the template and the store are None.

        Parameters
        ----------
        identifier: string
            Unique template identifier
        name: string
            Unique template name
        description: string, optional
            Optional short description for display in listings
        instructions: string, optional
            Text containing detailed instructions for benchmark participants
        template: robtmpl.template.base.WorkflowTemplate, optional
            Reference to the associated workflow template. The template may be
            None in which case it will be loaded on demand from the repository.
        store: robtmpl.template.io.base.TemplateStore, optional
            Reference to the template store that contains the workflow template.
            This reference is required to load the template on demand.

        Raises
        ------
        ValueError
        """
        # Raise ValueError if template and store are None
        if template is None and store is None:
            raise ValueError('no workflow template given')
        self.identifier = identifier
        self.name = name
        self.description = description
        self.instructions = instructions
        self.template = template
        self.store = store

    def has_description(self):
        """Shortcut to test of the description attribute is set.

        Returns
        -------
        bool
        """
        return not self.description is None

    def has_instructions(self):
        """Test if the instructions for the benchmark are set.

        Returns
        -------
        bool
        """
        return not self.instructions is None

    def has_schema(self):
        """Test if the result schema is set.

        Returns
        -------
        bool
        """
        return not self.get_workflow_template().result_schema is None

    def get_workflow_template(self):
        """Access the associated template. The template is loaded on demand from
        the template store if it is None.

        Returns
        -------
        robtmpl.template.base.WorkflowTemplate
        """
        if self.template is None:
            self.template = self.store.read(self.identifier)
        return self.template


class TemplateRepository(object):
    """The template repository maintains a set of workflow templates. For each
    workflow template a copy of the static files that are used as input in the
    workflow is maintained.

    In addition to workflow templates the results of individual template runs
    are maintained as well.
    """
    def __init__(self, id_func=None, max_attempts=DEFAULT_MAX_ATTEMPTS):
        """Initialize the identifier function that is used to generate unique
        template identifier. By default, short identifier are used.

        Parameters
        ----------
        id_func: func, optional
            Function to generate template folder identifier
        max_attempts: int, optional
            Maximum number of attempts to create a unique folder for a new
            workflow template
        """
        self.id_func = id_func if not id_func is None else util.get_short_identifier
        self.max_attempts = max_attempts

    @abstractmethod
    def add_template(
        self, name, description=None, instructions=None, src_dir=None,
        src_repo_url=None, template_spec_file=None
    ):
        """Create file and folder structure for a new workflow template. Assumes
        that either a workflow source directory or the Url of a remote Git
        repository is given.

        Each template is assigned a unique identifier. Creates a copy of the
        file structure for the static workflow template files.

        The source folder is expected to contain the template specification
        file. If the template_spec file is not given the method will look for a
        file from a default list of file names. If no template file is found in
        the source folder a ValueError is raised.

        Parameters
        ----------
        name: string
            Unique template name for display purposes
        description: string, optional
            Optional short description for display in listings
        instructions: string, optional
            Optional text containing detailed instructions for benchmark
            participants
        src_dir: string, optional
            Directory containing the workflow components, i.e., the fixed
            files and the template specification (optional).
        src_repo_url: string, optional
            Git repository that contains the the workflow components
        template_spec_file: string, optional
            Path to the workflow template specification file (absolute or
            relative to the workflow directory)

        Returns
        -------
        robtmpl.template.base.WorkflowTemplate

        Raises
        ------
        robtmpl.core.error.InvalidParameterError
        robtmpl.core.error.InvalidTemplateError
        ValueError
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_template(self, identifier):
        """Delete all resources that are associated with the given template.
        The result is True if the template existed and False otherwise.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        bool
        """
        raise NotImplementedError()

    @abstractmethod
    def exists_template(self, identifier):
        """Test if a template with the given identifier exists.

        Returns
        -------
        bool
        """
        raise NotImplementedError()

    @abstractmethod
    def get_template(self, identifier):
        """Get handle for the template with the given identifier.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        robtmpl.repo.base.TemplateHandle

        Raises
        ------
        robtmpl.core.error.UnknownTemplateError
        """
        raise NotImplementedError()

    def get_unique_identifier(self):
        """Create a new unique identifier for a workflow template.

        Returns
        -------
        string

        Raises
        ------
        ValueError
        """
        identifier = None
        attempt = 0
        while identifier is None:
            identifier = self.id_func()
            if self.exists_template(identifier):
                identifier = None
                attempt += 1
                if attempt > self.max_attempts:
                    raise RuntimeError('could not create unique directory')
        return identifier

    @abstractmethod
    def list_templates(self):
        """Get list of all templates in the repository.

        Returns
        -------
        list(robtmpl.repo.base.TemplateHandle)
        """
        raise NotImplementedError()
