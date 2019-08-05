"""Test functionality of the template arguments modules."""

import os
import pytest

from benchtmpl.io.files.base import FileHandle
from benchtmpl.workflow.parameter.base import TemplateParameter
from benchtmpl.workflow.template.base import TemplateHandle
from benchtmpl.workflow.template.loader import DefaultTemplateLoader

import benchtmpl.workflow.parameter.declaration as pd
import benchtmpl.workflow.parameter.value as values
import benchtmpl.workflow.template.loader as tmpl


DIR = os.path.dirname(os.path.realpath(__file__))
LOCAL_FILE = os.path.join(DIR, '../../.files/schema.json')


class TestArgumentValues(object):
    """Test parsing and validating argument values for parameterized workflow
    templates.
    """
    def test_flat_parse(self):
        """Test parsing arguments for a flat (un-nested) parameter declaration.
        """
        template = TemplateHandle(
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(pd.parameter_declaration('A', data_type=pd.DT_INTEGER)),
                TemplateParameter(pd.parameter_declaration('B', data_type=pd.DT_BOOL)),
                TemplateParameter(pd.parameter_declaration('C', data_type=pd.DT_DECIMAL)),
                TemplateParameter(pd.parameter_declaration('D', data_type=pd.DT_FILE, required=False)),
                TemplateParameter(pd.parameter_declaration('E', data_type=pd.DT_STRING, required=False))
            ]
        )
        params = template.parameters
        fh = FileHandle(filepath=LOCAL_FILE)
        # Valid argument set
        args = values.parse_arguments(
            arguments={'A': 10, 'B': True, 'C': 12.5, 'D': fh, 'E': 'ABC'},
            parameters=params,
            validate=True
        )
        assert len(args) == 5
        for key in params.keys():
            assert key in args
        values.parse_arguments(arguments=args, parameters=params, validate=False)
        # Error cases
        with pytest.raises(ValueError):
            values.parse_arguments(arguments={'A': 10, 'Z': 0}, parameters=params)
        with pytest.raises(ValueError):
            values.parse_arguments(arguments={'A': 10, 'B': True}, parameters=params)
        # Validate data type
        with pytest.raises(ValueError):
            values.parse_arguments(
                arguments={'A': '10', 'B': True, 'C': 12.3, 'D': fh, 'E': 'ABC'},
                parameters=params,
                validate=True
            )
        with pytest.raises(ValueError):
            values.parse_arguments(
                arguments={'A': 10, 'B': 23, 'C': 12.3, 'D': fh, 'E': 'ABC'},
                parameters=params,
                validate=True
            )
        with pytest.raises(ValueError):
            values.parse_arguments(
                arguments={'A': 10, 'B': True, 'C': '12.3', 'D': fh, 'E': 'ABC'},
                parameters=params,
                validate=True
            )
        with pytest.raises(ValueError):
            values.parse_arguments(
                arguments={'A': 10, 'B': True, 'C': 12.3, 'D': 'fh', 'E': 'ABC'},
                parameters=params,
                validate=True
            )
        with pytest.raises(ValueError):
            values.parse_arguments(
                arguments={'A': 10, 'B': True, 'C': 12.3, 'D': fh, 'E': 12},
                parameters=params,
                validate=True
            )

    def test_nested_parse(self):
        """Test parsing arguments for a nested parameter declaration."""
        template = DefaultTemplateLoader().from_dict({
                tmpl.LABEL_WORKFLOW: dict(),
                tmpl.LABEL_PARAMETERS: [
                    pd.parameter_declaration('A', data_type=pd.DT_INTEGER),
                    pd.parameter_declaration('B', data_type=pd.DT_RECORD),
                    pd.parameter_declaration('C', data_type=pd.DT_DECIMAL, parent='B'),
                    pd.parameter_declaration('D', data_type=pd.DT_STRING, parent='B', required=False),
                    pd.parameter_declaration('E', data_type=pd.DT_LIST, required=False),
                    pd.parameter_declaration('F', data_type=pd.DT_INTEGER, parent='E'),
                    pd.parameter_declaration('G', data_type=pd.DT_DECIMAL,  parent='E', required=False)
                ]
            },
            validate=True
        )
        params = template.parameters
        # Without values for list parameters
        args = values.parse_arguments(
            arguments={'A': 10, 'B': {'C': 12.3}},
            parameters=params,
            validate=True
        )
        assert len(args) == 2
        assert args['B'].has('C')
        assert not args['B'].has('D')
        assert args['B'].len() == 1
        assert args['B'].get('C').value == 12.3
        # With list arguments
        args = values.parse_arguments(
            arguments={
                'A': 10,
                'B': {'C': 12.3, 'D': 'ABC'},
                'E': [
                    {'F': 1},
                    {'F': 2},
                    {'F': 3, 'G': 0.9}
                ]
            },
            parameters=params,
            validate=True
        )
        assert len(args) == 3
        assert args['B'].has('C')
        assert args['B'].has('D')
        assert args['B'].len() == 2
        assert args['E'].len() == 3
        for arg in args['E'].value:
            if arg.get('F').value < 3:
                assert len(arg) == 1
            else:
                assert len(arg) == 2
        # Error cases
        with pytest.raises(ValueError):
            values.parse_arguments(
                arguments={'A': 10, 'B': [{'C': 12.3}]},
                parameters=params,
                validate=True
            )

    def test_validate(self):
        """Test error cases for argument validation."""
        para_list = TemplateParameter(pd.parameter_declaration('E', data_type=pd.DT_LIST))
        values.TemplateArgument(parameter=para_list, value=1)
        with pytest.raises(ValueError):
            values.TemplateArgument(parameter=para_list, value=1, validate=True)
        para_record = TemplateParameter(pd.parameter_declaration('E', data_type=pd.DT_RECORD))
        values.TemplateArgument(parameter=para_record, value=list())
        with pytest.raises(ValueError):
            values.TemplateArgument(parameter=para_record, value=list(), validate=True)
        arg = values.TemplateArgument(
            parameter=TemplateParameter(pd.parameter_declaration('E', data_type=pd.DT_INTEGER)),
            value=1,
            validate=True
        )
        arg.data_type = 'unknown'
        with pytest.raises(ValueError):
            arg.validate()
