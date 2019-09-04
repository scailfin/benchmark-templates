# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test functionality of the template for benchmark specifications and the
template loader.
"""

import os
import pytest

from robtmpl.benchmark.loader import BenchmarkTemplateLoader

import robtmpl.core.error as err


DIR = os.path.dirname(str(os.path.realpath(__file__)))
TEMPLATE_FILE_1 = os.path.join(DIR, '../.files/benchmark/template_1.yaml')
TEMPLATE_FILE_ERR_1 = os.path.join(DIR, '../.files/benchmark/template_2.yaml')
TEMPLATE_FILE_ERR_2 = os.path.join(DIR, '../.files/benchmark/template_3.yaml')
TEMPLATE_FILE_ERR_3 = os.path.join(DIR, '../.files/template/template.yaml')


class TestBenchmarkLoader(object):
    """Test benchmark template serialization and the template loader."""
    def test_load_from_file(self):
        """Test loading benchmark templates from a valid and invalid template
        files.
        """
        loader = BenchmarkTemplateLoader()
        template = loader.load(TEMPLATE_FILE_1)
        assert len(template.parameters) == 3
        for key in ['names', 'sleeptime', 'greeting']:
            assert key in template.parameters
        assert len(template.schema.columns) == 3
        # Test error cases
        with pytest.raises(err.InvalidTemplateError):
            loader.load(TEMPLATE_FILE_ERR_1)
        with pytest.raises(err.InvalidTemplateError):
            loader.load(TEMPLATE_FILE_ERR_2)
        # A plain template file without schema information will also raise
        # an error when using the benchmark loader
        with pytest.raises(err.InvalidTemplateError):
            loader.load(TEMPLATE_FILE_ERR_3)

    def test_template_serialization(self):
        """Test template serialization."""
        loader = BenchmarkTemplateLoader()
        template = loader.load(TEMPLATE_FILE_1)
        tmpl_ser = loader.from_dict(
            loader.to_dict(template),
            identifier=template.identifier,
            base_dir=template.base_dir
        )
        assert template.identifier == tmpl_ser.identifier
        assert template.base_dir == tmpl_ser.base_dir
        assert len(tmpl_ser.parameters) == 3
        for key in ['names', 'sleeptime', 'greeting']:
            assert key in tmpl_ser.parameters
        assert len(tmpl_ser.schema.columns) == 3
