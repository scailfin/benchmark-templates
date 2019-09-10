# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Exceptions that are raised by the various components of the reproducible
open benchmark components.
"""


class ROBError(Exception):
    """Base exception indicating that a component of benchmark templates
    encountered an error situation.
    """
    def __init__(self, message):
        """Initialize error message.

        Parameters
        ----------
        message : string
            Error message
        """
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        """Get printable representation of the exception.

        Returns
        -------
        string
        """
        return self.message

class UnknownObjectError(ROBError):
    """Generic error for references to unknown objects.
    """
    def __init__(self, obj_id, type_name='object'):
        """Initialize error message.

        Parameters
        ----------
        obj_id: string
            Unique object identifier
        type_name: string, optional
            Name of type of the referenced object
        """
        super(UnknownObjectError, self).__init__(
            message='unknown {} \'{}\''.format(type_name, obj_id)
        )


# -- Configuration -------------------------------------------------------------

class MissingConfigurationError(ROBError):
    """Error indicating that the value for an environment variable is not set.
    """
    def __init__(self, var_name):
        """Initialize error message.

        Parameters
        ----------
        var_name: string
            Environment variable name
        """
        super(MissingConfigurationError, self).__init__(
            message='variable \'{}\' not set'.format(var_name)
        )


# --  Workflow Engine ----------------------------------------------------------

class DuplicateRunError(ROBError):
    """Exception indicating that a given run identifier is not unique.
    """
    def __init__(self, identifier):
        """Initialize error message for duplicate run identifier.

        Parameters
        ----------
        identifier: string
            Unique run identifier
        """
        super(DuplicateRunError, self).__init__(
            message='non-unique run identifier \'{}\''.format(identifier)
        )


class UnknownRunError(UnknownObjectError):
    """Exception indicating that a given run identifier does not reference a
    known workflow run.
    """
    def __init__(self, identifier):
        """Initialize error message for unknown run identifier.

        Parameters
        ----------
        identifier: string
            Unique run identifier
        """
        super(UnknownRunError, self).__init__(
            type_name='run',
            obj_id=identifier
        )


# -- Workflow Templates --------------------------------------------------------

class InvalidParameterError(ROBError):
    """Exception indicating that a given template parameter is invalid.
    """
    def __init__(self, message):
        """Initialize error message. The message for invalid parameter errors
        is depending on the context

        Parameters
        ----------
        message : string
            Error message
        """
        super(InvalidParameterError, self).__init__(message=message)


class InvalidTemplateError(ROBError):
    """Exception indicating that a given workflow template is invalid or has
    missing elements.
    """
    def __init__(self, message):
        """Initialize error message. The message for invalid template errors
        is depending on the context

        Parameters
        ----------
        message : string
            Error message
        """
        super(InvalidTemplateError, self).__init__(message=message)


class MissingArgumentError(ROBError):
    """Exception indicating that a required parameter in a workflow template
    has no argument given for a workflow run.
    """
    def __init__(self, identifier):
        """Initialize missing argument error message for parameter identifier.

        Parameters
        ----------
        identifier: string
            Unique parameter identifier
        """
        super(MissingArgumentError, self).__init__(
            message='missing argument for \'{}\''.format(identifier)
        )


class UnknownParameterError(UnknownObjectError):
    """Exception indicating that a workflow specification references a parameter
    that is not defined for a given template.
    """
    def __init__(self, identifier):
        """Initialize error message for given parameter identifier.

        Parameters
        ----------
        identifier: string
            Unique template parameter identifier
        """
        super(UnknownParameterError, self).__init__(
            type_name='parameter',
            obj_id=identifier
        )


class UnknownTemplateError(UnknownObjectError):
    """Error when referencing a workflow template with an unknown identifier.
    """
    def __init__(self, identifier):
        """Initialize error message.

        Parameters
        ----------
        identifier: string
            Unique template identifier
        """
        super(UnknownTemplateError, self).__init__(
            type_name='template',
            obj_id=identifier
        )
