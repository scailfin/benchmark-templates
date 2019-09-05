# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test functionality of the template store implementations."""

import os
import pytest

from robtmpl.template.parameter.base import TemplateParameter
from robtmpl.workflow.resource.base import ResourceDescriptor, LABEL_ID
from robtmpl.template.base import WorkflowTemplate
from robtmpl.template.io.json import JsonFileStore

import robtmpl.core.error as err
import robtmpl.template.parameter.declaration as pd


DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.join(DIR, '../.files/benchmark')
# Valid benchmark template
BENCHMARK = 'ABCDEFGH'
DEFAULT_NAME = 'benchmark.json'
# Benchmark templates with errors
BENCHMARK_ERR_1 = 'ERROR2'
BENCHMARK_ERR_2 = 'ERROR3'
# Template with unknown parameters
TEMPLATE_ERR = 'ERROR1'


class TestJsonTemplateStore(object):
    """Unit tests to read and write workflow template file from and to disk using
    the Json template store.
    """
    def test_load_from_file(self):
        """Test loading benchmark templates from a valid and invalid template
        files.
        """
        # Loader with default file name
        loader = JsonFileStore(base_dir=BASE_DIR, default_file_name=DEFAULT_NAME)
        template = loader.read(BENCHMARK)
        assert template.identifier == BENCHMARK
        assert len(template.parameters) == 3
        for key in ['names', 'sleeptime', 'greeting']:
            assert key in template.parameters
        columns = [c.identifier for c in template.result_schema.columns]
        assert len(columns) == 4
        for key in ['col1', 'col2', 'col3', 'col4']:
            assert key in columns
        # Loader without default file name
        loader = JsonFileStore(base_dir=BASE_DIR)
        template = loader.read(BENCHMARK)
        assert template.identifier == BENCHMARK
        assert len(template.parameters) == 3
        for key in ['names', 'sleeptime', 'greeting']:
            assert key in template.parameters
        columns = [c.identifier for c in template.result_schema.columns]
        assert len(columns) == 3
        for key in ['col1', 'col2', 'col3']:
            assert key in columns
        # Test error cases
        with pytest.raises(err.InvalidTemplateError):
            loader.read(BENCHMARK_ERR_1)
        with pytest.raises(err.InvalidTemplateError):
            loader.read(BENCHMARK_ERR_2)
        # Error when loading unknown template
        with pytest.raises(err.UnknownTemplateError):
            loader.read('UNKNOWN')

    def test_serialize_benchmark(self):
        """Test benchmark template serialization."""
        loader = JsonFileStore(base_dir=BASE_DIR)
        template = loader.read(BENCHMARK)
        tmpl_ser = WorkflowTemplate.from_dict(
            template.to_dict(),
            identifier=template.identifier
        )
        assert template.identifier == tmpl_ser.identifier
        assert len(tmpl_ser.parameters) == 3
        for key in ['names', 'sleeptime', 'greeting']:
            assert key in tmpl_ser.parameters
        assert len(tmpl_ser.result_schema.columns) == 3

    def test_serialize_template(self):
        """Test serialization of workflow templates."""
        template = WorkflowTemplate(
            identifier='ABC',
            workflow_spec=dict(),
            parameters=[
                TemplateParameter(pd.parameter_declaration('A')),
                TemplateParameter(pd.parameter_declaration('B', data_type=pd.DT_LIST)),
                TemplateParameter(pd.parameter_declaration('C', parent='B'))
            ]
        )
        doc = template.to_dict()
        parameters = WorkflowTemplate.from_dict(doc).parameters
        assert len(parameters) == 3
        assert 'A' in parameters
        assert 'B' in parameters
        assert len(parameters['B'].children) == 1
        template = WorkflowTemplate.from_dict(doc)
        assert template.identifier == 'ABC'
        # The base directory is not materialized
        # Invalid resource descriptor serializations
        with pytest.raises(err.InvalidTemplateError):
            ResourceDescriptor.from_dict(dict())
        with pytest.raises(err.InvalidTemplateError):
            ResourceDescriptor.from_dict({LABEL_ID: 'A', 'noname': 'B'})

    def test_unknown_parameter(self):
        """Test for raised errors in templates that contain references to
        undefined parameters. This test ensures that the validate flag is True
        when the loader instantiates templates from dictionaries.
        """
        with pytest.raises(err.UnknownParameterError):
            template = JsonFileStore(base_dir=BASE_DIR).read(TEMPLATE_ERR)

    def test_write_template(self, tmpdir):
        """Test write method of the Json store."""
        loader = JsonFileStore(base_dir=BASE_DIR)
        template = loader.read(BENCHMARK)
        writer = JsonFileStore(base_dir=str(tmpdir))
        loader.write(template)
        template = loader.read(BENCHMARK)
        assert template.identifier == BENCHMARK
