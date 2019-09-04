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

class UnknownRunError(ROBError):
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
            message='unknown run \'{}\''.format(identifier)
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


class UnknownParameterError(ROBError):
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
            message='reference to undefined parameter \'{}\''.format(identifier)
        )


class UnknownTemplateError(ROBError):
    """Exception indicating that a given template identifier does not reference
    an existing template.
    """
    def __init__(self, identifier):
        """Initialize error message for unknown template identifier.

        Parameters
        ----------
        identifier: string
            Unique template identifier
        """
        super(UnknownTemplateError, self).__init__(
            message='unknown template \'{}\''.format(identifier)
        )
