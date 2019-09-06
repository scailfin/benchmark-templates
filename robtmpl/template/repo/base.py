# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Base classes and interfaces for template repositories. Contains the abstract
repository interface and the template handle that represents entries in a
repository.
"""

from abc import abstractmethod

import robtmpl.core.util as util


""" "Default value for max. attempts parameters."""
DEFAULT_MAX_ATTEMPTS = 100


class TemplateHandle(object):
    """The template handle represents workflow templates that are maintained in
    a template repository. With each entry in the repository a set of additional
    information is stored.

    The basic information for repository entries contains the unique template
    identifier, a unique name, an optional short description, and an optional
    set of instructions. Both, the identifier and the name of a template are
    expected to be unique. The name is used to identify the template in listings
    that are visible to the user.

    The workflow template itself may be loaded on demand to avoid having to
    read all information when listing all entries in a repository, for example.
    """
    def __init__(
        self, identifier, name, description=None, instructions=None,
        template=None, store=None
    ):
        """Initialize the handle properties and the reference to the workflow
        template.

        Raises a ValueError if both, the template and the store are None.

        Parameters
        ----------
        identifier: string
            Unique template identifier
        name: string
            Unique template name
        description: string, optional
            Optional short description for display in listings
        instructions: string, optional
            Text containing detailed instructions for benchmark participants
        template: robtmpl.template.base.WorkflowTemplate, optional
            Reference to the associated workflow template. The template may be
            None in which case it will be loaded on demand from the repository.
        store: robtmpl.template.io.base.TemplateStore, optional
            Reference to the template store that contains the workflow template.
            This reference is required to load the template on demand.

        Raises
        ------
        ValueError
        """
        # Raise ValueError if template and store are None
        if template is None and store is None:
            raise ValueError('no workflow template given')
        self.identifier = identifier
        self.name = name
        self.description = description
        self.instructions = instructions
        self.template = template
        self.store = store

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
        list(robtmpl.template.repo.base.BenchmarkResult)
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
            leaderboard.append(BenchmarkResult(user_name=user_name, submission_name=submission_name, result=result))
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

    def has_schema(self):
        """Test if the result schema is set.

        Returns
        -------
        bool
        """
        return not self.get_workflow_template().result_schema is None

    def get_workflow_template(self):
        """Access the associated template. The template is loaded on demand from
        the template store if it is None.

        Returns
        -------
        robtmpl.template.base.WorkflowTemplate
        """
        if self.template is None:
            self.template = self.store.read(self.identifier)
        return self.template

    def insert_results(self, run_id, result):
        """Insert the results of a benchmark run into the results table. Expects
        a dictionary that contains result values for all mandatory attributes in
        the result schema.

        Parameters
        ----------
        run_id: string
            Unique run identifier
        result: dict
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
                msg = 'missing result for \'{}\''.format(col.identifier)
                raise err.ROBError(msg)
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


class TemplateRepository(object):
    """The template repository maintains a set of workflow templates. For each
    workflow template a copy of the static files that are used as input in the
    workflow is maintained.

    In addition to workflow templates the results of individual template runs
    are maintained as well.
    """
    def __init__(self, id_func=None, max_attempts=DEFAULT_MAX_ATTEMPTS):
        """Initialize the identifier function that is used to generate unique
        template identifier. By default, short identifier are used.

        Parameters
        ----------
        id_func: func, optional
            Function to generate template folder identifier
        max_attempts: int, optional
            Maximum number of attempts to create a unique folder for a new
            workflow template
        """
        self.id_func = id_func if not id_func is None else util.get_short_identifier
        self.max_attempts = max_attempts

    @abstractmethod
    def add_template(
        self, name, description=None, instructions=None, src_dir=None,
        src_repo_url=None, template_spec_file=None
    ):
        """Create file and folder structure for a new workflow template. Assumes
        that either a workflow source directory or the Url of a remote Git
        repository is given.

        Each template is assigned a unique identifier. Creates a copy of the
        file structure for the static workflow template files.

        The source folder is expected to contain the template specification
        file. If the template_spec file is not given the method will look for a
        file from a default list of file names. If no template file is found in
        the source folder a ValueError is raised.

        Parameters
        ----------
        name: string
            Unique template name for display purposes
        description: string, optional
            Optional short description for display in listings
        instructions: string, optional
            Optional text containing detailed instructions for benchmark
            participants
        src_dir: string, optional
            Directory containing the workflow components, i.e., the fixed
            files and the template specification (optional).
        src_repo_url: string, optional
            Git repository that contains the the workflow components
        template_spec_file: string, optional
            Path to the workflow template specification file (absolute or
            relative to the workflow directory)

        Returns
        -------
        robtmpl.template.base.WorkflowTemplate

        Raises
        ------
        robtmpl.core.error.InvalidParameterError
        robtmpl.core.error.InvalidTemplateError
        ValueError
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_template(self, identifier):
        """Delete all resources that are associated with the given template.
        The result is True if the template existed and False otherwise.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        bool
        """
        raise NotImplementedError()

    @abstractmethod
    def exists_template(self, identifier):
        """Test if a template with the given identifier exists.

        Returns
        -------
        bool
        """
        raise NotImplementedError()

    @abstractmethod
    def get_template(self, identifier):
        """Get handle for the template with the given identifier.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        robtmpl.template.repo.base.TemplateHandle

        Raises
        ------
        robtmpl.core.error.UnknownTemplateError
        """
        raise NotImplementedError()

    def get_unique_identifier(self):
        """Create a new unique identifier for a workflow template.

        Returns
        -------
        string

        Raises
        ------
        ValueError
        """
        identifier = None
        attempt = 0
        while identifier is None:
            identifier = self.id_func()
            if self.exists_template(identifier):
                identifier = None
                attempt += 1
                if attempt > self.max_attempts:
                    raise RuntimeError('could not create unique directory')
        return identifier

    @abstractmethod
    def list_templates(self):
        """Get list of all templates in the repository.

        Returns
        -------
        list(robtmpl.template.repo.base.TemplateHandle)
        """
        raise NotImplementedError()
