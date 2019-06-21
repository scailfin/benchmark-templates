# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Definition of schema components for benchmark result schemas. The schema
definition is part of the extended workflow template specification that is used
to define benchmarks.
"""

import benchtmpl.workflow.parameter.declaration as pd

"""Supported data types for result values."""
DATA_TYPES = [pd.DT_DECIMAL, pd.DT_INTEGER, pd.DT_STRING]


"""Labels for serialization."""
LABEL_ID = 'id'
LABEL_IS_DEFAULT = 'isDefault'
LABEL_NAME = 'name'
LABEL_RESULT_FILE = 'file'
LABEL_REQUIRED = 'required'
LABEL_SCHEMA = 'schema'
LABEL_SORT_ORDER = 'sortOrder'
LABEL_TYPE = 'type'

COLUMN_LABELS = [LABEL_ID, LABEL_NAME, LABEL_TYPE]
SCHEMA_LABELS = [LABEL_RESULT_FILE, LABEL_SCHEMA]


"""Column sort orders."""
SORT_ASC = 'ASC'
SORT_DESC = 'DESC'

class BenchmarkResultColumn(object):
    """Column in the result schema of a benchmark. Each column has a unique
    identifier and unique name. The identifier is used as column name in the
    database schema. the name is for display purposes in the user interface.
    """
    def __init__(self, identifier, name, data_type, required=None, is_default=None, sort_order=None):
        """Initialize the unique column identifier, name, and the data type. If
        the value of data_type is not in the list of supported data types an
        error is raised.

        Parameters
        ----------
        identifier: string
            Unique column identifier
        name: string
            Unique column name
        data_type: string
            Data type identifier
        required: bool, optional
            Indicates whether a value is expected for this column in every
            benchmark run result
        is_default: bool, optional
            Indicates whether this column is the default csort column for the
            benchmark leaderboard
        sort_order: string, optional
            Sort order for this column when generating the leaderboard
        """
        # Raise error if the data type value is not in the list of supported
        # data types
        if not data_type in DATA_TYPES:
            raise ValueError('unknown data type \'{}\''.format(data_type))
        self.identifier = identifier
        self.name = name
        self.data_type = data_type
        self.required = required if not required is None else True
        self.is_default = is_default if not is_default is None else False
        self.sort_order = sort_order if not sort_order is None else SORT_DESC

    @staticmethod
    def from_dict(doc):
        """Get an instance of the column from the dictionary serialization.
        Raises an error if the given dictionary does not contain the expected
        elements as generated by the to_dict() method of the class.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a column object

        Returns
        -------
        benchtmpl.workflow.benchmark.schema.BenchmarkResultColumn

        Raises
        ------
        ValueError
        """
        # Validate the serialization dictionary
        validate_doc(
            doc,
            COLUMN_LABELS,
            optional_labels=[LABEL_REQUIRED, LABEL_IS_DEFAULT, LABEL_SORT_ORDER]
        )
        # Return instance of the column object
        return BenchmarkResultColumn(
            identifier=doc[LABEL_ID],
            name=doc[LABEL_NAME],
            data_type=doc[LABEL_TYPE],
            required=doc.get(LABEL_REQUIRED),
            is_default=doc.get(LABEL_IS_DEFAULT),
            sort_order=doc.get(LABEL_SORT_ORDER)
        )

    def is_desc(self):
        """True if the values in this columns are sorted in descending order
        when generating the leaderboard.

        Returns
        -------
        bool
        """
        return self.sort_order == SORT_DESC

    def sort_statement(self):
        """Get column identifier and the optional sort order statement depending
        on the current value for the sort order attribute. The result is to be
        used when generating SQL queries that fetch benchmark results.

        Returns
        -------
        string
        """
        if self.is_desc():
            return self.identifier + ' DESC'
        else:
            return self.identifier

    def sql_stmt(self):
        """SQL statement for column in create table statement.

        Returns
        -------
        string
        """
        stmt = self.identifier
        if self.data_type == pd.DT_INTEGER:
            stmt += ' INTEGER'
        elif self.data_type == pd.DT_DECIMAL:
            stmt += ' DOUBLE'
        else:
            stmt += ' TEXT'
        if self.required:
            stmt += ' NOT NULL'
        return stmt

    def to_dict(self):
        """Get dictionary serialization for the column object.

        Returns
        -------
        dict
        """
        return {
            LABEL_ID: self.identifier,
            LABEL_NAME: self.name,
            LABEL_TYPE: self.data_type,
            LABEL_REQUIRED: self.required,
            LABEL_IS_DEFAULT: self.is_default,
            LABEL_SORT_ORDER: self.sort_order
        }


class BenchmarkResultSchema(object):
    """The result schema of a benchmark run is a collection of columns. The
    result object of the run is expected to contain a value for each required
    column and at most for all columns. The schema also contains the identifier
    of the output file that contains the result object.
    """
    def __init__(self, columns, result_file_id):
        """Initialize the schema columns and the result file identifier.

        Parameters
        ----------
        columns: list(benchtmpl.workflow.benchmark.schema.BenchmarkResultColumn)
            List of columns in the result object
        result_file_id: string
            Identifier of the benchmark run result file that contains the
            analytics results.
        """
        self.columns = columns
        self.result_file_id = result_file_id

    @staticmethod
    def from_dict(doc):
        """Get an instance of the schema from a dictionary serialization.
        Raises an error if the given dictionary does not contain the expected
        elements as generated by the to_dict() method of the class or if the
        names or identifier of columns are not unique.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a benchmark result schema object

        Returns
        -------
        benchtmpl.workflow.benchmark.schema.BenchmarkResultSchema

        Raises
        ------
        ValueError
        """
        # Validate the serialization dictionary
        validate_doc(doc, SCHEMA_LABELS)
        # Get column list. Ensure that all column names and identifier are
        # unique
        columns=[BenchmarkResultColumn.from_dict(c) for c in doc[LABEL_SCHEMA]]
        ids = set()
        names = set()
        for col in columns:
            if col.identifier in ids:
                raise ValueError('duplicate column identifier \'{}\''.format(col.identifier))
            ids.add(col.identifier)
            if col.name in names:
                raise ValueError('not unique column name \'{}\''.format(col.name))
            names.add(col.name)
        file_id = doc[LABEL_RESULT_FILE]
        # Return instance of the column object
        return BenchmarkResultSchema(columns=columns, result_file_id=file_id)

    def to_dict(self):
        """Get dictionary serialization for the result schema object.

        Returns
        -------
        dict
        """
        return {
            LABEL_RESULT_FILE: self.result_file_id,
            LABEL_SCHEMA: [col.to_dict() for col in self.columns]
        }


# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def validate_doc(doc, mandatory_labels, optional_labels=[]):
    """Raises error if the dictionary contains labels that are not in the given
    label lists or if there are labels in the mandatory list that are not in the
    dictionary.

    Paramaters
    ----------
    doc: dict
        Dictionary serialization of an object
    mandatory_labels: list(string)
        List of mandatory labels for the dictionary serialization
    optional_labels: list(string), optional
        List of optional labels for the dictionary serialization

    Raises
    ------
    ValueError
    """
    # Ensure that all mandatory labels are present in the dictionary
    for key in mandatory_labels:
        if not key in doc:
            raise ValueError('missing element \'{}\''.format(key))
    # Raise error if additional elements are present in the dictionary
    labels = mandatory_labels + optional_labels
    for key in doc:
        if not key in labels:
            raise ValueError('unknown element \'{}\''.format(key))
