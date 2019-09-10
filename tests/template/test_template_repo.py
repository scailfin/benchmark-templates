# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test functionality of the template repository."""

import git
import os
import pytest
import sqlite3

from robtmpl.config.install import DB
from robtmpl.core.db.driver import DatabaseDriver
from robtmpl.template.repo.base import TemplateRepository
from robtmpl.template.repo.fs import TemplateFSRepository

import robtmpl.config.base as config
import robtmpl.core.error as err
import robtmpl.core.db.driver as driver
import robtmpl.template.schema as schema


DIR = os.path.dirname(os.path.realpath(__file__))
# Directory containing the template specification
TEMPLATE_DIR = os.path.join(DIR, '../.files/template')
# Alternative template specification files
ALT_TEMPLATE = os.path.join(TEMPLATE_DIR, 'alt-template.yaml')
ALT_TEMPLATE_ERROR = os.path.join(TEMPLATE_DIR, 'alt-validate-error.yaml')
# Valid benchmark template
BENCHMARK = 'ABCDEFGH'
DEFAULT_NAME = 'benchmark.json'


class DummyIDFunc():
    """Dummy id function."""
    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1
        return '0000'


class TestTemplateRepository(object):
    """Test functionality of abstract template repository."""
    def test_abstract_methods(self, tmpdir):
        """Test abstract methods for completeness."""
        repo = TemplateRepository()
        with pytest.raises(NotImplementedError):
            repo.add_template('unknown')
        with pytest.raises(NotImplementedError):
            repo.delete_template('unknown')
        with pytest.raises(NotImplementedError):
            repo.exists_template('unknown')
        with pytest.raises(NotImplementedError):
            repo.get_template('unknown')
        with pytest.raises(NotImplementedError):
            repo.list_templates()
        with pytest.raises(NotImplementedError):
            repo.get_unique_identifier()


