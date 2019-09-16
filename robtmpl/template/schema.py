# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Definition of schema components for benchmark results. The schema definition
is part of the extended workflow template specification that is used to define
benchmarks.
"""

import robtmpl.error as err
import robtmpl.util as util
import robtmpl.template.parameter.declaration as pd


"""Supported data types for result values."""
DATA_TYPES = [pd.DT_DECIMAL, pd.DT_INTEGER, pd.DT_STRING]


"""Labels for serialization."""
# Column specification
COLUMN_ID = 'id'
COLUMN_NAME = 'name'
COLUMN_REQUIRED = 'required'
COLUMN_TYPE = 'type'
# Leader board default sort order
SORT_ID = COLUMN_ID
SORT_DESC = 'sortDesc'
# Schema specification
SCHEMA_RESULTFILE = 'file'
SCHEMA_COLUMNS = 'schema'
SCHEMA_ORDERBY = 'orderBy'


class ResultColumn(object):
    """Column in the result schema of a benchmark. Each column has a unique
    identifier and unique name. The identifier is used as column name in the
    database schema. The name is for display purposes in a user interface.
    """
    def __init__(self, identifier, name, data_type, required=None):
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

        Raises
        ------
        robtmpl.error.InvalidTemplateError
        """
        # Raise error if the data type value is not in the list of supported
        # data types
        if not data_type in DATA_TYPES:
            raise err.InvalidTemplateError('unknown data type \'{}\''.format(data_type))
        self.identifier = identifier
        self.name = name
        self.data_type = data_type
        self.required = required if not required is None else True

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
        robtmpl.template.schema.ResultColumn

        Raises
        ------
        robtmpl.error.InvalidTemplateError
        """
        # Validate the serialization dictionary
        try:
            util.validate_doc(
                doc,
                mandatory_labels=[COLUMN_ID, COLUMN_NAME, COLUMN_TYPE],
                optional_labels=[COLUMN_REQUIRED]
            )
        except ValueError as ex:
            raise err.InvalidTemplateError(str(ex))
        # Return instance of the column object
        return ResultColumn(
            identifier=doc[COLUMN_ID],
            name=doc[COLUMN_NAME],
            data_type=doc[COLUMN_TYPE],
            required=doc.get(COLUMN_REQUIRED)
        )

    def to_dict(self):
        """Get dictionary serialization for the column object.

        Returns
        -------
        dict
        """
        return {
            COLUMN_ID: self.identifier,
            COLUMN_NAME: self.name,
            COLUMN_TYPE: self.data_type,
            COLUMN_REQUIRED: self.required
        }


class ResultSchema(object):
    """The result schema of a benchmark run is a collection of columns. The
    result schema is used to generate leader boards for benchmarks.

    The schema also contains the identifier of the output file that contains the
    result object. The result object that is generated by each benchmark  run is
    expected to contain a value for each required columns in the schema.
    """
    def __init__(self, result_file_id, columns, order_by=None):
        """Initialize the result file identifier, schema columns, and the
        default sort order.

        Parameters
        ----------
        result_file_id: string
            Identifier of the benchmark run result file that contains the
            analytics results.
        columns: list(robtmpl.template.schema.ResultColumn)
            List of columns in the result object
        order_by: list(robtmpl.template.schema.SortColumn)
            List of columns that define the default sort order for entries in
            the leader board.
        """
        self.result_file_id = result_file_id
        self.columns = columns
        self.order_by = order_by if not order_by is None else list()

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
        robtmpl.template.schema.ResultSchema

        Raises
        ------
        robtmpl.error.InvalidTemplateError
        """
        # Validate the serialization dictionary
        try:
            util.validate_doc(
                doc,
                mandatory_labels=[SCHEMA_RESULTFILE, SCHEMA_COLUMNS],
                optional_labels=[SCHEMA_ORDERBY]
            )
        except ValueError as ex:
            raise err.InvalidTemplateError(str(ex))
        # Identifier of the output file that contains the result object
        file_id = doc[SCHEMA_RESULTFILE]
        # Get column list. Ensure that all column names and identifier are
        # unique
        columns=[ResultColumn.from_dict(c) for c in doc[SCHEMA_COLUMNS]]
        ids = set()
        names = set()
        for col in columns:
            if col.identifier in ids:
                msg = 'duplicate column identifier \'{}\''
                raise err.InvalidTemplateError(msg.format(col.identifier))
            ids.add(col.identifier)
            if col.name in names:
                msg = 'not unique column name \'{}\''
                raise err.InvalidTemplateError(msg.format(col.name))
            names.add(col.name)
        # Get optional default sort statement for the ranking
        order_by = list()
        if SCHEMA_ORDERBY in doc:
            # Ensure that the column identifier reference columns in the schema
            for c in doc[SCHEMA_ORDERBY]:
                col = SortColumn.from_dict(c)
                if not col.identifier in ids:
                    msg = 'unknown column \'{}\''
                    raise err.InvalidTemplateError(msg.format(col.identifier))
                order_by.append(col)
        # Return benchmark schema object
        return ResultSchema(
            result_file_id=file_id,
            columns=columns,
            order_by=order_by
        )

    def to_dict(self):
        """Get dictionary serialization for the result schema object.

        Returns
        -------
        dict
        """
        return {
            SCHEMA_RESULTFILE: self.result_file_id,
            SCHEMA_COLUMNS: [col.to_dict() for col in self.columns],
            SCHEMA_ORDERBY: [col.to_dict() for col in self.order_by]
        }


class SortColumn(object):
    """The sort column defines part of an ORDER BY statement that is used to
    sort benchmark results when creating the benchmark leader board. Each object
    contains a reference to a result column and a flag indicating the sort
    order for values in the column.
    """
    def __init__(self, identifier, sort_desc=None):
        """Initialize the object properties.

        Parameters
        ----------
        identifier: string
            Unique column identifier
        sort_desc: bool, optional
            Sort values in descending order if True or in ascending order
            otherwise
        """
        self.identifier = identifier
        self.sort_desc = sort_desc if not sort_desc is None else True

    @staticmethod
    def from_dict(doc):
        """Get an instance of the sort column from the dictionary serialization.
        Raises an error if the given dictionary does not contain the expected
        elements as generated by the to_dict() method of the class.

        Parameters
        ----------
        doc: dict
            Dictionary serialization of a column object

        Returns
        -------
        robtmpl.template.schema.SortColumn

        Raises
        ------
        robtmpl.error.InvalidTemplateError
        """
        # Validate the serialization dictionary
        try:
            util.validate_doc(
                doc,
                mandatory_labels=[SORT_ID],
                optional_labels=[SORT_DESC]
            )
        except ValueError as ex:
            raise err.InvalidTemplateError(str(ex))
        sort_desc = None
        if SORT_DESC in doc:
            sort_desc = doc[SORT_DESC]
        # Return instance of the column object
        return SortColumn(identifier=doc[SORT_ID], sort_desc=sort_desc)

    def to_dict(self):
        """Get dictionary serialization for the sort column object.

        Returns
        -------
        dict
        """
        return {SORT_ID: self.identifier, SORT_DESC: self.sort_desc}
