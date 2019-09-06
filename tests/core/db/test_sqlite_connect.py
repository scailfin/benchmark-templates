# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the SQLite database connector."""

import os
import pytest

from robtmpl.config.install import DB
from robtmpl.core.db.driver import DatabaseDriver

import robtmpl.config.base as config
import robtmpl.core.db.driver as driver


DIR = os.path.dirname(os.path.realpath(__file__))
DML_FILE = os.path.join(DIR, '../../.files/db/testdb.sql')


class TestSQLiteConnector(object):
    """Unit tests for the SQLite database connector to test the connect() and
    init_db() methods.
    """
    def test_create_db(self, tmpdir):
        """Use the database driver init_db method to test connecting to a SQLite
        database and executing a script.
        """
        # The connect string references a new database file in the tmpdir
        connect_string = '{}/{}'.format(str(tmpdir), config.DEFAULT_DATABASE)
        # Create a new empty database
        dbms_id = driver.SQLITE[0]
        DB.init(dbms_id=dbms_id, connect_string=connect_string)
        db = DatabaseDriver.get_connector(
            dbms_id=dbms_id,
            connect_string=connect_string
        )
        db.execute(DML_FILE)
        with db.connect() as con:
            rs = con.execute('SELECT * FROM template').fetchall()
            assert len(rs) == 2
            assert rs[0]['id'] == '1234'
            assert rs[0]['name'] == 'Alice'
            assert rs[1]['id'] == '5678'
            assert rs[1]['name'] == 'Bob'
