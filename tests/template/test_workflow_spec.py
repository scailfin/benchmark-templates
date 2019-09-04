# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test replacing parameters with argument values in a parameterized workflow
specification.
"""

from robtmpl.core.io.files.base import FileHandle
from robtmpl.template.parameter.base import TemplateParameter
from robtmpl.template.parameter.value import TemplateArgument

import robtmpl.template.parameter.util as pd
import robtmpl.template.parameter.value as pr
import robtmpl.template.base as tmpl


class TestReplaceSpecificationParameters(object):
    """Test replacing parameter references in workflow specifications."""
    def test_file_args(self):
        """Test the replace_args function for file parameters."""
        spec = {
            'input': [
                '$[[codeFile]]'
            ]
        }
        parameters = pd.create_parameter_index([
            {
                'id': 'codeFile',
                'datatype': 'file',
                'defaultValue': 'src/helloworld.py',
                'as': 'code/helloworld.py'
            }
        ])
        # Test default values (no arguments)
        wf = tmpl.replace_args(
            spec=spec,
            parameters=parameters,
            arguments=dict()
        )
        assert wf['input'] == ['code/helloworld.py']
        # Test default values (with arguments)
        wf = tmpl.replace_args(
            spec=spec,
            parameters=parameters,
            arguments=pr.parse_arguments(
                arguments={'codeFile': FileHandle(filepath='/dev/null')},
                parameters=parameters
            )
        )
        assert wf['input'] == ['code/helloworld.py']
        # Test file parameters without constant value
        parameters = pd.create_parameter_index([
            {
                'id': 'codeFile',
                'datatype': 'file',
                'defaultValue': 'src/helloworld.py'
            }
        ])
        # Test default values (no arguments)
        wf = tmpl.replace_args(
            spec=spec,
            parameters=parameters,
            arguments=dict()
        )
        assert wf['input'] == ['src/helloworld.py']
        wf = tmpl.replace_args(
            spec=spec,
            parameters=parameters,
            arguments=pr.parse_arguments(
                arguments={'codeFile': FileHandle(filepath='/dev/null')},
                parameters=parameters
            )
        )
        assert wf['input'] == ['null']

    def test_scalar_args(self):
        """Test the replace_args function for scalar values."""
        spec = {
            'parameters': {
                'sleeptime': '$[[sleeptime]]'
            }
        }
        parameters = pd.create_parameter_index([
            {
                'id': 'sleeptime',
                'datatype': 'int',
                'defaultValue': 10
            }
        ])
        # Test default values (no arguments)
        wf = tmpl.replace_args(
            spec=spec,
            parameters=parameters,
            arguments=dict()
        )
        assert wf['parameters'] == {'sleeptime': 10}
        # Test default values (with arguments)
        wf = tmpl.replace_args(
            spec=spec,
            parameters=parameters,
            arguments=pr.parse_arguments(
                arguments={'sleeptime': 5},
                parameters=parameters
            )
        )
        assert wf['parameters'] == {'sleeptime': 5}
