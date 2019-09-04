# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Defines environment variables and their default values that are used to
control the configuration of different components of the reproducible open
benchmark engine.

This module also provides methods to access the configuration values. The name
of methods that are indented for use outside of the module are in upper case to
emphasize that they access constant configuration values.
"""

import os

import robtmpl.core.error as err


"""Environment variables to configure the database driver."""
ROB_DB_CONNECT = 'ROB_DBCONNECT'
ROB_DB_ID = 'ROB_DBMS'


"""Environment variable for test purposes."""
ROB_TEST = 'ROB_TEST'


# -- Public helper methofd to access configuration values ----------------------

def DB_CONNECT(default_value=None, raise_error=False):
    """Get the connect string for the database from the respective environment
    variable 'ROB_DBCONNECT'. Raises a MissingConfigurationError if the
    raise_error flag is True and 'ROB_DBCONNECT' is not set. If the raise_error
    flag is False and 'ROB_DBCONNECT' is not set the default value is returned.

    Parameters
    ----------
    default_value: string, optional
        Default value if 'ROB_DBCONNECT' is not set and raise_error flag is
        False
    raise_error: bool, optional
        Flag indicating whether an error is raised if the environment variable
        is not set (i.e., None or and empty string '')

    Returns
    -------
    string
    """
    return get_variable(
        name=ROB_DB_CONNECT,
        default_value=default_value,
        raise_error=raise_error
    )


def DB_IDENTIFIER(default_value=None, raise_error=False):
    """Get the identifier for the database management system from the respective
    environment variable 'ROB_DBMS'. Raises a MissingConfigurationError if
    the raise_error flag is True and 'ROB_DBMS' is not set. If the
    raise_error flag is False and 'ROB_DBMS' is not set the default value is
    returned.

    Parameters
    ----------
    default_value: string, optional
        Default value if 'ROB_DBMS' is not set and raise_error flag is False
    raise_error: bool, optional
        Flag indicating whether an error is raised if the environment variable
        is not set (i.e., None or and empty string '')

    Returns
    -------
    string
    """
    return get_variable(
        name=ROB_DB_ID,
        default_value=default_value,
        raise_error=raise_error
    )


# -- Private helper methods ----------------------------------------------------

def get_variable(name, default_value, raise_error):
    """Get the value for the given  environment variable. Raises a
    MissingConfigurationError if the raise_error flag is True and the variable
    is not set. If the raise_error flag is False and the environment variables
    is not set then the default value is returned.

    Parameters
    ----------
    name: string
        Environment variable name
    default_value: string
        Default value if variable is not set and raise_error flag is False
    raise_error: bool
        Flag indicating whether an error is raised if the environment variable
        is not set (i.e., None or and empty string '')

    Returns
    -------
    string

    Raises
    ------
    robtmpl.core.error.MissingConfigurationError
    """
    value = os.environ.get(name)
    if value is None or value == '':
        if raise_error:
            raise err.MissingConfigurationError(name)
        else:
            value = default_value
    return value
