"""Test basic token scanner functionality to collect template parameter values
from standard input.
"""

import pytest

from benchtmpl.io.scanner import Scanner, ListReader
from benchtmpl.workflow.parameter.base import TemplateParameter

import benchtmpl.workflow.parameter.declaration as pd


class TestScanner(object):
    def test_propmpt(self):
        """Test generated prompts when reading parameter values from standard
        input.
        """
        # BOOL
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_BOOL
        ))).prompt()
        assert p == 'ABC (bool): '
        # FILE
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_FILE
        ))).prompt()
        assert p == 'ABC (file): '
        # FLOAT
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_DECIMAL
        ))).prompt()
        assert p == 'ABC (decimal): '
        # INTEGER
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_INTEGER
        ))).prompt()
        assert p == 'ABC (integer): '
        # STRING
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_STRING
        ))).prompt()
        assert p == 'ABC (string): '
        # Default values in prompts
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_INTEGER,
            default_value=100
        ))).prompt()
        assert p == 'ABC (integer) [default 100]: '
        p = TemplateParameter(pd.set_defaults(pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_STRING,
            default_value=100
        ))).prompt()
        assert p == 'ABC (string) [default \'100\']: '

    def test_scan_default_values(self):
        """Test return of default values when reading empty input."""
        sc = Scanner(reader=ListReader(5 * ['']))
        assert sc.next_int(default_value=11) == 11
        assert sc.next_float(default_value=1.23) == 1.23
        #self.assertFalse(sc.next_bool(default_value=False))
        assert not sc.next_bool(default_value=False)
        assert sc.next_file(default_value='file.txt') == 'file.txt'
        assert sc.next_string(default_value='Default text') == 'Default text'

    def test_scan_scalar_values(self):
        """Test parsing of scalar tokens."""
        sc = Scanner(reader=ListReader(['3', '34.56', 'FALSE', 'y', 'data/names.txt', 'Some text']))
        assert sc.next_int() == 3
        assert sc.next_float() == 34.56
        assert not sc.next_bool()
        assert sc.next_bool()
        assert sc.next_file() == 'data/names.txt'
        assert sc.next_string() == 'Some text'
        # Value errors when parsing invalid tokens
        sc = Scanner(reader=ListReader(['3', 'FALSE', 'data/names.txt']))
        with pytest.raises(ValueError):
            sc.next_bool()
        with pytest.raises(ValueError):
            sc.next_int()
        with pytest.raises(ValueError):
            sc.next_float()
