# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""The database driver is a static class that is used to get an instance of a
connector object that provides connectivity to the database management system
that is being used by the application for data management.

The intent of the driver is to hide the specifics of connecting to different
database systems from the application. Instead, the database system and the
underlying database are specified using a unique database system identifier and
a system-specific connection string.

The database driver can be configured using the environment variables
ROB_DBMS and ROB_DBCONNECT
"""

import os
import pkg_resources

import robtmpl.core.config as config
import robtmpl.core.util as util


"""Default database system identifier."""
SQLITE = ['SQLITE', 'SQLITE3']
POSTGRES = ['POSTGRES', 'POSTGRESQL', 'PSQL', 'PG']


class DatabaseDriver(object):
    """The database driver instantiates objects that provide connectivity to
    the database that is used by the application. The driver provides access
    to different database management systems.
    """
    @staticmethod
    def get_connector(dbms_id=None, connect_string=None):
        """Get a connector object for the database management system that is
        being used by the application. The system and database are specified
        using the optional argument values. Missing argument values are filled
        in from the respective environment variables.

        The dbms-identifier is used to identify the database management system
        that is being used by the application. The driver currently supports two
        different systems with the following identifiers (as synonyms):

        SQLite3: SQLITE or SQLITE3
        PostgreSQL: POSTGRES, POSTGRESQL, PSQL, or PG

        The connect string is a database system specific string containing
        information that is used by the respective system's connect method to
        establish the connection.

        A ValueError is raised if an unknown database system identifier is
        given. The database system may raise additional errors if the connect
        string is invalid.

        Parameters
        ----------
        dbms_id: string
            Unique identifier for the database management system
        connect_string: string
            Database system specific information to establish a connection to
            an existing database

        Returns
        -------
        robtmpl.core.db.base.DatabaseConnector

        Raises
        ------
        ValueError
        """
        # If missing, set the database system identifier and connection string
        # using the values in the respective environment variables. Raises an
        # VallueError if either parameter is None
        if dbms_id is None:
            dbms_id = config.DB_IDENTIFIER(raise_error=True)
        if connect_string is None:
            connect_string = config.DB_CONNECT(raise_error=True)
        # Return the connector for the identified database management system.
        # Raises ValueError if the given identifier is unknown.
        if dbms_id.upper() in SQLITE:
            # -- SQLite database -----------------------------------------------
            from robtmpl.core.db.sqlite import SQLiteConnector
            return SQLiteConnector(connect_string=connect_string)
        elif dbms_id.upper() in POSTGRES:
            # -- PostgreSQL database -------------------------------------------
            from robtmpl.core.db.pg import PostgresConnector
            return PostgresConnector(connect_string=connect_string)
        else:
            raise ValueError('unknown database system \'{}\''.format(dbms_id))

    @staticmethod
    def init_db(dbms_id=None, connect_string=None):
        """Initialize the database from the schema definition files in the
        resources folder.

        Add names of files here if they contain DML or DDL statements that are
        to be executed when the database is initialized.

        The given parameters are used to establish the connection to the
        database.

        Parameters
        ----------
        dbms_id: string
            Unique identifier for the database management system
        connect_string: string
            Database system specific information to establish a connection to
            an existing database
        """
        # Add names of files here if they contain statements to be executed
        # when the database is initialized. Files are executed in the order
        # of the list.
        scripts = ['core/db/install/benchrepo.sql']
        # Get a database connector
        db = DatabaseDriver.get_connector(
            dbms_id=dbms_id,
            connect_string=connect_string
        )
        # Assumes that all script files are distributed as part of the current
        # package
        pkg_name = __package__.split('.')[0]
        # Execute the database scripts
        for script_file in scripts:
            db.execute(pkg_resources.resource_filename(pkg_name, script_file))
