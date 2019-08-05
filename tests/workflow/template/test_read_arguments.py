"""Test read arguments function for REANA templates."""

import pytest

from benchtmpl.io.scanner import Scanner, ListReader
from benchtmpl.workflow.parameter.base import TemplateParameter
from benchtmpl.workflow.template.base import TemplateHandle

import benchtmpl.workflow.parameter.declaration as pd
import benchtmpl.workflow.template.util as tmpl


class TestReadTemplateArguments(object):
    def test_read_with_record(self):
        """Read argument for a template that contains a parameter of data type
        DT_RECORD.
        """
        template = TemplateHandle(
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='codeFile',
                        data_type=pd.DT_FILE,
                        index=0,
                        default_value=None
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='sleeptime',
                        data_type=pd.DT_INTEGER,
                        index=1,
                        default_value=10
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='verbose',
                        data_type=pd.DT_BOOL,
                        index=2,
                        default_value=False
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='frac',
                        data_type=pd.DT_DECIMAL,
                        index=4
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='outputType',
                        index=3
                    )
                ),
            ]
        )
        sc = Scanner(reader=ListReader(['ABC.txt', 3, True, 'XYZ', 0.123]))
        arguments = tmpl.read(template.list_parameters(), scanner=sc)
        assert arguments['codeFile'].name == 'ABC.txt'
        assert arguments['sleeptime'] == 3
        assert arguments['verbose']
        assert arguments['outputType'] == 'XYZ'
        assert arguments['frac'] == 0.123
