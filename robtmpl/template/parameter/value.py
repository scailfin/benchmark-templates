# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""The template argument class is used to represent user-provided values for
workflow template parameters. The class is a simple wrapper that combines
the value and the meta-data in the parameter declaration.
"""

from past.builtins import basestring

from robtmpl.core.io.files.base import FileHandle, InputFile
from robtmpl.template.parameter.base import ParameterBase

import robtmpl.template.parameter.declaration as pd


class TemplateArgument(ParameterBase):
    """Template arguments capture user-provided values for workflow template
    parameters that are used to instantiate and execute a parameterized workflow
    specification. The argument class captures the actual value and provides
    access to the parameter meta-data.
    """
    def __init__(self, parameter, value, validate=True):
        """Initialize the parameter value and meta-data. The type of the value
        argument depends on the data type of the parameter. If the parameter is
        of type record the value is expected to be a dictionary of arguments.
        If the parameter is of type list the value is expected to be a list of
        lists.

        Parameters
        ----------
        parameter: robtmpl.template.parameter.base.TemplateParameter
            Parameter declaration
        value: list or dict or scalar or robtmpl.template.parameter.value.InputFile
            Parameter value. the type depends on the parameter data type.
        validate: bool, optional
            Validate the argument value against the parameter declaration if
            set to True

        Raises
        ------
        ValueError
        """
        super(TemplateArgument, self).__init__(
            identifier=parameter.identifier,
            data_type=parameter.data_type
        )
        # Modify the given argument value if it is of type FileHandle
        if parameter.is_file() and isinstance(value, FileHandle):
            if parameter.has_constant():
                if parameter.as_input():
                    raise ValueError(
                        'expected input file for \'{}\''.format(self.identifier)
                    )
                else:
                    target_path = parameter.get_constant()
            else:
                target_path = value.name
            self.value = InputFile(
                f_handle=value,
                target_path=target_path
            )
        else:
            self.value = value
        # Validate the argument value if the validate flag is set to True
        if validate:
            self.validate()

    def validate(self):
        """Validate the argument value against the parameter declaration. This
        method does not return any value but it raises a ValueError if the
        argument value is not valid with respect to the parameter declaration.

        Raises
        ------
        ValueError
        """
        if self.is_bool():
            if not isinstance(self.value, bool):
                raise ValueError('expected bool for \'{}\''.format(self.identifier))
        elif self.is_float():
            if not isinstance(self.value, float):
                raise ValueError('expected float for \'{}\''.format(self.identifier))
        elif self.is_int():
            if not isinstance(self.value, int):
                raise ValueError('expected int for \'{}\''.format(self.identifier))
        elif self.is_string():
            if not isinstance(self.value, basestring):
                raise ValueError('expected string for \'{}\''.format(self.identifier))
        elif self.is_file():
            # Expects a file handle
            if not isinstance(self.value, InputFile):
                raise ValueError('expected input file for \'{}\''.format(self.identifier))
        elif self.is_list():
            if not isinstance(self.value, list):
                raise ValueError('expected list for \'{}\''.format(self.identifier))
            for record in self.value:
                for arg in record.values():
                    arg.validate()
        elif self.is_record():
            if not isinstance(self.value, dict):
                raise ValueError('expected dictionary for \'{}\''.format(self.identifier))
            for arg in self.value.values():
                arg.validate()
        else:
            raise ValueError('unknown data type \'{}\''.format(self.data_type))


# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def mandatory_arguments(parameters, parent=None):
    """Get a list of parameter names that are mandatory. The optional parent
    parameter allows to request mandatory parameter for nested components.

    Parameters
    ----------
    parameters: dict(robtmpl.template.parameter.base.TemplateParameter)
        Dictionary of parameter declarations
    parent: robtmpl.template.parameter.base.TemplateParameter
        Parent paremeter declaration for nested structures

    Returns
    -------
    list(string)
    """
    result = list()
    for para in parameters.values():
        if not para.is_required:
            continue
        if para.parent == parent:
            result.append(para.identifier)
    return result


def parse_arguments(arguments, parameters, validate=False, parent=None):
    """Convert a dictionary of argument identifier and argument value pairs into
    a dictionary of template argument instances.

    Parameters
    ----------
    arguments: dict()
        Key, value pairs of argument identifier and argument value
    parameters: dict(robtmpl.template.parameter.base.TemplateParameter)
        Dictionary of parameter declarations
    validate: bool, optional
        Validate argument value agains parameter declaration if True
    parent: robtmpl.template.parameter.base.TemplateParameter
        Parent paremeter declaration for nested structures

    Returns
    -------
    dict(robtmpl.template.parameter.value.TemplateArgument)

    Raises
    ------
    ValueError
    """
    result = dict()
    for arg_id, arg_value in arguments.items():
        # Get the parameter declaration. Raise error if the parameter id is
        # unknown.
        if not arg_id in parameters:
            raise ValueError('unknown argument \'{}\''.format(arg_id))
        para = parameters[arg_id]
        if isinstance(arg_value, list) and para.is_list():
            # Expects a list of records
            value = list()
            for rec in arg_value:
                value.append(
                    parse_arguments(
                        arguments=rec,
                        parameters=parameters,
                        validate=validate,
                        parent=para
                    )
                )
        elif isinstance(arg_value, dict) and para.is_record():
            # Expects a dictionary of argument values (i.e., a record)
            value = parse_arguments(
                arguments=arg_value,
                parameters=parameters,
                validate=validate,
                parent=para
            )
        elif not (para.is_list() or para.is_record()):
            value = arg_value
        else:
            raise ValueError('invalid value for \'{}\''.format(arg_id))
        result[arg_id] = TemplateArgument(
            parameter=para,
            value=value,
            validate=validate
        )
    # Ensure that all mandatory arguments are given
    for key in mandatory_arguments(parameters, parent=parent):
        if not key in result:
            raise ValueError('missing value for \'{}\''.format(key))
    return result
