# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the database driver."""

import os
import pytest

from robtmpl.core.db.driver import DatabaseDriver as DB

import robtmpl.config.base as config


class TestDatabaseDriver(object):
    """Collection of unit tests for the database driver."""
    def test_connect_sqlite(self, tmpdir):
        """Test instantiating database connectors."""
        # SQLite
        f_name = '/tmp/test.db'
        os.environ[config.ROB_DB_ID] = 'SQLITE'
        os.environ[config.ROB_DB_CONNECT] = f_name
        db = DB.get_connector()
        assert db.info(indent='..') == '..sqlite3 {}'.format(f_name)
        f_name ='/tmp/test.sqlite3.db'
        db = DB.get_connector(dbms_id='SQLITE3', connect_string=f_name)
        assert db.info(indent='..') == '..sqlite3 {}'.format(f_name)
        # PostgreSQL
        connect = 'localhost:5678/mydb:myuser/the/pwd'
        os.environ[config.ROB_DB_ID] = 'POSTGRES'
        os.environ[config.ROB_DB_CONNECT] = connect
        db = DB.get_connector()
        assert db.info() == 'postgres {} on {}'.format('mydb', 'localhost:5678')
        assert db.user == 'myuser'
        assert db.password == 'the/pwd'
        db = DB.get_connector(connect_string='localhost/db:user/some:pwd')
        assert db.info() == 'postgres {} on {}'.format('db', 'localhost')
        assert db.user == 'user'
        assert db.password == 'some:pwd'
        # Unknown database identifier
        with pytest.raises(ValueError):
            DB.get_connector(dbms_id='unknown', connect_string='CONNECT ME')
