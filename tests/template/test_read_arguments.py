# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test read arguments function for REANA templates."""

import pytest

from robtmpl.io.scanner import Scanner, ListReader
from robtmpl.template.parameter.base import TemplateParameter, AS_INPUT
from robtmpl.template.base import WorkflowTemplate

import robtmpl.template.parameter.declaration as pd
import robtmpl.template.parameter.util as tmpl


class TestReadTemplateArguments(object):
    def test_read_with_record(self):
        """Read argument for a template that contains a parameter of data type
        DT_RECORD.
        """
        template = WorkflowTemplate(
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='codeFile',
                        data_type=pd.DT_FILE,
                        index=0,
                        default_value=None,
                        as_const=AS_INPUT
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='dataFile',
                        data_type=pd.DT_FILE,
                        index=1,
                        default_value='data/names.txt'
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='resultFile',
                        data_type=pd.DT_FILE,
                        index=2,
                        default_value=None
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='sleeptime',
                        data_type=pd.DT_INTEGER,
                        index=3,
                        default_value=10
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='verbose',
                        data_type=pd.DT_BOOL,
                        index=4,
                        default_value=False
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='frac',
                        data_type=pd.DT_DECIMAL,
                        index=6
                    )
                ),
                TemplateParameter(
                    pd.parameter_declaration(
                        identifier='outputType',
                        index=5
                    )
                ),
            ]
        )
        sc = Scanner(reader=ListReader([
            'ABC.txt',
            'code/abc.py',
            '',
            'result/output.txt',
            'skip this error',
            3,
            True,
            'XYZ',
            0.123
        ]))
        arguments = tmpl.read(template.list_parameters(), scanner=sc)
        assert arguments['codeFile'].name == 'ABC.txt'
        assert arguments['codeFile'].target_path == 'code/abc.py'
        assert arguments['dataFile'].name == 'names.txt'
        assert arguments['dataFile'].target_path is None
        assert arguments['resultFile'].name == 'output.txt'
        assert arguments['resultFile'].target_path is None
        assert arguments['sleeptime'] == 3
        assert arguments['verbose']
        assert arguments['outputType'] == 'XYZ'
        assert arguments['frac'] == 0.123
