"""Test benchmark result schema objects."""

import pytest

import benchtmpl.workflow.benchmark.schema as schema

import benchtmpl.workflow.parameter.declaration as pd


class TestBenchmarkResultSchema(object):
    def test_column_serialization(self):
        """Test serialization of column objects."""
        # Ensure the required default value is set properly
        col = schema.BenchmarkResultColumn(
            identifier='col_1',
            name='Column 1',
            data_type=pd.DT_INTEGER
        )
        assert col.identifier == 'col_1'
        assert col.name == 'Column 1'
        assert col.data_type == pd.DT_INTEGER
        assert col.required
        assert type(col.required) == bool
        assert not col.is_default
        assert col.is_desc()
        col = schema.BenchmarkResultColumn.from_dict(col.to_dict())
        assert col.identifier == 'col_1'
        assert col.name == 'Column 1'
        assert col.data_type == pd.DT_INTEGER
        assert col.required
        assert type(col.required) == bool
        assert not col.is_default
        assert col.is_desc()
        # Test serialization if required value is given
        col = schema.BenchmarkResultColumn(
            identifier='col_1',
            name='Column 1',
            data_type=pd.DT_INTEGER,
            required=False,
            is_default=True,
            sort_order='ASC'
        )
        assert col.identifier == 'col_1'
        assert col.name == 'Column 1'
        assert col.data_type == pd.DT_INTEGER
        assert not col.required
        assert type(col.required) == bool
        assert col.is_default
        assert not col.is_desc()
        col = schema.BenchmarkResultColumn.from_dict(col.to_dict())
        assert col.identifier == 'col_1'
        assert col.name == 'Column 1'
        assert col.data_type == pd.DT_INTEGER
        assert not col.required
        assert type(col.required) == bool
        assert col.is_default
        assert not col.is_desc()

    def test_schema_serialization(self):
        """Test creating schema objects from dictionaries and vice versa."""
        s = schema.BenchmarkResultSchema.from_dict({
            schema.LABEL_RESULT_FILE: 'results.json',
            schema.LABEL_SCHEMA: [
                schema.BenchmarkResultColumn(
                    identifier='col_1',
                    name='Column 1',
                    data_type=pd.DT_INTEGER
                ).to_dict(),
                schema.BenchmarkResultColumn(
                    identifier='col_2',
                    name='Column 2',
                    data_type=pd.DT_DECIMAL,
                    required=True
                ).to_dict(),
                schema.BenchmarkResultColumn(
                    identifier='col_3',
                    name='Column 3',
                    data_type=pd.DT_STRING,
                    required=False
                ).to_dict()
            ]
        })
        self.validate_schema(s)
        # Recreate the object from its serialization
        s = schema.BenchmarkResultSchema.from_dict(s.to_dict())
        self.validate_schema(s)
        # Error cases
        with pytest.raises(ValueError):
            doc = s.to_dict()
            doc['unknown'] = 'A'
            schema.BenchmarkResultSchema.from_dict(doc)
        with pytest.raises(ValueError):
            doc = s.to_dict()
            del doc[schema.LABEL_RESULT_FILE]
            schema.BenchmarkResultSchema.from_dict(doc)
        with pytest.raises(ValueError):
            schema.BenchmarkResultColumn(
                identifier='col_1',
                name='Column 1',
                data_type=pd.DT_LIST
            )

    def validate_column(self, column, identifier, name, data_type, required):
        """Ensure that the given column matches the respective arguments."""
        assert column.identifier == identifier
        assert column.name == name
        assert column.data_type == data_type
        assert column.required == required

    def validate_schema(self, schema):
        """Validate that the given schema."""
        assert len(schema.columns) == 3
        self.validate_column(
            column=schema.columns[0],
            identifier='col_1',
            name='Column 1',
            data_type=pd.DT_INTEGER,
            required=True
        )
        self.validate_column(
            column=schema.columns[1],
            identifier='col_2',
            name='Column 2',
            data_type=pd.DT_DECIMAL,
            required=True
        )
        self.validate_column(
            column=schema.columns[2],
            identifier='col_3',
            name='Column 3',
            data_type=pd.DT_STRING,
            required=False
        )
