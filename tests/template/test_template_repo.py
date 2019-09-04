# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test functionality of the default template repository implementation."""

import os
import pytest

from robtmpl.template.base import TemplateHandle
from robtmpl.template.loader import DefaultTemplateLoader
from robtmpl.template.repo import TemplateRepository
from robtmpl.template.repo import STATIC_FILES_DIR, TEMPLATE_FILE

import robtmpl.core.error as err


DIR = os.path.dirname(os.path.realpath(__file__))
ERR_SPEC = os.path.join(DIR, '../.files/template-error-1.yaml')
JSON_SPEC = os.path.join(DIR, '../.files/template/reana-template.json')
WORKFLOW_DIR = os.path.join(DIR, '../.files/template')


class DummyIDFunc():
    """Dummy id function."""
    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1
        return '0000'


class TestTemplateRepository(object):
    """Test functionality of default template repository."""
    def test_add_template(self, tmpdir):
        """Test creating templates."""
        store = TemplateRepository(base_dir=str(tmpdir))
        template = store.add_template(src_dir=WORKFLOW_DIR)
        self.validate_template_handle(template)
        # Ensure that the template handle has been serialized correctly
        f = os.path.join(store.base_dir, template.identifier, TEMPLATE_FILE)
        doc = DefaultTemplateLoader().load(f)
        d = os.path.join(store.base_dir, template.identifier, STATIC_FILES_DIR)
        assert os.path.isdir(d)
        # Get template and repeat tests
        self.validate_template_handle(store.get_template(template.identifier))
        store = TemplateRepository(base_dir=str(tmpdir))
        self.validate_template_handle(store.get_template(template.identifier))
        # Add template with JSON specification file
        template = store.add_template(
            src_dir=WORKFLOW_DIR,
            template_spec_file=JSON_SPEC
        )
        self.validate_template_handle(template)
        # Unknown template error
        with pytest.raises(err.UnknownTemplateError):
            store.get_template('unknown')
        # Errors when specifying wrong parameter combination
        with pytest.raises(ValueError):
            store.add_template()
        with pytest.raises(ValueError):
            store.add_template(src_dir=WORKFLOW_DIR, src_repo_url=WORKFLOW_DIR)
        # Load templates with erroneous specifications
        with pytest.raises(err.InvalidTemplateError):
            store.add_template(src_dir=WORKFLOW_DIR, template_spec_file=ERR_SPEC)
        # Error when cloning invalid repository from GitHub
        with pytest.raises(err.InvalidTemplateError):
            store.add_template(src_repo_url='https://github.com/reanahub/reana-demo-helloworld')

    def test_delete_template(self, tmpdir):
        """Ensure correct return values when deleting existing and non-existing
        templates.
        """
        store = TemplateRepository(base_dir=str(tmpdir))
        template = store.add_template(src_dir=WORKFLOW_DIR)
        f = os.path.join(store.base_dir, template.identifier, TEMPLATE_FILE)
        d = os.path.join(store.base_dir, template.identifier, STATIC_FILES_DIR)
        assert os.path.isfile(f)
        assert os.path.isdir(d)
        assert store.delete_template(template.identifier)
        assert not os.path.isfile(f)
        assert not os.path.isdir(d)
        assert not store.delete_template(template.identifier)
        # Test deleting after store object is re-instantiated
        template = store.add_template(src_dir=WORKFLOW_DIR)
        store = TemplateRepository(base_dir=str(tmpdir))
        assert store.delete_template(template.identifier)
        assert not store.delete_template(template.identifier)

    def test_error_for_id_func(self, tmpdir):
        """Error when the id function cannot return unique folder identifier."""
        dummy_func = DummyIDFunc()
        store = TemplateRepository(base_dir=os.path.join(str(tmpdir)), id_func=dummy_func)
        os.makedirs(os.path.join(store.base_dir, dummy_func()))
        with pytest.raises(RuntimeError):
            store.add_template(src_dir=WORKFLOW_DIR)
        assert dummy_func.count == 102

    def validate_template_handle(self, template):
        """Basic tests to validate a given template handle."""
        assert not template.identifier is None
        assert not template.base_dir is None
        assert template.workflow_spec['inputs']['files'] == ['$[[code]]', '$[[names]]']
        assert len(template.parameters) == 4
        assert os.path.isfile(os.path.join(template.base_dir, 'code/helloworld.py'))
        assert os.path.isfile(os.path.join(template.base_dir, 'inputs/names.txt'))
