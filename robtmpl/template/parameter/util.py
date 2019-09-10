# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper methods for workflow template parameters."""

from __future__ import print_function

from robtmpl.core.io.files.base import FileHandle
from robtmpl.core.io.scanner import Scanner
from robtmpl.template.parameter.base import TemplateParameter
from robtmpl.template.parameter.value import InputFile

import robtmpl.core.error as err
import robtmpl.template.parameter.declaration as pd


# -- Parameter index -----------------------------------------------------------

def create_parameter_index(parameters, validate=True):
    """Create instances of template parameters from a list of dictionaries
    containing parameter declarations. The result is a dictionary containing the
    top-level parameters, indexed by their unique identifier.

    Parameters
    ----------
    parameters: list(dict)
        List of dictionaries containing template parameter declarations
    validate: bool, optional
        Flag indicating if given template parameter declarations are to be
        validated against the parameter schema or not.

    Returns
    -------
    dict(string: robtmpl.template.parameter.base.TemplateParameter)

    Raises
    ------
    robtmpl.core.error.InvalidTemplateError
    robtmpl.core.error.UnknownParameterError
    """
    result = dict()
    for para in parameters:
        # Validate the template parameters if the validate flag is True
        if validate:
            pd.validate_parameter(para)
        # Create a TemplateParameter instance for the parameter. Keep
        # track of children for parameter that are of type DT_LIST or
        # DT_RECORD. Children are added after all parameters have been
        # instantiated.
        p_id = para[pd.LABEL_ID]
        # Ensure that the identifier of all parameters are unique
        if p_id in result:
            msg = 'parameter \'{}\' not unique'.format(p_id)
            raise err.InvalidTemplateError(msg)
        c = None
        if para[pd.LABEL_DATATYPE] in [pd.DT_LIST, pd.DT_RECORD]:
            c = list()
        tp = TemplateParameter(pd.set_defaults(para), children=c)
        result[p_id] = tp
    # Add parameter templates to the list of children for their
    # respective parent (if given). We currently only support one level
    # of nesting.
    for para in parameters:
        if pd.LABEL_PARENT in para:
            p_id = para[pd.LABEL_ID]
            parent = para[pd.LABEL_PARENT]
            if not parent is None:
                result[parent].add_child(result[p_id])
    return result


# -- Read parameter values -----------------------------------------------------

def read(parameters, scanner=None):
    """Read values for each of the template parameters using a given input
    scanner. If no scanner is given values are read from standard input.

    Returns a dictionary of argument values that can be passed to the workflow
    execution engine to run a parameterized workflow.

    Parameters
    ----------
    parameters: list(robtmpl.template.parameter.base.TemplateParameter)
        List of workflow template parameter declarations
    scanner: robtmpl.core.io.scanner.Scanner
        Input scanner to read parameter values

    Returns
    -------
    dict
    """
    sc = scanner if not scanner is None else Scanner()
    arguments = dict()
    for para in parameters:
        # Skip nested parameter
        if not para.parent is None:
            continue
        if para.is_list():
            raise ValueError('lists are not supported yet')
        elif para.is_record():
            # A record can only appear once and all record children have
            # global unique identifier. Thus, we can add values for each
            # of the children directly to the arguments dictionary
            for child in para.children:
                val = read_parameter(child, sc, prompt_prefix='  ')
                if not val is None:
                    arguments[child.identifier] = val
        else:
            val = read_parameter(para, sc)
            if not val is None:
                arguments[para.identifier] = val
    return arguments



def read_parameter(para, scanner, prompt_prefix=''):
    """Read value for a given template parameter declaration. Prompts the
    user to enter a value for the given parameter and returns the converted
    value that was entered by the user.

    Parameters
    ----------
    para: robtmpl.template.parameter.TemplateParameter
        Workflow template parameter declaration

    Returns
    -------
    bool or float or int or string or robtmpl.template.parameter.base.InputFile
    """
    while True:
        print(prompt_prefix + para.prompt(), end='')
        try:
            if para.is_bool():
                return scanner.next_bool(default_value=para.default_value)
            elif para.is_file():
                filename = scanner.next_file(default_value=para.default_value)
                target_path = None
                if para.has_constant() and para.as_input():
                    print('Target Path:', end='')
                    target_path = scanner.next_string()
                return InputFile(
                    f_handle=FileHandle(filepath=filename),
                    target_path=target_path
                )
            elif para.is_float():
                return scanner.next_float(default_value=para.default_value)
            elif para.is_int():
                return scanner.next_int(default_value=para.default_value)
            else:
                return scanner.next_string(default_value=para.default_value)
        except ValueError as ex:
            print(ex)
