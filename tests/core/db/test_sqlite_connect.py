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

from robtmpl.core.db.sqlite import SQLiteConnector

DIR = os.path.dirname(os.path.realpath(__file__))
SCHEMA_FILE = os.path.join(DIR, '../../.files/db/testdb.sql')


class TestSQLiteConnector(object):
    """Unit tests for the SQLite database connector to test the connect() and
    init_db() methods.
    """
    def test_create_db(self, tmpdir):
        """test connectimg to a database and executing a script."""
        # The connect string references a new database file in the tmpdir
        connect_string = '{}/my.db'.format(str(tmpdir))
        # Create a new empty database
        db = SQLiteConnector(connect_string=connect_string)
        db.init_db(schema_file=SCHEMA_FILE)
        with db.connect() as con:
            rs = con.execute('SELECT * FROM user').fetchall()
            assert len(rs) == 2
            assert rs[0]['name'] == 'Alice'
            assert rs[0]['age'] == 30
            assert rs[1]['name'] == 'Bob'
            assert rs[1]['age'] == 25
