# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test functionality of the abstract template repository."""

import pytest

from robtmpl.template.repo.base import TemplateRepository


class TestTemplateRepository(object):
    """Test functionality of abstract template repository."""
    def test_abstract_methods(self, tmpdir):
        """Test abstract methods for completeness."""
        repo = TemplateRepository()
        with pytest.raises(NotImplementedError):
            repo.add_template('unknown')
        with pytest.raises(NotImplementedError):
            repo.delete_template('unknown')
        with pytest.raises(NotImplementedError):
            repo.exists_template('unknown')
        with pytest.raises(NotImplementedError):
            repo.get_template('unknown')
        with pytest.raises(NotImplementedError):
            repo.list_templates()
        with pytest.raises(NotImplementedError):
            repo.get_unique_identifier()
