# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test functionality of the template base module."""

import os
import pytest

from robtmpl.core.io.files.base import FileHandle
from robtmpl.template.parameter.base import TemplateParameter
from robtmpl.template.parameter.value import TemplateArgument
from robtmpl.workflow.resource.base import ResourceDescriptor, LABEL_ID
from robtmpl.template.base import WorkflowTemplate

import robtmpl.core.error as err
import robtmpl.core.util as util
import robtmpl.template.parameter.declaration as pd
import robtmpl.template.base as tmpl
import robtmpl.template.util as tmplutil


DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_JSON_FILE = os.path.join(DIR, '../.files/template/template.json')
TEMPLATE_YAML_FILE = os.path.join(DIR, '../.files/template/template.yaml')


class TestWorkflowTemplate(object):
    """Unit tests for classes and methods in the template base module."""
    def test_get_parameter_references(self):
        """Test function to get all parameter references in a workflow
        specification.
        """
        spec = {
            'input': [
                'A',
                '$[[X]]',
                {'B': {'C': '$[[Y]]', 'D': [123, '$[[Z]]']}}
            ],
            'E': {'E': 'XYZ', 'F': 23, 'G': '$[[W]]'},
            'F': '$[[U]]',
            'G': ['$[[V]]', 123]
        }
        refs = tmplutil.get_parameter_references(spec)
        assert refs == set(['U', 'V', 'W', 'X', 'Y', 'Z'])
        # If given parameter set as argument the elements in that set are part
        # of the result
        para = set(['A', 'B', 'X'])
        refs = tmplutil.get_parameter_references(spec, parameters=para)
        assert refs == set(['A', 'B', 'U', 'V', 'W', 'X', 'Y', 'Z'])
        # Error if specification contains nested lists
        with pytest.raises(err.InvalidTemplateError):
            tmplutil.get_parameter_references({
                'input': [
                    'A',
                    ['$[[X]]'],
                    {'B': {'C': '$[[Y]]', 'D': [123, '$[[Z]]']}}
                ]
            })

    def test_init(self):
        """Test initialization of attributes and error cases when creating
        template instances.
        """
        template = WorkflowTemplate(
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(pd.parameter_declaration('A')),
                TemplateParameter(pd.parameter_declaration('B'))
            ]
        )
        assert not template.identifier is None
        template = WorkflowTemplate(
            identifier='ABC',
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(pd.parameter_declaration('A')),
                TemplateParameter(pd.parameter_declaration('B'))
            ]
        )
        assert template.identifier == 'ABC'
        with pytest.raises(err.InvalidTemplateError):
            WorkflowTemplate(
                workflow_spec=dict(),
                parameters=[
                    TemplateParameter(pd.parameter_declaration('A')),
                    TemplateParameter(pd.parameter_declaration('B')),
                    TemplateParameter(pd.parameter_declaration('A'))
                ]
            )

    def test_nested_parameters(self):
        """Test proper nesting of parameters for DT_LIST and DT_RECORD."""
        # Create a new WorkflowTemplate with an empty workflow specification and
        # a list of six parameters (one record and one list)
        template = WorkflowTemplate.from_dict({
                tmpl.LABEL_WORKFLOW: dict(),
                tmpl.LABEL_PARAMETERS: [
                    pd.parameter_declaration('A'),
                    pd.parameter_declaration('B', data_type=pd.DT_RECORD),
                    pd.parameter_declaration('C', parent='B'),
                    pd.parameter_declaration('D', parent='B'),
                    pd.parameter_declaration('E', data_type=pd.DT_LIST),
                    pd.parameter_declaration('F', parent='E'),
                ]
            },
            validate=True
        )
        # Parameters 'A', 'C', 'D', and 'F' have no children
        for key in ['A', 'C', 'D', 'F']:
            assert not template.get_parameter(key).has_children()
        # Parameter 'B' has two children 'C' and 'D'
        b = template.get_parameter('B')
        assert b.has_children()
        assert len(b.children) == 2
        assert 'C' in [p.identifier for p in b.children]
        assert 'D' in [p.identifier for p in b.children]
        # Parameter 'E' has one childr 'F'
        e = template.get_parameter('E')
        assert e.has_children()
        assert len(e.children) == 1
        assert 'F' in [p.identifier for p in e.children]

    def test_simple_replace(self):
        """Replace parameter references in simple template with argument values.
        """
        for filename in [TEMPLATE_YAML_FILE, TEMPLATE_JSON_FILE]:
            template = WorkflowTemplate.from_dict(util.read_object(filename))
            arguments = {
                'code': TemplateArgument(
                    parameter=template.get_parameter('code'),
                    value=FileHandle('code/helloworld.py')
                ),
                'names': TemplateArgument(
                    parameter=template.get_parameter('names'),
                    value=FileHandle('data/list-of-names.txt')
                ),
                'sleeptime': TemplateArgument(
                    parameter=template.get_parameter('sleeptime'),
                    value=10
                )
            }
            spec = tmplutil.replace_args(
                spec=template.workflow_spec,
                arguments=arguments,
                parameters=template.parameters
            )
            assert spec['inputs']['files'][0] == 'helloworld.py'
            assert spec['inputs']['files'][1] == 'data/names.txt'
            assert spec['inputs']['parameters']['helloworld'] == 'code/helloworld.py'
            assert spec['inputs']['parameters']['inputfile'] == 'data/names.txt'
            assert spec['inputs']['parameters']['sleeptime'] == 10
            assert spec['inputs']['parameters']['waittime'] == 5

    def test_sort(self):
        """Test the sort functionality of the template list_parameters method.
        """
        # Create a new WorkflowTemplate with an empty workflow specification and
        # a list of five parameters
        template = WorkflowTemplate.from_dict({
                tmpl.LABEL_WORKFLOW: dict(),
                tmpl.LABEL_PARAMETERS: [
                    pd.parameter_declaration('A', index=1),
                    pd.parameter_declaration('B'),
                    pd.parameter_declaration('C'),
                    pd.parameter_declaration('D', index=2),
                    pd.parameter_declaration('E', index=1)
                ]
            },
            validate=True
        )
        # Get list of sorted parameter identifier from listing
        keys = [p.identifier for p in template.list_parameters()]
        assert keys == ['B', 'C', 'A', 'E', 'D']
