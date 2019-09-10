# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""The file system implementation of the template repository maintains
information about templates and their static files on the file system as well
as in a relational database.
"""

import git
import os
import shutil

from robtmpl.core.db.driver import DatabaseDriver
from robtmpl.template.repo.base import TemplateRepository
from robtmpl.template.base import TemplateHandle, WorkflowTemplate
from robtmpl.core.io.store.json import JsonFileStore

import robtmpl.core.error as err
import robtmpl.core.util as util
import robtmpl.template.repo.base as base


"""Names for files and folders that are used to maintain template information."""
STATIC_FILES_DIR = 'static'
TEMPLATE_FILE = 'template.json'


class TemplateFSRepository(TemplateRepository):
    """This repository maintains templates on the file system. It also uses a
    relational database to store template information like the template name
    and user instructions.
    """
    def __init__(
        self, base_dir, con=None, store=None, default_filenames=None,
        id_func=None, max_attempts=base.DEFAULT_MAX_ATTEMPTS
    ):
        """Initialize the database connection and the template store.

        Parameters
        ----------
        base_dir: string
            Base directory for the repository
        con: DB-API 2.0 database connection
            Connection to underlying database
        store: robtmpl.core.io.store.base.TemplateStore, optional
            Store for workflow templates
        default_filenames: list(string), optional
            List of default names for template specification files
        id_func: func, optional
            Function to generate template folder identifier
        max_attempts: int, optional
            Maximum number of attempts to create a unique folder for a new
            workflow template
        """
        super(TemplateFSRepository, self).__init__(
            id_func=id_func,
            max_attempts=max_attempts
        )
        # Set the base directory and ensure that it exists
        self.base_dir = util.create_dir(base_dir)
        # Get connection using the environment configuration if no connection
        # is given
        if not con is None:
            self.con = con
        else:
            self.con = DatabaseDriver.get_connector().connect()
        # Initialize the template store
        if not store is None:
            self.store = store
        else:
            self.store = JsonFileStore(
                base_dir=self.base_dir,
                default_file_name=TEMPLATE_FILE
            )
        # Initialize the list of default termplate specification file names
        if not default_filenames is None:
            self.default_filenames = default_filenames
        else:
            self.default_filenames = list()
            for name in ['benchmark', 'template', 'workflow']:
                for suffix in ['.yml', '.yaml', '.json']:
                    self.default_filenames.append(name + suffix)

    def add_template(
        self, name, description=None, instructions=None, src_dir=None,
        src_repo_url=None, template_spec_file=None
    ):
        """Add a template to the repository. The associated workflow template
        is created in the template repository from either the given source
        directory or Git repository. The template repository will raise an
        error if neither or both arguments are given.

        Creates a new folder with unique name in the base directory of the
        template store. The created folder will contain a copy of the source
        folder or the git repository.

        The source folder is expected to contain the template specification
        file. If the template_spec file is not given the method will look for a
        file using the entries in the list of default file names. If no template
        file is found in the source folder a ValueError is raised.

        The contents of the source directory will be copied to the new template
        directory (as subfolder named 'static').

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
        robtmpl.template.base.TemplateHandle

        Raises
        ------
        robtmpl.core.error.ROBError
        robtmpl.core.error.InvalidTemplateError
        ValueError
        """
        # Exactly one of src_dir and src_repo_url has to be not None. If both
        # are None (or not None) a ValueError is raised.
        if src_dir is None and src_repo_url is None:
            raise ValueError('both \'src_dir\' and \'src_repo_url\' are missing')
        elif not src_dir is None and not src_repo_url is None:
            raise ValueError('cannot have both \'src_dir\' and \'src_repo_url\'')
        # Ensure that the template name is not empty, not longer than 255
        # character and unique.
        if name is None:
            raise err.ROBError('missing template name')
        name = name.strip()
        if name == '' or len(name) > 255:
            raise err.ROBError('invalid template name')
        sql = 'SELECT id FROM template WHERE name = ?'
        if not self.con.execute(sql, (name,)).fetchone() is None:
            raise err.ROBError('template exists')
        # Get unique identifier and create a new folder for the template files
        # and resources
        identifier = self.get_unique_identifier()
        template_dir = util.create_dir(os.path.join(self.base_dir, identifier))
        # Copy either the given workflow directory into the created template
        # folder or clone the Git repository.
        try:
            static_dir = os.path.join(template_dir, STATIC_FILES_DIR)
            if not src_dir is None:
                shutil.copytree(src=src_dir, dst=static_dir)
            else:
                git.Repo.clone_from(src_repo_url, static_dir)
        except (IOError, OSError, git.exc.GitCommandError) as ex:
            # Make sure to cleanup by removing the created template folder
            shutil.rmtree(template_dir)
            raise ex
        # Find template specification file in the template workflow folder.
        # If the file is not found the template directory is removed and a
        # ValueError is raised.
        template = None
        candidates = list()
        for filename in self.default_filenames:
            candidates.append(os.path.join(static_dir, filename))
        if not template_spec_file is None:
            candidates = [template_spec_file] + candidates
        for filename in candidates:
            if os.path.isfile(filename):
                # Read template from file. If no error occurs the folder
                # contains a valid template.
                template = WorkflowTemplate.from_dict(
                    doc=util.read_object(filename),
                    identifier=identifier,
                    validate=True
                )
                # Store serialized template handle on disk
                self.store.write(
                    identifier=template.identifier,
                    obj=template.to_dict()
                )
                break
        # No template file found. Cleanup and raise error.
        if template is None:
            shutil.rmtree(template_dir)
            raise err.InvalidTemplateError('no template file found')
        # Insert template into database and return descriptor
        sql = 'INSERT INTO template'
        sql += '(id, name, description, instructions) '
        sql += 'VALUES(?, ?, ?, ?)'
        self.con.execute(sql, (identifier, name, description, instructions))
        # Commit all changes to the database
        self.con.commit()
        # Return the template handle
        return TemplateHandle(
            template=template,
            name=name,
            description=description,
            instructions=instructions
        )

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
        # Delete the template record. The number of deleted rows is used the
        # generate the return value.
        sql = 'DELETE FROM template WHERE id = ?'
        cur = self.con.cursor()
        cur.execute(sql, (identifier,))
        result = cur.rowcount > 0
        self.con.commit()
        # Remove the template directory if it exists
        template_dir = os.path.join(self.base_dir, identifier)
        if os.path.isdir(template_dir):
            shutil.rmtree(template_dir)
        return result

    def exists_template(self, identifier):
        """Test if a template with the given identifier exists.

        Returns
        -------
        bool
        """
        # Query the database to see if a template with the given identifier
        # exists
        sql = 'SELECT id FROM template WHERE id = ?'
        return not self.con.execute(sql, (identifier,)).fetchone() is None

    def get_static_dir(self, identifier):
        """Get path to directory containing static files for the template with
        the given identifier.

        Returns
        -------
        string
        """
        template_dir = os.path.join(self.base_dir, identifier)
        return os.path.join(template_dir, STATIC_FILES_DIR)

    def get_template(self, identifier):
        """Get handle for the template with the given identifier.

        Parameters
        ----------
        identifier: string
            Unique template identifier

        Returns
        -------
        robtmpl.template.base.TemplateHandle

        Raises
        ------
        robtmpl.core.error.UnknownTemplateError
        """
        # Get template information from database. If the result is empty an
        # error is raised
        sql = 'SELECT id, name, description, instructions '
        sql += 'FROM template '
        sql += 'WHERE id = ?'
        rs = self.con.execute(sql, (identifier,)).fetchone()
        if rs is None:
            raise err.UnknownTemplateError(identifier)
        # Get workflow template for template repository
        template = WorkflowTemplate.from_dict(self.store.read(identifier))
        # Return handle for template
        return TemplateHandle(
            template=template,
            name=rs['name'],
            description=rs['description'],
            instructions=rs['instructions']
        )

    def list_templates(self):
        """Get list of all templates in the repository.

        Returns
        -------
        list(robtmpl.template.base.TemplateHandle)
        """
        sql = 'SELECT id, name, description, instructions '
        sql += 'FROM template '
        rs = self.con.execute(sql)
        result = list()
        for bmark in rs:
            result.append(
                TemplateHandle(
                    template=WorkflowTemplate.from_dict(
                        self.store.read(bmark['id'])
                    ),
                    name=bmark['name'],
                    description=bmark['description'],
                    instructions=bmark['instructions']
                )
            )
        return result