class TestTemplateFSRepository(object):
    """Test functionality of the default benchmark repository."""
    def init_db(self, base_dir):
        """Initialize the database and return an open connection."""
        # The connect string references a new database file in the tmpdir
        connect_string = '{}/{}'.format(str(base_dir), config.DEFAULT_DATABASE)
        # Create a new empty database
        dbms_id = driver.SQLITE[0]
        DB.init(dbms_id=dbms_id, connect_string=connect_string)
        db = DatabaseDriver.get_connector(
            dbms_id=dbms_id,
            connect_string=connect_string
        )
        # Set environment variables to allow connecting without con parameter
        os.environ[config.ROB_DB_ID] = driver.SQLITE[0]
        os.environ[config.ROB_DB_CONNECT] = connect_string
        # Return open database connections
        return db.connect()

    def test_add_template(self, tmpdir):
        """Test creating templates."""
        con = self.init_db(base_dir=str(tmpdir))
        repo = TemplateFSRepository(base_dir=str(tmpdir), con=con)
        template = repo.add_template(name='My Template', src_dir=TEMPLATE_DIR)
        # Validate the template handle
        assert not template.identifier is None
        assert template.name == 'My Template'
        assert template.has_schema()
        assert template.workflow_spec['inputs']['files'] == ['$[[code]]', '$[[names]]']
        assert len(template.parameters) == 4
        assert not template.has_description()
        assert template.get_description() == ''
        assert not template.has_instructions()
        assert template.get_instructions() == ''
        # Make sure files are being copied
        template_dir = repo.get_static_dir(template.identifier)
        assert os.path.isfile(os.path.join(template_dir, 'code/helloworld.py'))
        assert os.path.isfile(os.path.join(template_dir, 'inputs/names.txt'))
        # Force error by overriding the list of default file names
        repo = TemplateFSRepository(
            base_dir=str(tmpdir),
            con=con,
            store=repo.store,
            default_filenames=['ABC']
        )
        with pytest.raises(err.InvalidTemplateError):
            repo.add_template(name='Next Template', src_dir=TEMPLATE_DIR)
        # Alternative specification file
        template = repo.add_template(
            name='Alt Template',
            description='desc',
            instructions='instr',
            src_dir=TEMPLATE_DIR,
            template_spec_file=ALT_TEMPLATE
        )
        assert template.name == 'Alt Template'
        assert template.has_description()
        assert template.get_description() == 'desc'
        assert template.has_instructions()
        assert template.get_instructions() == 'instr'
        assert not template.has_schema()
        with pytest.raises(err.UnknownParameterError):
            repo.add_template(
                name='Alt Template Err',
                src_dir=TEMPLATE_DIR,
                template_spec_file=ALT_TEMPLATE_ERROR
            )
        # Test error conditions
        with pytest.raises(ValueError):
            # No source given
            repo.add_template(name='Alt Template Err')
        with pytest.raises(ValueError):
            # Two sources given
            repo.add_template(
                name='Alt Template Err',
                src_dir='dev/null',
                src_repo_url='/dev/null'
            )
        with pytest.raises(err.ROBError):
            # Empty name
            repo.add_template(name=None, src_dir=TEMPLATE_DIR)
        with pytest.raises(err.ROBError):
            # Missing name
            repo.add_template(name='', src_dir=TEMPLATE_DIR)
        with pytest.raises(git.exc.GitCommandError):
            # Invalid git repository
            repo.add_template(
                name='Alt Template Err',
                src_repo_url='/dev/null'
            )

    def test_delete_template(self, tmpdir):
        """Test deleting templates."""
        con = self.init_db(base_dir=str(tmpdir))
        repo = TemplateFSRepository(base_dir=str(tmpdir), con=con)
        template1 = repo.add_template(name='Template 1', src_dir=TEMPLATE_DIR)
        template2 = repo.add_template(name='Template 2', src_dir=TEMPLATE_DIR)
        assert len(repo.list_templates()) == 2
        assert repo.delete_template(template1.identifier)
        assert not repo.delete_template(template1.identifier)
        templates = repo.list_templates()
        assert len(templates) == 1
        assert template2.identifier == templates[0].identifier
        assert repo.delete_template(template2.identifier)
        assert len(repo.list_templates()) == 0
        repo = TemplateFSRepository(base_dir=str(tmpdir), con=con)
        assert len(repo.list_templates()) == 0

    def test_error_for_id_func(self, tmpdir):
        """Error when the id function cannot return unique folder identifier."""
        dummy_func = DummyIDFunc()
        con = self.init_db(base_dir=str(tmpdir))
        repo = TemplateFSRepository(base_dir=str(tmpdir), id_func=dummy_func)
        repo.add_template(name='Template 1', src_dir=TEMPLATE_DIR)
        with pytest.raises(RuntimeError):
            repo.add_template(name='Template 2', src_dir=TEMPLATE_DIR)
        assert dummy_func.count == 102

    def test_get_template(self, tmpdir):
        """Test adding and retrieving templates."""
        con = self.init_db(base_dir=str(tmpdir))
        repo = TemplateFSRepository(base_dir=str(tmpdir), con=con)
        template = repo.add_template(name='My Template', src_dir=TEMPLATE_DIR)
        assert template.name == 'My Template'
        assert template.has_schema()
        assert template.workflow_spec['inputs']['files'] == ['$[[code]]', '$[[names]]']
        assert len(template.parameters) == 4
        # Retrieve template and re-verify
        template = repo.get_template(template.identifier)
        assert template.name == 'My Template'
        assert template.has_schema()
        assert template.workflow_spec['inputs']['files'] == ['$[[code]]', '$[[names]]']
        assert len(template.parameters) == 4
        # Re-instantiate repository, retrieve template and re-verify
        repo = TemplateFSRepository(base_dir=str(tmpdir), con=con)
        template = repo.get_template(template.identifier)
        assert template.name == 'My Template'
        assert template.has_schema()
        assert template.workflow_spec['inputs']['files'] == ['$[[code]]', '$[[names]]']
        assert len(template.parameters) == 4
        # Error for unknown template
        with pytest.raises(err.UnknownTemplateError):
            repo.get_template('unknown')
        template = repo.get_template(template.identifier)
        repo.delete_template(template.identifier)
        with pytest.raises(err.UnknownTemplateError):
            repo.get_template(template.identifier)

    def test_list_templates(self, tmpdir):
        """Test creating and listing templates."""
        con = self.init_db(base_dir=str(tmpdir))
        repo = TemplateFSRepository(base_dir=str(tmpdir), con=con)
        template1 = repo.add_template(name='Template 1', src_dir=TEMPLATE_DIR)
        template2 = repo.add_template(name='Template 2', src_dir=TEMPLATE_DIR)
        with pytest.raises(err.ROBError):
            repo.add_template(name='Template 2', src_dir=TEMPLATE_DIR)
        with pytest.raises(err.ROBError):
            repo.add_template(name='T' * 300, src_dir=TEMPLATE_DIR)
        templates = repo.list_templates()
        assert len(templates) == 2
        ids = [t.identifier for t in templates]
        assert template1.identifier in ids
        assert template2.identifier in ids
        # Re-instantiate the repository
        repo = TemplateFSRepository(base_dir=str(tmpdir), store=repo.store)
        templates = repo.list_templates()
        assert len(templates) == 2
        ids = [t.identifier for t in templates]
        assert template1.identifier in ids
        assert template2.identifier in ids

    def test_result_schema(self, tmpdir):
        """Test creating result schema from template specification."""
        con = self.init_db(base_dir=str(tmpdir))
        repo = TemplateFSRepository(base_dir=str(tmpdir), con=con)
        template = repo.add_template(name='My Template', src_dir=TEMPLATE_DIR)
        # Create the result table
        res_table = 'res_' + template.identifier
        schema.create_result_table(
            con,
            res_table,
            template.get_schema()
        )
        # The table schould contain four columns. Only column 2 will accept NULL
        # values
        sql = "INSERT INTO {}(run_id, col1, col2, col3) VALUES('A', 0, 1.2, 'A')"
        con.execute(sql.format(res_table))
        sql = "INSERT INTO {}(run_id, col1, col3) VALUES('B', 0, 'A')"
        con.execute(sql.format(res_table))
        con.commit()
        with pytest.raises(sqlite3.IntegrityError):
            sql = "INSERT INTO {}(run_id, col3) VALUES('C', 'A')"
            con.execute(sql.format(res_table))
        rs = con.execute('SELECT * FROM {}'.format(res_table)).fetchall()
        assert len(rs) == 2
