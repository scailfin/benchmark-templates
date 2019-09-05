# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Template stores that maintain templates as Json objects."""

import os

from robtmpl.template.base import WorkflowTemplate
from robtmpl.template.io.base import TemplateStore

import robtmpl.core.error as err
import robtmpl.core.util as util


class JsonFileStore(TemplateStore):
    """The Json file store maintains workflow template specifications as
    separate files on disk. Files are stored under a given base directory. The
    file format is Json.

    For each template the store will either create a file in the base directory
    using the template identifier as name or create a file with a given default
    name in a sub-directory named after the template identifier. This behavior
    is controlled by the default_file_name attribute. If the attribute is None
    the former case is True, otherwise the latter case.
    """
    def __init__(self, base_dir, default_file_name=None):
        """Initialize the base directory and the default file name. Templates
        are stored in files under the base directory. Depending on whether the
        default file name is given, templates are either stored as files named
        using the template identifier (default_file_name is None) or in a sub-
        directory named after the template identifier (default_file_name is not
        None).
        """
        # Set the directory and ensure that it exists
        self.base_dir = util.create_dir(base_dir)
        self.default_file_name = default_file_name

    def get_filename(self, identifier):
        """The name for a template file depends on the value of the default
        file name attribute.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        string
        """
        if self.default_file_name is None:
            # The file is in the base directory named after the template
            # identifier
            return os.path.join(self.base_dir, '{}.json'.format(identifier))
        else:
            # The file is in a sub-directory named after the identifier
            sub_dir = os.path.join(self.base_dir, identifier)
            return os.path.join(sub_dir, self.default_file_name)

    def read(self, identifier):
        """Read workflow template with the given identifier from the store.
        Raises an error if the identifier is unknown.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        robtmpl.template.base.WorkflowTemplate

        Raises
        ------
        robtmpl.core.error.UnknownTemplateError
        """
        filename = self.get_filename(identifier)
        # Raise an error if the file does not exist
        if not os.path.isfile(filename):
            raise err.UnknownTemplateError(identifier)
        # Read file from disk and return template instance. The base directory
        # for the template instance is the folder that contains the
        doc = util.read_object(filename, format=util.FORMAT_JSON)
        return WorkflowTemplate.from_dict(doc, identifier=identifier)

    def write(self, template):
        """Write the given template to the store. Replaces an existing template
        with the same identifier if it exists.

        Parameters
        ----------
        template: robtmpl.template.base.WorkflowTemplate
            Instance of a template handle class that is supported by the
            template loader

        """
        filename = self.get_filename(template.identifier)
        util.write_object(
            obj=template.to_dict(),
            filename=filename,
            format=util.FORMAT_JSON
        )
