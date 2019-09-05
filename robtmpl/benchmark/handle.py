# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Extended workflow template for data analytics benchmarks. The benchmark
template extends the base template with one element that contains the
specification for the benchmark result.

The assumption is that the workflow for the benchmark contains one step that
generates a result file. This file is expected to contain a JSON or YAML object
with the summarized results for the benchmark workflow run. These results are
used to generate the overall benchmark leaderboard.

The structure of the benchmark result element is defined in the schema module.
"""

"""Prefix for all benchmark result tables. The table name is a concatenation of
the prefix and the template identifier.
"""
PREFIX_RESULT_TABLE = 'bm_'

class TemplateHandle(object):
    """The basic information for benchmarks in listings contains the unique
    identifier, name, an optional short description, and an optional set of
    instructions.

    Both, the identifier and the name of a benchmark ar unique. The name is
    used to identify the benchmark in listings that are visible to the user.
    """
    def __init__(self, identifier, name, description=None, instructions=None):
        """Initialize the descriptor attributes.

        Parameters
        ----------
        identifier: string
            Unique benchmark identifier
        name: string
            Unique benchmark name
        description: string, optional
            Optional short description for display in benchmark listings
        instructions: string, optional
            Text containing detailed instructions for benchmark participants
        """
        self.identifier = identifier
        self.name = name
        self.description = description
        self.instructions = instructions

    def has_description(self):
        """Shortcut to test of the description attribute is set.

        Returns
        -------
        bool
        """
        return not self.description is None

    def has_instructions(self):
        """Test if the instructions for the benchmark are set.

        Returns
        -------
        bool
        """
        return not self.instructions is None


class TemplateHandle(object):
    """The benchmark handle extends the descriptor with a reference to the
    associated workflow template.

    The basic information for benchmarks in listings contains the unique
    identifier, name, an optional short description, and an optional set of
    instructions.

    Both, the identifier and the name of a benchmark ar unique. The name is
    used to identify the benchmark in listings that are visible to the user.
    """
    def __init__(self, con, template, name, description=None, instructions=None):
        """Initialize the descriptor attributes and the reference to the
        workflow template.

        Parameters
        ----------
        con: DB-API 2.0 database connection
            Connection to underlying database
        template: benchtmpl.workflow.benchmark.base.BenchmarkTemplate
            Handle for the associated workflow template. The identifier for the
            benchmark is inherited from the template identifier.
        name: string
            Unique benchmark name
        description: string, optional
            Optional short description for display in benchmark listings
        instructions: string, optional
            Text containing detailed instructions for benchmark participants
        """
        self.identifier = identifier
        self.name = name
        self.description = description
        self.instructions = instructions
        self.con = con
        self.template = template
        # The result table name is the concatenation of the common prefix and
        # the benchmark identifier
        self.result_table_name = PREFIX_RESULT_TABLE + self.identifier

    def create_result_table(self):
        """Create table to store benchmark results bases on the benchmark schema
        specification.
        """
        cols = list(['run_id  CHAR(32) NOT NULL'])
        for col in self.template.schema.columns:
            cols.append(col.sql_stmt())
        sql = 'CREATE TABLE {}({}, PRIMARY KEY(run_id))'
        self.con.execute(sql.format(self.result_table_name, ','.join(cols)))
        self.con.commit()

    def get_leaderboard(self, sort_key=None, all_entries=False):
        """Get current leaderboard for the benchmark. The result is a list of
        leaderboard entries. Each entry contains the user and the run results.
        If the all_entries flag is False at most one result per user is added
        to the result.

        Parameters
        ----------
        sort_key: string, optional
            Use the given attribute to sort run results. If not given the schema
            default attribute is used
        all_entries: bool, optional
            Include at most one entry per user in the result if False

        Returns
        -------
        list(benchengine.benchmark.base.LeaderboardEntry)
        """
        # Create list of result columns for SELECT clause and get the attribute
        # that is used to sort the result
        cols = list()
        sort_stmt = None
        for col in self.template.schema.columns:
            if col.is_default:
                cols.insert(0, col)
                if sort_key is None:
                    sort_stmt = col.sort_statement()
            else:
                cols.append(col)
                if not sort_key is None and col.identifier == sort_key:
                    sort_stmt = col.sort_statement()
        col_names = list()
        for col in cols:
            col_names.append('r.{}'.format(col.identifier))
        # Use the first column as the sort column if no default is specified in
        # the schema.
        if sort_stmt is None:
            sort_stmt = self.template.schema.columns[0].sort_statement()
        # Query the database to get the ordered list or benchmark run results
        sql = 'SELECT u.id, u.email, {} '.format(','.join(col_names))
        sql += 'FROM registered_user u, benchmark_run b, '
        sql += '{} r '.format(self.result_table_name)
        sql += 'WHERE u.id = b.user_id AND b.run_id = r.run_id '
        sql += 'ORDER BY {}'.format(sort_stmt)
        rs = self.con.execute(sql).fetchall()
        # Keep track of users for which we have results (only needed if the
        # all_entries flag is False)
        users = set()
        leaderboard = list()
        for row in rs:
            user = RegisteredUser(identifier=row[0], email=row[1])
            if user.identifier in users and not all_entries:
                continue
            users.add(user.identifier)
            result = dict()
            for i in range(len(cols)):
                col = cols[i]
                result[col.identifier] = row[i + 2]
            leaderboard.append(LeaderboardEntry(user=user, results=result))
        return leaderboard

    def has_description(self):
        """Shortcut to test of the description attribute is set.

        Returns
        -------
        bool
        """
        return not self.description is None

    def has_instructions(self):
        """Test if the instructions for the benchmark are set.

        Returns
        -------
        bool
        """
        return not self.instructions is None

    def insert_results(self, run_id, results):
        """Insert the results of a benchmark run into the results table. Expects
        a dictionary that contains result values for all mandatory results.

        Parameters
        ----------
        run_id: string
            Unique run identifier
        results: dict
                Dictionary containing run result values

        Raises
        ------
        benchengine.error.ROBError
        """
        columns = list(['run_id'])
        values = list([run_id])
        for col in self.template.schema.columns:
            if col.identifier in results:
                values.append(results[col.identifier])
            elif col.required:
                raise err.ROBError('missing result for \'{}\''.format(col.identifier))
            else:
                values.append(None)
            columns.append(col.identifier)
        sql = 'INSERT INTO {}({}) VALUES({})'.format(
            self.result_table_name,
            ','.join(columns),
            ','.join(['?'] * len(columns))
        )
        self.con.execute(sql, values)
        self.con.commit()


class LeaderboardEntry(object):
    """Entry in the leaderboard for a benchmark. Each entry contains a reference
    to the user that submitted the run and a dictionary containing the run
    results.
    """
    def __init__(self, user, results):
        """Initialize the components of the leaderboard entry.

        Parameters
        ----------
        user: benchengine.user.base.RegisteredUser
            User that submitted the benchmark run
        result: dict
            Dictionary of run results. The result values are keyed by the column
            identifier from the benchmark schema.
        """
        self.user = user
        self.results = results
