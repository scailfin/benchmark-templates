# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Interface for classes that store workflow templates."""

from abc import abstractmethod


class TemplateStore(object):
    """The template store is used to read and write workflow template
    specifications from and to a template store. Different implementations of
    this class may maintain templates in persistent stores, on the file system,
    or keep copies in main memory.
    """
    @abstractmethod
    def read(self, identifier):
        """Read workflow template with the given identifier from the store.
        Raises an error if the identifier is unknown.

        Parameters
        ----------
        identifier: string, optional
            Unique template identifier.

        Returns
        -------
        robtmpl.template.base.WorkflowTemplate

        Raises
        ------
        robtmpl.core.error.UnknownTemplateError
        """
        raise NotImplementedError()

    @abstractmethod
    def write(self, template):
        """Write the given template to the store. Replaces an existing template
        with the same identifier if it exists.

        Parameters
        ----------
        template: robtmpl.template.base.WorkflowTemplate
            Instance of a template handle class that is supported by the
            template loader

        """
        raise NotImplementedError()
