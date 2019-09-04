# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

import os

from robtmpl.core.db.base import DatabaseConnector

import robtmpl.core.util as util


class SQLiteConnector(DatabaseConnector):
    """Database connector for SQLite3 databases."""
    def __init__(self, connect_string):
        """Connect to the given SQLite3 database file.

        Parameters
        ----------
        connect_string: string
            The connect string is the name of the file that contains the
            database.

        Returns
        -------
        DB-API 2.0 database connection
        """
        # Set the connect string and ensure that the directory for the database
        # file exists. Create parent directories if necessary.
        self.connect_string = os.path.abspath(connect_string)
        util.create_dir(os.path.dirname(self.connect_string))

    def connect(self):
        """Connect to the SQLite3 database file that is specified in the
        internal connection string.

        Returns
        -------
        DB-API 2.0 database connection
        """
        import sqlite3
        con = sqlite3.connect(
            self.connect_string,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        con.row_factory = sqlite3.Row
        return con

    def info(self, indent=''):
        """Get information about the underlying database.

        Parameters
        ----------
        indent: string, optional
             Optional indent when printing information string

        Returns
        -------
        string
        """
        return indent + 'sqlite3 {}'.format(self.connect_string)

    def init_db(self, schema_file):
        """Initialize the database by executing a given SQL script to create
        a clean initial version of the database tables and views.

        Parameters
        ----------
        schema_file: string
            Path to the file containing the statements to create database tables
        """
        with self.connect() as con:
            with open(schema_file) as f:
                con.executescript(f.read())
