# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Handles and descriptors for resources that are created by successful workflow
runs.

The resource descriptor is used to define the type of resources that are
generated by workflow runs.

Resource handles represent resources that are created as the result of a
successful workflow run. The most common type of resource at this point are
plain files.

In the future we might want to maintain additional information about the files
(e.g. serialization format and schema), as well as allow additional types of
resources.
"""

from robtmpl.core.error import InvalidTemplateError


"""Identifier for resource types."""
RESOURCE_FILE = 'file'


"""Element labels for serialization of resource descriptors."""
LABEL_FILEPATH = 'filepath'
LABEL_ID = 'id'
LABEL_TYPE = 'type'


class ResourceDescriptor(object):
    """Each resource handle has an identifier that is unique among the resources
    that are created by a workflow run. The identifier should remain the same
    over different runs for the same type of resource (e.g., an output file that
    is expected to be generated by a workflow run).

    The resource descriptor also has a type identifier.
    """
    def __init__(self, identifier, type_id):
        """Initialize the resource identifier and the type identifier.

        Parameters
        ----------
        identifier: string
            Resource identifier that is unique among all resources that are
            created within a single workflow run.
        type_id: string
            Identifier for resource type
        """
        self.identifier = identifier
        self.type_id = type_id

    @staticmethod
    def from_dict(doc):
        """Get instance of the resource descriptor from a dictionary
        serialization as created by the to_dict() method. Expects a dictionary
        with two elements 'id' and 'type'.

        Raises InvalidTemplateError if an invalid dictionary is given.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a resource descriptor

        Returns
        -------
        robtmpl.workflow.resource.base.ResourceDescriptor

        Raises
        ------
        robtmpl.core.error.InvalidTemplateError
        """
        if not (LABEL_ID in doc and LABEL_TYPE in doc):
            raise InvalidTemplateError('invalid resource descriptor serialization')
        if doc[LABEL_TYPE] == RESOURCE_FILE:
            return FileResource.from_dict(doc)
        else:
            raise ValueError('unknown resource type \'{}\''.format(type_id))

    def to_dict(self):
        """Create dictionary serialization of the resource descriptor

        Returns
        -------
        dict
        """
        return {LABEL_ID: self.identifier, LABEL_TYPE: self.type_id}


class FileResource(ResourceDescriptor):
    """Handle for a file resource that is created as the result of a workflow
    run. The handle contains the reference to the persistent file that is stored
    on disk. The file should be maintaioned by the workflow backend in a
    persistent manner in order to be accessible as long as information about
    the workflow run is maintained in some backend database.
    """
    def __init__(self, identifier, filepath):
        """Initialize the resource identifier and the path to the (persistently)
        created file.

        Parameters
        ----------
        identifier: string
            Resource identifier that is unique among all resources that are
            created within a single workflow run.
        filepath: string
            Path to persistent file on disk.
        """
        super(FileResource, self).__init__(
            identifier=identifier,
            type_id=RESOURCE_FILE
        )
        self.filepath = filepath

    @staticmethod
    def from_dict(doc):
        """Get instance of the file resource descriptor from a dictionary
        serialization as created by the to_dict() method. Expects a dictionary
        with three elements 'id', 'type.' and 'filepath'.

        Raises an error if an invalid dictionary is given.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a file resource descriptor

        Returns
        -------
        robtmpl.workflow.resource.base.FileResource

        Raises
        ------
        ValueError
        """
        # Expect exactly three elements in the dictionary
        if len(doc) != 3:
            raise ValueError('invalid file resource descriptor')
        if not (LABEL_ID in doc and LABEL_TYPE in doc and LABEL_FILEPATH in doc):
            raise ValueError('invalid file resource descriptor')
        if doc[LABEL_TYPE] != RESOURCE_FILE:
            raise ValueError('invalid file resource descriptor')
        return FileResource(
            identifier=doc[LABEL_ID],
            filepath=doc[LABEL_FILEPATH]
        )

    def to_dict(self):
        """Create dictionary serialization of the file resource. Extends the
        descriptor serialization with the file path.

        Returns
        -------
        dict
        """
        obj = super(FileResource, self).to_dict()
        obj[LABEL_FILEPATH] = self.filepath
        return obj
