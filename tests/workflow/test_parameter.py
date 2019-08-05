"""Test validation of template parameter declarations."""

import pytest

from benchtmpl.workflow.parameter.base import TemplateParameter

import benchtmpl.error as err
import benchtmpl.workflow.parameter.declaration as pd


class TestParameterValidation(object):
    def test_invalid_datatype(self):
        """Assert that an error is raised if a package declaration with an
        invalid data type is given.
        """
        # Ensure that it works with a valid data type
        p = pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_RECORD
        )
        with pytest.raises(err.InvalidParameterError):
            p = pd.parameter_declaration(identifier='ABC', data_type='XYZ')
        # Specifying a non-string value should also raise an error
        with pytest.raises(err.InvalidParameterError):
            pd.parameter_declaration(identifier='ABC', data_type=123)
        # Ensure that validation fails if data type is manipulated
        p = pd.parameter_declaration(
            identifier='ABC',
            data_type=pd.DT_RECORD
        )
        pd.validate_parameter(p)
        p[pd.LABEL_DATATYPE] = 'Something unknown'
        with pytest.raises(err.InvalidParameterError):
            pd.validate_parameter(p)

    def test_invalid_identifier(self):
        """Assert that an error is raised if a package declaration with an
        invalid identifier is given.
        """
        # Ensure that it works with a valid identifier
        pd.parameter_declaration(identifier='ABC', data_type=pd.DT_BOOL)
        # Error is raised if identifier is None
        with pytest.raises(err.InvalidParameterError):
            pd.parameter_declaration(identifier=None, data_type=pd.DT_BOOL)

    def test_maximal_declaration(self):
        """Test parameter declarations that provide values for all arguments.
        """
        # Set all parameter elements to values that are different from their
        # default value
        p = pd.parameter_declaration(
            identifier='ABC',
            name='XYZ',
            description='ABC to XYZ',
            data_type=pd.DT_INTEGER,
            index=10,
            required=False,
            values=[
                pd.enum_value(value=1),
                pd.enum_value(value=2, text='Two'),
                pd.enum_value(value=3, text='THREE', is_default=True)
            ],
            parent='DEF',
            default_value=5,
            as_const='data/names.txt'
        )
        assert isinstance(p, dict)
        assert p.get(pd.LABEL_ID) == 'ABC'
        assert p.get(pd.LABEL_NAME) == 'XYZ'
        assert p.get(pd.LABEL_DESCRIPTION) == 'ABC to XYZ'
        assert p.get(pd.LABEL_DATATYPE) == pd.DT_INTEGER
        assert p.get(pd.LABEL_INDEX) == 10
        assert not p.get(pd.LABEL_REQUIRED)
        assert p.get(pd.LABEL_PARENT) == 'DEF'
        assert p.get(pd.LABEL_DEFAULT) == 5
        assert p.get(pd.LABEL_AS) == 'data/names.txt'
        # Valudate value enumeration
        values = p.get(pd.LABEL_VALUES, [])
        assert len(values) == 3
        self.validate_value(values[0], 1, '1', False)
        self.validate_value(values[1], 2, 'Two', False)
        self.validate_value(values[2], 3, 'THREE', True)
        # Ensure that the returned dictionary is valid with respect to the
        # parameter schema declaration.
        pd.validate_parameter(p)

    def test_minimal_declaration(self):
        """Test parameter declarations that only provide the required arguments.
        """
        # Expect to get a dictionary that contains the identifier, name (both
        # equal to 'ABC'), a data type DT_STRING, an index of 0. The required
        #  flag is True.
        p = pd.parameter_declaration(identifier='ABC')
        assert isinstance(p, dict)
        assert p.get(pd.LABEL_ID) == 'ABC'
        assert p.get(pd.LABEL_NAME) == 'ABC'
        assert p.get(pd.LABEL_DESCRIPTION) == 'ABC'
        assert p.get(pd.LABEL_DATATYPE) == pd.DT_STRING
        assert p.get(pd.LABEL_INDEX) == 0
        assert p.get(pd.LABEL_REQUIRED)
        # All other optional elements of the declaration are missing
        assert pd.LABEL_DEFAULT not in p
        assert pd.LABEL_PARENT not in p
        assert pd.LABEL_VALUES not in p
        # Ensure that the returned dictionary is valid with respect to the
        # parameter schema declaration.
        pd.validate_parameter(p)

    def test_parameter_declaration(self):
        """Test methods of the parameter declaration object."""
        obj = pd.set_defaults(pd.parameter_declaration(identifier='ABC'))
        obj[pd.LABEL_AS] = 'XYZ'
        p = TemplateParameter(obj)
        # Type flags
        assert not p.is_bool()
        assert not p.is_file()
        assert not p.is_float()
        assert not p.is_int()
        assert not p.is_list()
        assert not p.is_record()
        assert p.is_string()
        # Constant values
        assert p.has_constant()
        assert p.get_constant() == 'XYZ'
        # Error for invalid data type
        with pytest.raises(err.InvalidParameterError):
            TemplateParameter({pd.LABEL_ID: 'A', pd.LABEL_DATATYPE: 'XYZ'})

    def test_set_defaults(self):
        """Test the set defaults method with minimal input."""
        p = pd.set_defaults({pd.LABEL_ID: 'My ID'})
        assert p.get(pd.LABEL_ID) == 'My ID'
        assert p.get(pd.LABEL_NAME) == 'My ID'
        assert p.get(pd.LABEL_DESCRIPTION) == 'My ID'
        assert p.get(pd.LABEL_DATATYPE) == pd.DT_STRING
        assert p.get(pd.LABEL_INDEX) == 0
        assert p.get(pd.LABEL_REQUIRED)


    def test_validate_error(self):
        """Assert that errors are raised if an invalid parameter declaration is
        given to the validate_parameter function.
        """
        p = pd.parameter_declaration(identifier='ABC')
        # Ensure that creating a dictionary from a valid parameter declaration
        # is still valid
        pd.validate_parameter(dict(p))
        # Invalid data type for parameter identifier
        p_invalid = dict(p)
        p_invalid[pd.LABEL_ID] = 123
        with pytest.raises(err.InvalidParameterError):
            pd.validate_parameter(p_invalid)
        # Invalid data type for parameter name
        p_invalid = dict(p)
        p_invalid[pd.LABEL_NAME] = 123
        with pytest.raises(err.InvalidParameterError):
            pd.validate_parameter(p_invalid)
        # Invalid data type for parameter data type
        p_invalid = dict(p)
        p_invalid[pd.LABEL_DATATYPE] = 12.3
        with pytest.raises(err.InvalidParameterError):
            pd.validate_parameter(p_invalid)
        # Invalid data type for parameter index
        p_invalid = dict(p)
        p_invalid[pd.LABEL_INDEX] = '12'
        with pytest.raises(err.InvalidParameterError):
            pd.validate_parameter(p_invalid)
        # Invalid data type for parameter required
        p_invalid = dict(p)
        p_invalid[pd.LABEL_REQUIRED] = '12'
        with pytest.raises(err.InvalidParameterError):
            pd.validate_parameter(p_invalid)

    def validate_value(self, obj, value, name, is_default):
        """Validate element in a parameter value enumeration."""
        assert obj[pd.LABEL_VALUE] == value
        assert obj[pd.LABEL_NAME] == name
        assert obj[pd.LABEL_IS_DEFAULT] == is_default
