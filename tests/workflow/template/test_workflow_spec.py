"""Test replacing parameters with argument values in a parameterized workflow
specification.
"""

from benchtmpl.io.files.base import FileHandle
from benchtmpl.workflow.parameter.base import TemplateParameter
from benchtmpl.workflow.parameter.value import TemplateArgument

import benchtmpl.workflow.parameter.util as pd
import benchtmpl.workflow.parameter.value as pr
import benchtmpl.workflow.template.base as tmpl


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
